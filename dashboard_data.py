"""
Dashboard Data Provider Module
Calculates statistics and trends for the admin dashboard
"""

from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

class DashboardDataProvider:
    """Provides data and statistics for the admin dashboard"""
    
    def __init__(self):
        """Initialize dashboard data provider"""
        self.categories = ['Water', 'Electricity', 'Transportation']
        self.priorities = ['High', 'Medium', 'Low']
        self.statuses = ['Open', 'In Progress', 'Resolved']
    
    def calculate_stats(self, complaints: List[Dict]) -> Dict:
        """
        Calculate comprehensive statistics from complaints
        
        Args:
            complaints: List of complaint dictionaries
            
        Returns:
            Dictionary with various statistics
        """
        if not complaints:
            return self._get_empty_stats()
        
        df = pd.DataFrame(complaints)
        
        # Total complaints
        total_complaints = len(complaints)
        
        # Category distribution
        category_counts = df['Category'].value_counts().to_dict() if 'Category' in df.columns else {}
        
        # Priority distribution
        priority_counts = df['Priority'].value_counts().to_dict() if 'Priority' in df.columns else {}
        
        # Status distribution
        status_counts = df['Status'].value_counts().to_dict() if 'Status' in df.columns else {}
        
        # High priority complaints
        high_priority = df[df['Priority'] == 'High'].to_dict('records') if 'Priority' in df.columns else []
        
        # Open complaints
        open_complaints = df[df['Status'] == 'Open'].to_dict('records') if 'Status' in df.columns else []
        
        # Users affected
        total_users_affected = df['Users_Affected'].sum() if 'Users_Affected' in df.columns else 0
        
        # Average resolution time (for resolved complaints)
        avg_resolution_time = self._calculate_avg_resolution_time(df)
        
        # Category percentages
        category_percentages = {
            cat: round((category_counts.get(cat, 0) / total_complaints) * 100, 1)
            for cat in self.categories
        }
        
        # Resolution rate
        resolved_count = status_counts.get('Resolved', 0)
        resolution_rate = round((resolved_count / total_complaints) * 100, 1) if total_complaints > 0 else 0
        
        return {
            'total_complaints': total_complaints,
            'category_distribution': category_counts,
            'category_percentages': category_percentages,
            'priority_distribution': priority_counts,
            'status_distribution': status_counts,
            'high_priority_complaints': high_priority[:10],  # Top 10
            'open_complaints_count': len(open_complaints),
            'resolved_complaints_count': resolved_count,
            'in_progress_count': status_counts.get('In Progress', 0),
            'total_users_affected': int(total_users_affected),
            'average_resolution_time': avg_resolution_time,
            'resolution_rate': resolution_rate,
            'most_affected_locations': self._get_most_affected_locations(df),
            'category_wise_priority': self._get_category_wise_priority(df)
        }
    
    def calculate_trends(self, complaints: List[Dict]) -> Dict:
        """
        Calculate trends over time
        
        Args:
            complaints: List of complaint dictionaries
            
        Returns:
            Dictionary with trend data
        """
        try:
            if not complaints:
                return self._get_empty_trends()
            
            df = pd.DataFrame(complaints)
            
            # Parse dates
            if 'Date' not in df.columns:
                return self._get_empty_trends()
            
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
            df = df.dropna(subset=['Date'])
            
            if len(df) == 0:
                return self._get_empty_trends()
            
            # Sort by date
            df = df.sort_values('Date')
            
            # Daily complaints
            daily_complaints = df.groupby(df['Date'].dt.date).size().to_dict()
            daily_complaints = {str(k): int(v) for k, v in daily_complaints.items()}
            
            # Weekly trends - use week of year
            df['Week'] = df['Date'].dt.isocalendar().week
            weekly_complaints = df.groupby('Week').size().to_dict()
            weekly_complaints = {str(k): int(v) for k, v in weekly_complaints.items()}
        
            # Category trends over time
            category_trends = {}
            for category in self.categories:
                cat_df = df[df['Category'] == category]
                cat_daily = cat_df.groupby(cat_df['Date'].dt.date).size().to_dict()
                category_trends[category] = {str(k): int(v) for k, v in cat_daily.items()}
            
            # Last 7 days data
            last_7_days = self._get_last_n_days_data(df, 7)
            
            # Last 30 days data
            last_30_days = self._get_last_n_days_data(df, 30)
            
            # Peak hours/days analysis
            peak_analysis = self._analyze_peak_times(df)
            
            return {
                'daily_complaints': daily_complaints,
                'weekly_complaints': weekly_complaints,
                'category_trends': category_trends,
                'last_7_days': last_7_days,
                'last_30_days': last_30_days,
                'peak_analysis': peak_analysis,
                'trend_direction': self._calculate_trend_direction(df)
            }
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return self._get_empty_trends()
    
    def _calculate_avg_resolution_time(self, df: pd.DataFrame) -> str:
        """Calculate average resolution time"""
        # This is a simplified version - in production, you'd track actual resolution timestamps
        resolved_df = df[df['Status'] == 'Resolved'] if 'Status' in df.columns else pd.DataFrame()
        
        if len(resolved_df) == 0:
            return "N/A"
        
        # Estimate based on priority
        time_estimates = {'High': 3, 'Medium': 6, 'Low': 12}  # hours
        
        if 'Priority' in resolved_df.columns:
            avg_hours = resolved_df['Priority'].map(time_estimates).mean()
            return f"{avg_hours:.1f} hours"
        
        return "6 hours (estimated)"
    
    def _get_most_affected_locations(self, df: pd.DataFrame) -> List[Dict]:
        """Get locations with most complaints"""
        if 'Location' not in df.columns:
            return []
        
        location_counts = df['Location'].value_counts().head(5)
        
        return [
            {'location': loc, 'count': int(count)}
            for loc, count in location_counts.items()
        ]
    
    def _get_category_wise_priority(self, df: pd.DataFrame) -> Dict:
        """Get priority distribution for each category"""
        if 'Category' not in df.columns or 'Priority' not in df.columns:
            return {}
        
        result = {}
        for category in self.categories:
            cat_df = df[df['Category'] == category]
            priority_dist = cat_df['Priority'].value_counts().to_dict()
            result[category] = priority_dist
        
        return result
    
    def _get_last_n_days_data(self, df: pd.DataFrame, n: int) -> Dict:
        """Get data for last N days"""
        if 'Date' not in df.columns:
            return {}
        
        cutoff_date = datetime.now() - timedelta(days=n)
        recent_df = df[df['Date'] >= cutoff_date]
        
        return {
            'total_complaints': len(recent_df),
            'by_category': recent_df['Category'].value_counts().to_dict() if 'Category' in recent_df.columns else {},
            'by_priority': recent_df['Priority'].value_counts().to_dict() if 'Priority' in recent_df.columns else {},
            'by_status': recent_df['Status'].value_counts().to_dict() if 'Status' in recent_df.columns else {}
        }
    
    def _analyze_peak_times(self, df: pd.DataFrame) -> Dict:
        """Analyze peak complaint times"""
        if 'Date' not in df.columns:
            return {}
        
        # Day of week analysis
        df['DayOfWeek'] = df['Date'].dt.day_name()
        day_counts = df['DayOfWeek'].value_counts().to_dict()
        
        # Find peak day
        peak_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else ('N/A', 0)
        
        return {
            'by_day_of_week': day_counts,
            'peak_day': peak_day[0],
            'peak_day_count': int(peak_day[1])
        }
    
    def _calculate_trend_direction(self, df: pd.DataFrame) -> str:
        """Calculate if complaints are trending up or down"""
        if 'Date' not in df.columns or len(df) < 14:
            return "stable"
        
        # Compare last 7 days with previous 7 days
        now = datetime.now()
        last_7_days = df[df['Date'] >= (now - timedelta(days=7))]
        prev_7_days = df[(df['Date'] >= (now - timedelta(days=14))) & 
                        (df['Date'] < (now - timedelta(days=7)))]
        
        last_count = len(last_7_days)
        prev_count = len(prev_7_days)
        
        if prev_count == 0:
            return "stable"
        
        change_percent = ((last_count - prev_count) / prev_count) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _get_empty_stats(self) -> Dict:
        """Return empty stats structure"""
        return {
            'total_complaints': 0,
            'category_distribution': {},
            'category_percentages': {},
            'priority_distribution': {},
            'status_distribution': {},
            'high_priority_complaints': [],
            'open_complaints_count': 0,
            'resolved_complaints_count': 0,
            'in_progress_count': 0,
            'total_users_affected': 0,
            'average_resolution_time': 'N/A',
            'resolution_rate': 0,
            'most_affected_locations': [],
            'category_wise_priority': {}
        }
    
    def _get_empty_trends(self) -> Dict:
        """Return empty trends structure"""
        return {
            'daily_complaints': {},
            'weekly_complaints': {},
            'category_trends': {},
            'last_7_days': {},
            'last_30_days': {},
            'peak_analysis': {},
            'trend_direction': 'stable'
        }
    
    def get_sustainability_metrics(self, complaints: List[Dict]) -> Dict:
        """
        Calculate sustainability-related metrics
        
        Args:
            complaints: List of complaint dictionaries
            
        Returns:
            Dictionary with sustainability metrics
        """
        if not complaints:
            return {}
        
        df = pd.DataFrame(complaints)
        
        # Water conservation impact
        water_complaints = df[df['Category'] == 'Water'] if 'Category' in df.columns else pd.DataFrame()
        water_users_affected = water_complaints['Users_Affected'].sum() if 'Users_Affected' in water_complaints.columns else 0
        
        # Energy efficiency impact
        electricity_complaints = df[df['Category'] == 'Electricity'] if 'Category' in df.columns else pd.DataFrame()
        energy_users_affected = electricity_complaints['Users_Affected'].sum() if 'Users_Affected' in electricity_complaints.columns else 0
        
        # Transportation carbon footprint
        transport_complaints = df[df['Category'] == 'Transportation'] if 'Category' in df.columns else pd.DataFrame()
        transport_users_affected = transport_complaints['Users_Affected'].sum() if 'Users_Affected' in transport_complaints.columns else 0
        
        return {
            'water_conservation': {
                'complaints': len(water_complaints),
                'users_affected': int(water_users_affected),
                'sdg_goal': 6,
                'impact_level': 'High' if len(water_complaints) > 10 else 'Medium'
            },
            'energy_efficiency': {
                'complaints': len(electricity_complaints),
                'users_affected': int(energy_users_affected),
                'sdg_goal': 7,
                'impact_level': 'High' if len(electricity_complaints) > 10 else 'Medium'
            },
            'sustainable_transport': {
                'complaints': len(transport_complaints),
                'users_affected': int(transport_users_affected),
                'sdg_goal': 11,
                'impact_level': 'Medium' if len(transport_complaints) > 5 else 'Low'
            },
            'overall_sustainability_score': self._calculate_sustainability_score(df)
        }
    
    def _calculate_sustainability_score(self, df: pd.DataFrame) -> int:
        """Calculate overall sustainability score (0-100)"""
        if len(df) == 0:
            return 100
        
        # Lower score for more unresolved complaints
        resolved_count = len(df[df['Status'] == 'Resolved']) if 'Status' in df.columns else 0
        resolution_rate = (resolved_count / len(df)) * 100 if len(df) > 0 else 0
        
        # Penalty for high priority issues
        high_priority_count = len(df[df['Priority'] == 'High']) if 'Priority' in df.columns else 0
        high_priority_penalty = (high_priority_count / len(df)) * 20 if len(df) > 0 else 0
        
        score = resolution_rate - high_priority_penalty
        return max(0, min(100, int(score)))

# Made with Bob
