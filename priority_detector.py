"""
Priority Detection Module
Determines complaint priority based on multiple factors
"""

from typing import Dict, Optional
from datetime import datetime

class PriorityDetector:
    """Detects and assigns priority levels to complaints"""
    
    def __init__(self):
        """Initialize priority detector with scoring rules"""
        self.priority_weights = {
            'urgency_keywords': 0.4,
            'users_affected': 0.3,
            'category_severity': 0.2,
            'time_sensitivity': 0.1
        }
        
        self.high_urgency_keywords = [
            'emergency', 'urgent', 'critical', 'danger', 'hazard',
            'sparks', 'contamination', 'no water', 'no power',
            'breakdown', 'failure', 'severe', 'immediate'
        ]
        
        self.medium_urgency_keywords = [
            'issue', 'problem', 'malfunction', 'disruption',
            'delayed', 'overcrowded', 'fluctuation', 'leakage'
        ]
        
        self.category_severity = {
            'Water': {
                'contamination': 'High',
                'no supply': 'High',
                'leakage': 'Medium',
                'overflow': 'Low'
            },
            'Electricity': {
                'sparks': 'High',
                'generator failure': 'High',
                'power cut': 'Medium',
                'fluctuation': 'Medium',
                'lights not working': 'Low'
            },
            'Transportation': {
                'breakdown': 'High',
                'overcrowded': 'Medium',
                'delayed': 'Medium',
                'route issue': 'Low'
            }
        }
    
    def detect_priority(self, complaint_text: str, users_affected: int, 
                       classification: Dict) -> str:
        """
        Detect priority level for a complaint
        
        Args:
            complaint_text: The complaint description
            users_affected: Number of users affected
            classification: Classification result from Granite
            
        Returns:
            Priority level: 'High', 'Medium', or 'Low'
        """
        score = 0.0
        text_lower = complaint_text.lower()
        
        # 1. Urgency keywords score (0-1)
        urgency_score = self._calculate_urgency_score(text_lower)
        score += urgency_score * self.priority_weights['urgency_keywords']
        
        # 2. Users affected score (0-1)
        users_score = self._calculate_users_score(users_affected)
        score += users_score * self.priority_weights['users_affected']
        
        # 3. Category severity score (0-1)
        category_score = self._calculate_category_score(
            text_lower, 
            classification.get('category', 'Water')
        )
        score += category_score * self.priority_weights['category_severity']
        
        # 4. Time sensitivity score (0-1)
        time_score = self._calculate_time_sensitivity(text_lower)
        score += time_score * self.priority_weights['time_sensitivity']
        
        # Convert score to priority level
        if score >= 0.7:
            return 'High'
        elif score >= 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_urgency_score(self, text_lower: str) -> float:
        """Calculate urgency score based on keywords"""
        # Check for high urgency keywords
        high_count = sum(1 for keyword in self.high_urgency_keywords 
                        if keyword in text_lower)
        if high_count > 0:
            return 1.0
        
        # Check for medium urgency keywords
        medium_count = sum(1 for keyword in self.medium_urgency_keywords 
                          if keyword in text_lower)
        if medium_count > 0:
            return 0.6
        
        return 0.3
    
    def _calculate_users_score(self, users_affected: int) -> float:
        """Calculate score based on number of users affected"""
        if users_affected >= 200:
            return 1.0
        elif users_affected >= 100:
            return 0.8
        elif users_affected >= 50:
            return 0.6
        elif users_affected >= 20:
            return 0.4
        else:
            return 0.2
    
    def _calculate_category_score(self, text_lower: str, category: str) -> float:
        """Calculate score based on category-specific severity"""
        if category not in self.category_severity:
            return 0.5
        
        severity_map = self.category_severity[category]
        
        for issue_type, severity in severity_map.items():
            if issue_type.lower() in text_lower:
                if severity == 'High':
                    return 1.0
                elif severity == 'Medium':
                    return 0.6
                else:
                    return 0.3
        
        return 0.5
    
    def _calculate_time_sensitivity(self, text_lower: str) -> float:
        """Calculate time sensitivity score"""
        time_critical_keywords = [
            'since morning', 'hours', 'days', 'immediate',
            'now', 'currently', 'ongoing'
        ]
        
        for keyword in time_critical_keywords:
            if keyword in text_lower:
                return 1.0
        
        return 0.5
    
    def get_priority_explanation(self, complaint_text: str, users_affected: int,
                                classification: Dict) -> Dict:
        """
        Get detailed explanation of priority assignment
        
        Args:
            complaint_text: The complaint description
            users_affected: Number of users affected
            classification: Classification result
            
        Returns:
            Dictionary with priority and explanation
        """
        text_lower = complaint_text.lower()
        
        urgency_score = self._calculate_urgency_score(text_lower)
        users_score = self._calculate_users_score(users_affected)
        category_score = self._calculate_category_score(
            text_lower, 
            classification.get('category', 'Water')
        )
        time_score = self._calculate_time_sensitivity(text_lower)
        
        total_score = (
            urgency_score * self.priority_weights['urgency_keywords'] +
            users_score * self.priority_weights['users_affected'] +
            category_score * self.priority_weights['category_severity'] +
            time_score * self.priority_weights['time_sensitivity']
        )
        
        priority = 'High' if total_score >= 0.7 else 'Medium' if total_score >= 0.4 else 'Low'
        
        return {
            'priority': priority,
            'score': round(total_score, 2),
            'factors': {
                'urgency_keywords': {
                    'score': round(urgency_score, 2),
                    'weight': self.priority_weights['urgency_keywords'],
                    'contribution': round(urgency_score * self.priority_weights['urgency_keywords'], 2)
                },
                'users_affected': {
                    'score': round(users_score, 2),
                    'weight': self.priority_weights['users_affected'],
                    'contribution': round(users_score * self.priority_weights['users_affected'], 2),
                    'count': users_affected
                },
                'category_severity': {
                    'score': round(category_score, 2),
                    'weight': self.priority_weights['category_severity'],
                    'contribution': round(category_score * self.priority_weights['category_severity'], 2)
                },
                'time_sensitivity': {
                    'score': round(time_score, 2),
                    'weight': self.priority_weights['time_sensitivity'],
                    'contribution': round(time_score * self.priority_weights['time_sensitivity'], 2)
                }
            },
            'explanation': self._generate_explanation(priority, urgency_score, users_affected, category_score)
        }
    
    def _generate_explanation(self, priority: str, urgency_score: float, 
                            users_affected: int, category_score: float) -> str:
        """Generate human-readable explanation for priority"""
        explanations = []
        
        if urgency_score >= 0.8:
            explanations.append("Contains critical urgency keywords")
        
        if users_affected >= 100:
            explanations.append(f"Affects a large number of users ({users_affected})")
        elif users_affected >= 50:
            explanations.append(f"Affects a significant number of users ({users_affected})")
        
        if category_score >= 0.8:
            explanations.append("Issue type is categorized as high severity")
        
        if not explanations:
            explanations.append("Standard priority based on overall assessment")
        
        return f"{priority} priority assigned. " + "; ".join(explanations) + "."
    
    def recalculate_priority(self, complaint_id: str, new_users_affected: Optional[int] = None,
                           status_change: Optional[str] = None) -> str:
        """
        Recalculate priority when complaint details change
        
        Args:
            complaint_id: The complaint ID
            new_users_affected: Updated number of users affected
            status_change: New status if changed
            
        Returns:
            Updated priority level
        """
        # This would integrate with the sheets manager to get current complaint
        # and recalculate priority based on new information
        # For now, return a placeholder
        return 'Medium'

# Made with Bob
