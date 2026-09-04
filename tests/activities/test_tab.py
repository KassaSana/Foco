"""Exercise the editor against real storage without starting a desktop window."""

import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from foco.activities.tab import ActivitiesTab
from foco.storage import DataLogger


class ActivityTable:
    def __init__(self):
        self.rows = {}
        self.next_id = 0

    def insert(self, parent, position, values):
        self.next_id += 1
        item_id = str(self.next_id)
        self.rows[item_id] = list(values)
        return item_id

    def get_children(self):
        return list(self.rows)

    def delete(self, *items):
        for item_id in items:
            del self.rows[item_id]

    def item(self, item_id, values=None):
        if values is not None:
            self.rows[item_id] = list(values)
        return {'values': self.rows[item_id]}


class TestActivityEditor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.logger = DataLogger(self.temp_dir.name, lambda: datetime(2026, 9, 2, 10))
        self.tab = ActivitiesTab()
        self.tab.data_logger = self.logger
        self.tab.activities_tree = ActivityTable()
        self.tab.activity_edit_status = Mock()
        self.tab._editing_activity = None
        self.tab._activities_dirty = False
        self.tab._refresh_activities()

    def seed(self, count=1):
        for number in range(count):
            self.logger.start_session({
                'application': 'chrome.exe', 'window_title': f'Reddit {number}',
                'category': 'Knowledge', 'is_pseudo_productive': True,
                'start_time': '09:00:00', 'custom_metadata': 'preserve me',
            })
            self.logger.end_session({'duration_minutes': 1, 'end_time': '09:01:00'})
        self.tab._refresh_activities()

    def edit(self, row, column, value):
        values = list(self.tab.activities_tree.item(row)['values'])
        values[column] = value
        self.tab.activities_tree.item(row, values=values)
        self.tab._mark_activities_dirty()

    def test_edit_preserves_all_sixty_rows_and_original_metadata(self):
        self.seed(60)
        self.assertEqual(len(self.tab.activities_tree.get_children()), 60)
        original = self.logger.get_day_data()['sessions']
        row = self.tab.activities_tree.get_children()[0]
        self.edit(row, 2, 'Corrected label')
        self.tab._save_activities()

        saved = self.logger.get_day_data()['sessions']
        self.assertEqual(len(saved), 60)
        self.assertEqual(saved[1:], original[1:])
        self.assertEqual(saved[0], dict(original[0], activity='Corrected label'))
        self.assertEqual(self.logger.get_today_summary()['pseudo_productive'], 60)
        self.assertEqual(self.logger.get_today_summary()['total_productive'], 0)
        reloaded = DataLogger(self.temp_dir.name, self.logger.now_provider)
        self.assertEqual(reloaded.get_day_data()['sessions'], saved)

    def test_category_correction_explicitly_removes_pseudo_flag(self):
        self.seed()
        row = self.tab.activities_tree.get_children()[0]
        self.assertEqual(self.tab.activities_tree.item(row)['values'][3], 'Pseudo_productive')
        self.edit(row, 3, 'Studying')
        self.tab._save_activities()
        self.assertEqual(self.logger.get_today_summary()['pseudo_productive'], 0)
        self.assertEqual(self.logger.get_today_summary()['studying'], 1)

    def test_refresh_keeps_unsaved_changes_and_save_keeps_new_tracking(self):
        self.seed()
        row = self.tab.activities_tree.get_children()[0]
        self.edit(row, 2, 'Draft')
        self.logger.start_session({'application': 'code.exe', 'category': 'Building'})
        self.logger.end_session({'duration_minutes': 5})
        self.tab._refresh_activities()
        self.assertEqual(self.tab.activities_tree.item(row)['values'][2], 'Draft')
        self.tab._save_activities()
        self.assertEqual(len(self.logger.get_day_data()['sessions']), 2)
        self.assertEqual(len(self.tab.activities_tree.get_children()), 2)

    def test_cancel_discards_draft_without_changing_history(self):
        self.seed()
        original = self.logger.get_day_data()
        self.tab._add_activity()
        with patch('foco.activities.tab.messagebox.askyesno', return_value=True):
            self.tab._cancel_activity_edits()
        self.assertFalse(self.tab._activities_dirty)
        self.assertEqual(len(self.tab.activities_tree.get_children()), 1)
        self.assertEqual(self.logger.get_day_data(), original)

    def test_add_and_delete_are_saved_without_touching_other_records(self):
        self.seed(2)
        original = self.logger.get_day_data()['sessions']
        first = self.tab.activities_tree.get_children()[0]
        self.tab.activities_tree.selection = lambda: [first]
        self.tab._delete_activity()
        self.tab._add_activity()
        added = self.tab.activities_tree.get_children()[-1]
        self.edit(added, 2, 'Offline study')
        self.edit(added, 3, 'Studying')
        self.edit(added, 4, '20')
        self.tab._save_activities()
        saved = self.logger.get_day_data()['sessions']
        self.assertEqual(len(saved), 2)
        self.assertEqual(saved[0], original[1])
        self.assertEqual(saved[1]['source'], 'manual')
        self.assertEqual(saved[1]['category'], 'Studying')
        self.assertEqual(self.logger.get_today_summary()['studying'], 20)

    def test_save_finishes_active_cell_once(self):
        self.seed()
        row = self.tab.activities_tree.get_children()[0]
        entry = Mock()
        entry.get.return_value = 'Final label'
        entry.destroy.side_effect = self.tab._finish_activity_edit
        self.tab._editing_activity = (row, 2, entry)
        self.tab._save_activities()
        entry.destroy.assert_called_once()
        self.assertEqual(self.logger.get_day_data()['sessions'][0]['activity'], 'Final label')

    def test_failed_save_keeps_draft_available(self):
        self.seed()
        row = self.tab.activities_tree.get_children()[0]
        self.edit(row, 2, 'Draft')
        with patch.object(self.logger, 'save_today_data', return_value=False), \
                patch('foco.activities.tab.messagebox.showerror') as error:
            self.tab._save_activities()
        error.assert_called_once()
        self.assertTrue(self.tab._activities_dirty)
        self.assertEqual(self.tab.activities_tree.item(row)['values'][2], 'Draft')
        self.assertNotIn('activity', self.logger.get_day_data()['sessions'][0])

    def test_invalid_duration_does_not_replace_history(self):
        self.seed()
        original = self.logger.get_day_data()
        row = self.tab.activities_tree.get_children()[0]
        for duration in ('-1', 'nan', 'inf', 'invalid'):
            with self.subTest(duration=duration):
                self.edit(row, 4, duration)
                with patch('foco.activities.tab.messagebox.showerror') as error:
                    self.tab._save_activities()
                error.assert_called_once()
                self.assertEqual(self.logger.get_day_data(), original)


if __name__ == '__main__':
    unittest.main()
