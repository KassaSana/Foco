"""
Trend Analyzer - Growth tracking and insights
Analyzes productivity trends over time and provides insights
"""
from datetime import datetime, timedelta
from collections import defaultdict

class TrendAnalyzer:
    def __init__(self, stats_calculator):
        self.stats_calculator = stats_calculator
    
    def analyze_weekly_trends(self, weeks_back=4):
        """Analyze trends over the last few weeks"""
        trends = []
        current_date = datetime.now()
        
        for i in range(weeks_back):
            # Get Monday of each week
            week_start = current_date - timedelta(days=current_date.weekday() + (i * 7))
            week_stats = self.stats_calculator.calculate_weekly_stats(week_start)
            
            trends.append({
                'week_start': week_start.strftime('%Y-%m-%d'),
                'total_hours': round(week_stats['totals']['total_productive'] / 60, 1),
                'building': round(week_stats['totals']['building'] / 60, 1),
                'studying': round(week_stats['totals']['studying'] / 60, 1),
                'applying': round(week_stats['totals']['applying'] / 60, 1),
                'knowledge': round(week_stats['totals']['knowledge'] / 60, 1),
                'consistency': week_stats['consistency']
            })
        
        # Calculate trends
        if len(trends) >= 2:
            latest = trends[0]
            previous = trends[1]
            
            growth = ((latest['total_hours'] - previous['total_hours']) / previous['total_hours'] * 100) if previous['total_hours'] > 0 else 0
            
            return {
                'weekly_data': trends,
                'growth_percentage': round(growth, 1),
                'trend_direction': 'up' if growth > 0 else 'down' if growth < 0 else 'stable',
                'average_weekly_hours': round(sum(w['total_hours'] for w in trends) / len(trends), 1),
                'most_improved_category': self.find_most_improved_category(trends)
            }
        
        return {'weekly_data': trends}
    
    def analyze_monthly_trends(self, months_back=6):
        """Analyze trends over the last few months"""
        trends = []
        current_date = datetime.now()
        
        for i in range(months_back):
            # Calculate target month/year
            target_month = current_date.month - i
            target_year = current_date.year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_stats = self.stats_calculator.calculate_monthly_stats(target_year, target_month)
            
            trends.append({
                'month': f"{target_year}-{target_month:02d}",
                'total_hours': round(month_stats['totals']['total_productive'] / 60, 1),
                'building': round(month_stats['totals']['building'] / 60, 1),
                'studying': round(month_stats['totals']['studying'] / 60, 1),
                'applying': round(month_stats['totals']['applying'] / 60, 1),
                'knowledge': round(month_stats['totals']['knowledge'] / 60, 1),
                'days_with_work': month_stats['days_with_work']
            })
        
        return {
            'monthly_data': trends,
            'average_monthly_hours': round(sum(m['total_hours'] for m in trends) / len(trends), 1) if trends else 0,
            'best_month': max(trends, key=lambda x: x['total_hours']) if trends else None,
            'consistency_trend': self.calculate_consistency_trend(trends)
        }
    
    def find_most_improved_category(self, weekly_trends):
        """Find which category improved the most"""
        if len(weekly_trends) < 2:
            return None
        
        latest = weekly_trends[0]
        previous = weekly_trends[1]
        
        categories = ['building', 'studying', 'applying', 'knowledge']
        improvements = {}
        
        for category in categories:
            if previous[category] > 0:
                improvement = ((latest[category] - previous[category]) / previous[category]) * 100
                improvements[category] = improvement
        
        if improvements:
            best_category = max(improvements.keys(), key=lambda k: improvements[k])
            return {
                'category': best_category.title(),
                'improvement': round(improvements[best_category], 1)
            }
        
        return None
    
    def calculate_consistency_trend(self, monthly_trends):
        """Calculate if consistency is improving"""
        if len(monthly_trends) < 3:
            return "insufficient_data"
        
        recent_months = monthly_trends[:3]
        older_months = monthly_trends[3:6] if len(monthly_trends) >= 6 else monthly_trends[3:]
        
        if not older_months:
            return "insufficient_data"
        
        recent_avg = sum(m['days_with_work'] for m in recent_months) / len(recent_months)
        older_avg = sum(m['days_with_work'] for m in older_months) / len(older_months)
        
        if recent_avg > older_avg * 1.1:
            return "improving"
        elif recent_avg < older_avg * 0.9:
            return "declining"
        else:
            return "stable"
    
    def get_productivity_insights(self):
        """Generate insights about productivity patterns"""
        insights = []
        
        # Weekly trends
        weekly_trends = self.analyze_weekly_trends(4)
        if 'growth_percentage' in weekly_trends:
            if weekly_trends['growth_percentage'] > 10:
                insights.append(f"📈 Great progress! Up {weekly_trends['growth_percentage']}% from last week")
            elif weekly_trends['growth_percentage'] < -10:
                insights.append(f"📉 Productivity down {abs(weekly_trends['growth_percentage'])}% from last week")
        
        # Category analysis
        if 'most_improved_category' in weekly_trends and weekly_trends['most_improved_category']:
            category_info = weekly_trends['most_improved_category']
            if category_info['improvement'] > 20:
                insights.append(f"🚀 {category_info['category']} time up {category_info['improvement']}%!")
        
        # Monthly trends
        monthly_trends = self.analyze_monthly_trends(3)
        if monthly_trends['consistency_trend'] == 'improving':
            insights.append("⭐ Your consistency is improving month over month")
        elif monthly_trends['consistency_trend'] == 'declining':
            insights.append("⚠️ Consider focusing on more consistent daily habits")
        
        # General insights
        if len(insights) == 0:
            insights.append("📊 Keep tracking to see your progress trends")
        
        return insights[:3]  # Return top 3 insights
    
    def get_weekly_comparison(self):
        """Compare this week to last week"""
        current_week = self.stats_calculator.calculate_weekly_stats()
        
        # Get last week's stats
        last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
        last_week = self.stats_calculator.calculate_weekly_stats(last_monday)
        
        comparison = {}
        
        for category in ['building', 'studying', 'applying', 'knowledge', 'total_productive']:
            current = current_week['totals'][category] / 60  # Convert to hours
            previous = last_week['totals'][category] / 60
            
            if previous > 0:
                change = ((current - previous) / previous) * 100
            else:
                change = 100 if current > 0 else 0
            
            comparison[category] = {
                'current': round(current, 1),
                'previous': round(previous, 1),
                'change_percentage': round(change, 1),
                'direction': 'up' if change > 0 else 'down' if change < 0 else 'same'
            }
        
        return comparison
    
    def predict_monthly_total(self):
        """Predict end-of-month total based on current pace"""
        today = datetime.now()
        days_in_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).day if today.month < 12 else 31
        days_elapsed = today.day
        days_remaining = days_in_month - days_elapsed
        
        # Get current month's data
        monthly_stats = self.stats_calculator.calculate_monthly_stats()
        current_total = monthly_stats['totals']['total_productive'] / 60  # Convert to hours
        
        if days_elapsed > 0:
            daily_average = current_total / days_elapsed
            predicted_total = current_total + (daily_average * days_remaining)
            
            return {
                'current_total': round(current_total, 1),
                'predicted_total': round(predicted_total, 1),
                'daily_average': round(daily_average, 1),
                'days_remaining': days_remaining
            }
        
        return None