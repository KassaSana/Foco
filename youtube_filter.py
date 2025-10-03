"""
Smart YouTube Filter - Allows only educational content
Integrates with browser monitoring to block non-educational YouTube
"""
import re
from urllib.parse import parse_qs, urlparse

class YouTubeFilter:
    def __init__(self):
        # Educational channels that are always allowed
        self.allowed_channels = [
            "neetcode", "neetcodeio", "leetcode",
            "freecodecamp", "codecademy", "coursera",
            "khanacademy", "khan academy",
            "mit", "stanford", "harvard", "berkeley", "cs50",
            "3blue1brown", "computerphile", "numberphile",
            "programming with mosh", "traversy media", "corey schafer",
            "tech with tim", "sentdex", "derek banas",
            "ben eater", "computerscience", "algorithms explained",
            "geeksforgeeks", "tutorialspoint",
        ]
        
        # Educational keywords in video titles
        self.educational_keywords = [
            "tutorial", "course", "lecture", "learn", "learning",
            "programming", "coding", "algorithm", "data structure",
            "computer science", "software engineering", "development",
            "python", "javascript", "java", "c++", "react", "node", "angular", "vue",
            "interview", "leetcode", "coding interview", "system design",
            "mathematics", "calculus", "statistics", "physics", "machine learning",
            "university", "college", "education", "academic", "bootcamp",
            "explained", "how to", "guide", "walkthrough", "beginner", "basics",
            "web development", "app development", "software", "coding"
        ]
        
        # Content that should be blocked (entertainment)
        self.blocked_keywords = [
            "funny", "meme", "memes", "react", "reaction", "reacting",
            "prank", "pranks", "fail", "fails", "compilation",
            "tiktok", "shorts", "vlog", "vlogging", "daily vlog",
            "lifestyle", "drama", "gossip", "celebrity",
            "gaming", "gameplay", "stream", "streaming", "highlights",
            "music video", "song", "album", "concert", "live performance",
            "unboxing", "haul", "shopping", "review" + " product",
            "storytime", "story time", "personal", "my life",
            "roast", "roasting", "diss", "beef", "exposed"
        ]
    
    def is_educational_content(self, title, channel=None, description=None):
        """Check if YouTube content is educational"""
        if not title:
            return False
        
        title_lower = title.lower()
        
        # Check channel whitelist
        if channel:
            channel_lower = channel.lower()
            for allowed in self.allowed_channels:
                if allowed in channel_lower:
                    return True
        
        # Check for educational keywords
        educational_score = 0
        for keyword in self.educational_keywords:
            if keyword in title_lower:
                educational_score += 1
        
        # Check for blocked keywords
        blocked_score = 0
        for keyword in self.blocked_keywords:
            if keyword in title_lower:
                blocked_score += 2  # Blocked keywords weigh more
        
        # Educational content needs positive score and blocked score shouldn't outweigh it
        # Allow if educational keywords outweigh blocked keywords
        return educational_score > 0 and educational_score >= blocked_score
    
    def extract_video_info(self, url):
        """Extract video information from YouTube URL"""
        try:
            parsed = urlparse(url)
            
            if 'youtube.com' in parsed.netloc:
                # Extract video ID
                if 'watch' in parsed.path:
                    query_params = parse_qs(parsed.query)
                    video_id = query_params.get('v', [None])[0]
                    return {'video_id': video_id, 'type': 'video'}
                elif '/c/' in parsed.path or '/channel/' in parsed.path:
                    return {'type': 'channel', 'path': parsed.path}
            
            return None
            
        except Exception:
            return None

def create_browser_extension():
    """Create a simple browser extension manifest for Chrome"""
    manifest = {
        "manifest_version": 3,
        "name": "ADHD Productivity YouTube Filter",
        "version": "1.0",
        "description": "Blocks non-educational YouTube content during focus sessions",
        "permissions": ["activeTab", "storage"],
        "content_scripts": [{
            "matches": ["*://*.youtube.com/*"],
            "js": ["youtube_filter.js"],
            "run_at": "document_start"
        }],
        "background": {
            "service_worker": "background.js"
        }
    }
    
    return manifest

def create_youtube_filter_js():
    """Create JavaScript for YouTube filtering"""
    js_code = '''
// ADHD Productivity YouTube Filter
(function() {
    'use strict';
    
    const educationalKeywords = [
        'tutorial', 'course', 'lecture', 'learn', 'programming', 'coding',
        'algorithm', 'interview', 'leetcode', 'neetcode', 'computer science',
        'mathematics', 'explained', 'how to', 'guide'
    ];
    
    const blockedKeywords = [
        'funny', 'meme', 'react', 'prank', 'fail', 'gaming', 'music video',
        'vlog', 'tiktok', 'shorts', 'drama', 'roast'
    ];
    
    const allowedChannels = [
        'neetcode', 'freecodecamp', 'khanacademy', '3blue1brown',
        'computerphile', 'mit', 'stanford', 'cs50'
    ];
    
    function isEducational(title, channel) {
        const titleLower = title.toLowerCase();
        const channelLower = (channel || '').toLowerCase();
        
        // Check allowed channels
        for (let allowedChannel of allowedChannels) {
            if (channelLower.includes(allowedChannel)) {
                return true;
            }
        }
        
        // Check keywords
        let eduScore = 0;
        let blockScore = 0;
        
        for (let keyword of educationalKeywords) {
            if (titleLower.includes(keyword)) eduScore++;
        }
        
        for (let keyword of blockedKeywords) {
            if (titleLower.includes(keyword)) blockScore += 2;
        }
        
        return eduScore > 0 && blockScore === 0;
    }
    
    function blockVideo() {
        document.body.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background: #1a1a1a; color: white; font-family: Arial;">
                <div style="text-align: center;">
                    <h1>🔒 Content Blocked</h1>
                    <p>This video is not educational content.</p>
                    <p>Focus on your studies! 💪</p>
                    <p><a href="/results?search_query=programming+tutorial" style="color: #4CAF50;">Find educational content instead</a></p>
                </div>
            </div>
        `;
    }
    
    function checkCurrentVideo() {
        const title = document.querySelector('h1.title')?.textContent || 
                     document.querySelector('#container h1')?.textContent ||
                     document.title;
        
        const channel = document.querySelector('#channel-name a')?.textContent ||
                       document.querySelector('.ytd-channel-name a')?.textContent;
        
        if (title && !isEducational(title, channel)) {
            blockVideo();
        }
    }
    
    // Check immediately and on URL changes
    checkCurrentVideo();
    
    // Monitor for navigation changes
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            setTimeout(checkCurrentVideo, 1000);
        }
    }).observe(document, {subtree: true, childList: true});
    
})();
'''
    return js_code

if __name__ == "__main__":
    # Test the filter
    filter = YouTubeFilter()
    
    test_videos = [
        ("NeetCode Array Tutorial", "neetcode"),
        ("CS50 Introduction to Programming", "harvard"),
        "Funny Cat Compilation 2024",
        "React Tutorial for Beginners",
        "Music Video - Latest Hits",
        "Algorithm Explained: Binary Search"
    ]
    
    print("🧪 Testing YouTube Filter:")
    print("=" * 40)
    
    for video in test_videos:
        if isinstance(video, tuple):
            title, channel = video
        else:
            title, channel = video, None
        
        is_allowed = filter.is_educational_content(title, channel)
        status = "✅ ALLOWED" if is_allowed else "❌ BLOCKED"
        print(f"{status}: {title}")