"""
Stats Calculator - Historical summaries and analytics
Generates daily/weekly/monthly/yearly summaries and insights
"""
from datetime import datetime

class StatsCalculator:
    def __init__(self, data_logger):
        self.data_logger = data_logger
    
    def calculate_daily_stats(self, date_str=None):
        """Calculate stats for a specific day"""
        day_data = self.data_logger.get_day_data(date_str)
        result = day_data['daily_summary'].copy()
        result['metrics'] = self.calculate_productivity_metrics([day_data])
        return result

    def calculate_productivity_metrics(self, day_records):
        """Calculate behavior and focus metrics for any collection of days."""
        productive_minutes = 0
        pseudo_minutes = 0
        productive_blocks = []
        focus_sessions = []
        context_switches = 0

        for day in day_records:
            summary = day.get('daily_summary', {})
            productive_minutes += float(summary.get('total_productive', 0) or 0)
            pseudo_minutes += float(summary.get('pseudo_productive', 0) or 0)
            context_switches += int(summary.get('context_switches', 0) or 0)
            focus_sessions.extend(day.get('focus_sessions', []))
            for session in day.get('sessions', []):
                if (not session.get('is_pseudo_productive', False)
                        and str(session.get('category', '')).lower() != 'unclassified'):
                    try:
                        duration = float(session.get('duration_minutes', 0) or 0)
                    except (TypeError, ValueError):
                        duration = 0
                    if duration > 0:
                        productive_blocks.append(duration)

        measured_minutes = productive_minutes + pseudo_minutes
        completed_focus = sum(
            float(session.get('completion_percentage', 0) or 0) >= 100
            for session in focus_sessions
        )
        focus_minutes = sum(float(session.get('active_minutes', 0) or 0)
                            for session in focus_sessions)
        return {
            'productive_minutes': round(productive_minutes, 1),
            'pseudo_minutes': round(pseudo_minutes, 1),
            'pseudo_ratio': round((pseudo_minutes / measured_minutes) * 100, 1)
                            if measured_minutes else 0,
            'average_work_block': round(sum(productive_blocks) / len(productive_blocks), 1)
                                  if productive_blocks else 0,
            'longest_work_block': round(max(productive_blocks), 1) if productive_blocks else 0,
            'context_switches': context_switches,
            'focus_minutes': round(focus_minutes, 1),
            'focus_sessions': len(focus_sessions),
            'focus_completion_rate': round((completed_focus / len(focus_sessions)) * 100, 1)
                                     if focus_sessions else 0,
        }

    def build_insights(self, metrics):
        """Create concise, actionable interpretations of the current metrics."""
        insights = []
        if metrics['pseudo_ratio'] >= 30:
            insights.append(f"Pseudo-productive time is {metrics['pseudo_ratio']:.0f}% of measured work.")
        elif metrics['productive_minutes'] > 0:
            insights.append(f"Pseudo-productive time is contained at {metrics['pseudo_ratio']:.0f}%.")
        if metrics['focus_sessions']:
            insights.append(
                f"{metrics['focus_completion_rate']:.0f}% of focus sessions reached their target."
            )
        if metrics['longest_work_block']:
            insights.append(f"Longest uninterrupted work block: {metrics['longest_work_block']:.0f} min.")
        return insights[:3] or ["Track a work session to establish a baseline."]
    
    def calculate_weekly_stats(self, start_date=None):
        """Calculate stats for a week"""
        weekly_data = self.data_logger.get_weekly_data(start_date)
        
        weekly_totals = {
            'building': 0,
            'studying': 0,
            'applying': 0,
            'knowledge': 0,
            'pseudo_productive': 0,
            'total_productive': 0,
            'context_switches': 0
        }
        
        daily_summaries = []
        
        for day_data in weekly_data:
            day_summary = day_data['daily_summary']
            daily_summaries.append({
                'date': day_data['date'],
                'total': day_summary['total_productive'],
                'building': day_summary['building'],
                'studying': day_summary['studying'],
                'applying': day_summary['applying'],
                'knowledge': day_summary['knowledge']
            })
            
            # Add to weekly totals
            for key in weekly_totals:
                weekly_totals[key] += day_summary.get(key, 0)
        
        # Calculate insights
        best_day = max(daily_summaries, key=lambda x: x['total'], default=None)
        avg_daily = weekly_totals['total_productive'] / 7 if weekly_totals['total_productive'] > 0 else 0
        
        top_category = max(['building', 'studying', 'applying', 'knowledge'], 
                          key=lambda cat: weekly_totals[cat])
        
        return {
            'totals': weekly_totals,
            'daily_summaries': daily_summaries,
            'best_day': best_day,
            'average_daily': round(avg_daily / 60, 1),  # Convert to hours
            'top_category': top_category.title(),
            'consistency': self.calculate_consistency(daily_summaries),
            'metrics': self.calculate_productivity_metrics(weekly_data),
        }
    
    def calculate_monthly_stats(self, year=None, month=None):
        """Calculate stats for a month"""
        monthly_data = self.data_logger.get_monthly_data(year, month)
        
        monthly_totals = {
            'building': 0,
            'studying': 0,
            'applying': 0,
            'knowledge': 0,
            'pseudo_productive': 0,
            'total_productive': 0,
            'context_switches': 0
        }
        
        weekly_summaries = []
        current_week = []
        
        for day_data in monthly_data:
            day_summary = day_data['daily_summary']
            current_week.append(day_summary)
            
            # Add to monthly totals
            for key in monthly_totals:
                monthly_totals[key] += day_summary.get(key, 0)
            
            # Group into weeks (every 7 days)
            if len(current_week) == 7:
                week_total = sum(day['total_productive'] for day in current_week)
                weekly_summaries.append(week_total)
                current_week = []
        
        # Add remaining days as partial week
        if current_week:
            week_total = sum(day['total_productive'] for day in current_week)
            weekly_summaries.append(week_total)
        
        # Calculate insights
        best_week = max(weekly_summaries) if weekly_summaries else 0
        top_category = max(['building', 'studying', 'applying', 'knowledge'], 
                          key=lambda cat: monthly_totals[cat])
        
        return {
            'totals': monthly_totals,
            'weekly_summaries': weekly_summaries,
            'best_week': round(best_week / 60, 1),  # Convert to hours
            'top_category': top_category.title(),
            'days_with_work': len([d for d in monthly_data if d['daily_summary']['total_productive'] > 120]),
            'metrics': self.calculate_productivity_metrics(monthly_data),
        }
    
    def calculate_yearly_stats(self, year=None):
        """Calculate stats for a year"""
        if year is None:
            year = datetime.now().year
        
        yearly_totals = {
            'building': 0,
            'studying': 0,
            'applying': 0,
            'knowledge': 0,
            'pseudo_productive': 0,
            'total_productive': 0
        }
        
        quarterly_summaries = [0, 0, 0, 0]  # Q1, Q2, Q3, Q4
        monthly_totals = []
        yearly_data = []
        
        for month in range(1, 13):
            try:
                monthly_data = self.data_logger.get_monthly_data(year, month)
                yearly_data.extend(monthly_data)
                month_total = sum(day['daily_summary']['total_productive'] for day in monthly_data)
                monthly_totals.append(month_total)
                
                # Add to quarterly totals
                quarter = (month - 1) // 3
                quarterly_summaries[quarter] += month_total
                
                # Add to yearly totals
                for day_data in monthly_data:
                    day_summary = day_data['daily_summary']
                    for key in yearly_totals:
                        yearly_totals[key] += day_summary.get(key, 0)
            except:
                monthly_totals.append(0)
        
        # Calculate insights
        best_month = max(monthly_totals) if monthly_totals else 0
        best_quarter = max(quarterly_summaries) if quarterly_summaries else 0
        
        return {
            'totals': yearly_totals,
            'quarterly_summaries': [round(q / 60, 1) for q in quarterly_summaries],
            'monthly_totals': [round(m / 60, 1) for m in monthly_totals],
            'best_month': round(best_month / 60, 1),
            'best_quarter': round(best_quarter / 60, 1),
            'metrics': self.calculate_productivity_metrics(yearly_data),
        }
    
    def calculate_consistency(self, daily_summaries):
        """Calculate consistency score (0-1) based on daily work"""
        if not daily_summaries:
            return 0
        
        days_with_work = len([day for day in daily_summaries if day['total'] > 120])  # >2h
        return round(days_with_work / len(daily_summaries), 2)
