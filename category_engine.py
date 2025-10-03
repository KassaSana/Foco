"""
Category Engine - Smart activity categorization logic
Categorizes activities and detects pseudo-productive time
"""
import json
import os

class CategoryEngine:
    def __init__(self):
        self.config = self.load_config()
        
        # App patterns for categorization
        self.building_apps = self.config.get('building_apps', [])
        self.studying_apps = self.config.get('studying_apps', [])
        self.applying_sites = self.config.get('applying_sites', [])
        self.pseudo_productive_sites = self.config.get('pseudo_productive_sites', [])
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'building_apps': ['code.exe', 'idea64.exe', 'pycharm64.exe', 'cmd.exe', 'powershell.exe'],
                'studying_apps': ['canvas', 'pdf', 'notion', 'onenote', 'acrobat'],
                'applying_sites': ['linkedin.com', 'indeed.com', 'glassdoor.com'],
                'pseudo_productive_sites': ['youtube.com', 'reddit.com', 'twitter.com']
            }
    
    def categorize_activity(self, app_name, window_title):
        """Categorize an activity into Building/Studying/Applying/Knowledge"""
        app_name_lower = app_name.lower()
        window_title_lower = window_title.lower()
        
        # Building - Coding, development tools
        if any(app in app_name_lower for app in self.building_apps):
            return 'Building'
        
        # Terminal/command line work
        if any(term in app_name_lower for term in ['cmd', 'powershell', 'terminal', 'git']):
            return 'Building'
        
        # Studying - Educational content, PDFs, notes
        if any(app in app_name_lower for app in self.studying_apps):
            return 'Studying'
        
        if any(keyword in window_title_lower for keyword in ['canvas', 'coursera', 'udemy', 'khan academy']):
            return 'Studying'
        
        # Applying - Job search, LinkedIn, career sites
        if 'linkedin' in window_title_lower or 'linkedin' in app_name_lower:
            if any(keyword in window_title_lower for keyword in ['job', 'career', 'apply', 'resume']):
                return 'Applying'
        
        if any(site in window_title_lower for site in self.applying_sites):
            return 'Applying'
        
        # Browser-based categorization
        if any(browser in app_name_lower for browser in ['chrome', 'firefox', 'edge', 'browser']):
            return self.categorize_browser_activity(window_title_lower)
        
        # Default to Knowledge Building
        return 'Knowledge'
    
    def categorize_browser_activity(self, window_title):
        """Categorize browser activity based on window title/URL"""
        # Job application sites
        if any(site in window_title for site in self.applying_sites):
            return 'Applying'
        
        # Educational sites
        educational_sites = ['stackoverflow.com', 'github.com', 'documentation', 'tutorial', 'learn']
        if any(site in window_title for site in educational_sites):
            return 'Knowledge'
        
        # Programming/development
        if any(keyword in window_title for keyword in ['github', 'gitlab', 'bitbucket', 'code']):
            return 'Building'
        
        # Social media and distractions
        if any(site in window_title for site in self.pseudo_productive_sites):
            return 'Knowledge'  # Will be flagged as pseudo-productive
        
        return 'Knowledge'
    
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
        if any(site in window_title_lower for site in self.pseudo_productive_sites):
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
    
    def get_category_color(self, category):
        """Get color coding for categories"""
        colors = {
            'Building': '#4CAF50',      # Green
            'Studying': '#2196F3',      # Blue  
            'Applying': '#FF9800',      # Orange
            'Knowledge': '#9C27B0'      # Purple
        }
        return colors.get(category, '#757575')  # Default gray