"""
Category Engine - Smart activity categorization logic
Categorizes activities and detects pseudo-productive time
"""
from ..config import load_config

class CategoryEngine:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.reload_config()

    def reload_config(self):
        self.config = load_config(self.config_path)
        # App patterns for categorization
        self.building_apps = self.config.get('building_apps', [])
        self.studying_apps = self.config.get('studying_apps', [])
        self.applying_sites = self.config.get('applying_sites', [])
        self.pseudo_productive_sites = self.config.get('pseudo_productive_sites', [])
        return self.config
    
    @staticmethod
    def _pattern_matches(pattern, *values):
        pattern = str(pattern).lower().strip()
        if not pattern:
            return False
        stem = pattern.rsplit('/', 1)[-1]
        if '.' in stem:
            stem = stem.rsplit('.', 1)[0]
        return any(pattern in value or (stem and stem in value) for value in values)

    def classify_activity(self, app_name, window_title):
        """Return a category and a human-readable reason for the match."""
        app_name_lower = str(app_name or '').lower()
        window_title_lower = str(window_title or '').lower()
        values = (app_name_lower, window_title_lower)

        for pattern in self.building_apps:
            if self._pattern_matches(pattern, *values):
                return 'Building', f'Building rule matched: {pattern}'
        if any(term in app_name_lower for term in ['cmd', 'powershell', 'terminal', 'git']):
            return 'Building', 'Terminal or Git application'

        for pattern in self.studying_apps:
            if self._pattern_matches(pattern, *values):
                return 'Studying', f'Studying rule matched: {pattern}'
        for keyword in ['canvas', 'coursera', 'udemy', 'khan academy']:
            if keyword in window_title_lower:
                return 'Studying', f'Educational title matched: {keyword}'

        for pattern in self.applying_sites:
            if self._pattern_matches(pattern, *values):
                return 'Applying', f'Applying rule matched: {pattern}'
        if 'linkedin' in window_title_lower or 'linkedin' in app_name_lower:
            for keyword in ['job', 'career', 'apply', 'resume']:
                if keyword in window_title_lower:
                    return 'Applying', f'Job-search title matched: {keyword}'

        if any(browser in app_name_lower for browser in ['chrome', 'firefox', 'edge', 'browser']):
            return self._classify_browser_activity(window_title_lower)

        return 'Unclassified', 'No classification rule matched'

    def categorize_activity(self, app_name, window_title):
        """Categorize an activity, retaining the historical string API."""
        return self.classify_activity(app_name, window_title)[0]
    
    def categorize_browser_activity(self, window_title):
        """Categorize a browser title, retaining the historical string API."""
        return self._classify_browser_activity(str(window_title or '').lower())[0]

    def _classify_browser_activity(self, window_title):
        """Categorize browser activity based on window title/URL"""
        # Job application sites
        for site in self.applying_sites:
            if self._pattern_matches(site, window_title):
                return 'Applying', f'Applying browser title matched: {site}'
        
        # Educational sites
        educational_sites = ['stackoverflow.com', 'github.com', 'documentation', 'tutorial', 'learn']
        for site in educational_sites:
            if site in window_title:
                return 'Knowledge', f'Knowledge browser title matched: {site}'
        
        # Programming/development
        for keyword in ['github', 'gitlab', 'bitbucket', 'code']:
            if keyword in window_title:
                return 'Building', f'Building browser title matched: {keyword}'
        
        # Social media and distractions
        for site in self.pseudo_productive_sites:
            if self._pattern_matches(site, window_title):
                return 'Unclassified', f'Pseudo-productive title matched: {site}'

        return 'Unclassified', 'Browser title did not match a classification rule'
    
    def is_pseudo_productive(self, app_name, window_title):
        """Detect if current activity is pseudo-productive"""
        window_title_lower = window_title.lower()
        app_name_lower = app_name.lower()
        
        # YouTube programming videos
        if 'youtube' in window_title_lower:
            programming_keywords = ['programming', 'coding', 'developer', 'tutorial', 'how to code', 
                                  'productivity', 'motivation', 'tips', 'career advice', 'programmer', 'better']
            if any(keyword in window_title_lower for keyword in programming_keywords):
                return True
        
        # Social media sites
        if any(self._pattern_matches(site, app_name_lower, window_title_lower)
               for site in self.pseudo_productive_sites):
            return True
        
        # Reddit programming discussions
        if 'reddit' in window_title_lower:
            return True
        
        # LinkedIn feed scrolling (vs actual job applications)
        if 'linkedin' in window_title_lower:
            if not any(keyword in window_title_lower for keyword in ['job', 'apply', 'message', 'post job']):
                return True
        
        # IDE open but no activity (this would need more sophisticated detection)
        if any(ide in app_name_lower for ide in ['code.exe', 'idea64.exe']) and 'untitled' in window_title_lower:
            return True
        
        return False
