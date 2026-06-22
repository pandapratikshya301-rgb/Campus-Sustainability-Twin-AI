"""
AI Recommendation Engine Module
Generates actionable recommendations using IBM Granite and RAG knowledge base
"""

from typing import Dict, List
from modules.rag_knowledge_base import RAGKnowledgeBase
from modules.granite_classifier import GraniteClassifier

class RecommendationEngine:
    """Generates AI-powered recommendations for complaint resolution"""
    
    def __init__(self, rag_kb: RAGKnowledgeBase, granite_classifier: GraniteClassifier):
        """
        Initialize recommendation engine
        
        Args:
            rag_kb: RAG knowledge base instance
            granite_classifier: Granite classifier instance
        """
        self.rag_kb = rag_kb
        self.granite_classifier = granite_classifier
    
    def get_recommendations(self, complaint_text: str, classification: Dict, 
                          priority: str) -> Dict:
        """
        Generate comprehensive recommendations for a complaint
        
        Args:
            complaint_text: The complaint description
            classification: Classification result from Granite
            priority: Priority level
            
        Returns:
            Dictionary with recommendations and action items
        """
        category = classification.get('category', 'Water')
        
        # Get relevant guidelines from RAG knowledge base
        guidelines = self.rag_kb.search(
            query=complaint_text,
            top_k=3,
            category=category
        )
        
        # Get similar historical cases
        similar_cases = self.rag_kb.get_similar_cases(
            complaint_text=complaint_text,
            category=category,
            top_k=2
        )
        
        # Generate immediate actions
        immediate_actions = self._generate_immediate_actions(
            complaint_text,
            category,
            priority,
            guidelines
        )
        
        # Generate preventive measures
        preventive_measures = self._generate_preventive_measures(
            category,
            guidelines
        )
        
        # Estimate resolution time
        resolution_time = self._estimate_resolution_time(category, priority)
        
        # Identify responsible department
        responsible_dept = self._get_responsible_department(category)
        
        # Generate sustainability impact assessment
        sustainability_impact = self._assess_sustainability_impact(category, priority)
        
        return {
            'immediate_actions': immediate_actions,
            'preventive_measures': preventive_measures,
            'resolution_time': resolution_time,
            'responsible_department': responsible_dept,
            'relevant_guidelines': [
                {
                    'title': g['metadata'].get('title', ''),
                    'content': g['content'],
                    'source': g['metadata'].get('source', '')
                }
                for g in guidelines
            ],
            'similar_cases': [
                {
                    'content': c['content'],
                    'location': c['metadata'].get('location', '')
                }
                for c in similar_cases
            ],
            'sustainability_impact': sustainability_impact,
            'priority_justification': self._get_priority_justification(priority)
        }
    
    def _generate_immediate_actions(self, complaint_text: str, category: str,
                                   priority: str, guidelines: List[Dict]) -> List[str]:
        """Generate immediate action items"""
        actions = []
        text_lower = complaint_text.lower()
        
        if category == 'Water':
            if 'no water' in text_lower or 'supply' in text_lower:
                actions.append("Inspect water supply line immediately")
                actions.append("Check overhead tank level")
                if priority == 'High':
                    actions.append("Deploy water tanker immediately")
                actions.append("Inform hostel residents about the update")
            elif 'contamination' in text_lower:
                actions.append("Stop water supply to affected area")
                actions.append("Conduct water quality test")
                actions.append("Arrange alternative safe water source")
                actions.append("Notify all users in the area")
            elif 'leakage' in text_lower or 'leak' in text_lower:
                actions.append("Locate and isolate the leakage point")
                actions.append("Deploy repair team")
                actions.append("Monitor water pressure in the area")
            elif 'purifier' in text_lower:
                actions.append("Arrange alternative drinking water source")
                actions.append("Call purifier maintenance team")
                actions.append("Replace or repair within 24 hours")
        
        elif category == 'Electricity':
            if 'sparks' in text_lower or 'electrical sparks' in text_lower:
                actions.append("EVACUATE AREA IMMEDIATELY")
                actions.append("Cut power supply to affected section")
                actions.append("Call emergency electrical team")
                actions.append("Do not allow entry until cleared by electrician")
            elif 'generator' in text_lower:
                actions.append("Check generator fuel levels")
                actions.append("Inspect electrical connections")
                actions.append("Activate backup generator if available")
                actions.append("Call maintenance team")
            elif 'power cut' in text_lower or 'no power' in text_lower:
                actions.append("Check main circuit breaker")
                actions.append("Inspect transformer status")
                actions.append("Coordinate with electricity board if needed")
            elif 'fluctuation' in text_lower:
                actions.append("Check voltage stabilizer")
                actions.append("Protect sensitive equipment with UPS")
                actions.append("Conduct load balancing assessment")
        
        elif category == 'Transportation':
            if 'breakdown' in text_lower:
                actions.append("Deploy replacement bus immediately")
                actions.append("Inform affected students via SMS/app")
                actions.append("Arrange vehicle recovery")
            elif 'overcrowded' in text_lower or 'overcrowding' in text_lower:
                actions.append("Add additional bus on this route")
                actions.append("Monitor passenger count")
                actions.append("Adjust bus frequency during peak hours")
            elif 'delayed' in text_lower or 'delay' in text_lower:
                actions.append("Investigate cause of delay")
                actions.append("Inform students about revised timing")
                actions.append("Optimize route if needed")
            elif 'traffic' in text_lower:
                actions.append("Implement staggered timing")
                actions.append("Deploy traffic management personnel")
                actions.append("Consider alternative routes")
        
        # Add actions from guidelines if available
        for guideline in guidelines[:2]:
            content = guideline['content']
            if 'arrange' in content.lower() or 'deploy' in content.lower():
                # Extract action-oriented sentences
                sentences = content.split('.')
                for sentence in sentences[:2]:
                    if len(sentence.strip()) > 10 and sentence.strip() not in actions:
                        actions.append(sentence.strip())
        
        # Ensure we have at least some actions
        if not actions:
            actions.append(f"Investigate {category.lower()} issue immediately")
            actions.append("Deploy appropriate technical team")
            actions.append("Keep affected users informed")
        
        return actions[:6]  # Limit to 6 actions
    
    def _generate_preventive_measures(self, category: str, 
                                     guidelines: List[Dict]) -> List[str]:
        """Generate preventive measures"""
        measures = {
            'Water': [
                "Conduct monthly pipeline inspection",
                "Regular water quality testing",
                "Maintain adequate water storage capacity",
                "Install water level monitoring sensors",
                "Promote water conservation awareness"
            ],
            'Electricity': [
                "Quarterly electrical safety audits",
                "Regular generator maintenance every 2 weeks",
                "Install voltage stabilizers for sensitive equipment",
                "Implement automatic power management systems",
                "Conduct energy conservation workshops"
            ],
            'Transportation': [
                "Bi-weekly vehicle maintenance checks",
                "Maintain pool of backup buses",
                "GPS tracking for real-time monitoring",
                "Regular driver training programs",
                "Collect and analyze student feedback quarterly"
            ]
        }
        
        return measures.get(category, ["Regular maintenance and monitoring"])
    
    def _estimate_resolution_time(self, category: str, priority: str) -> str:
        """Estimate resolution time based on category and priority"""
        time_matrix = {
            'Water': {
                'High': '2-4 hours',
                'Medium': '4-8 hours',
                'Low': '1-2 days'
            },
            'Electricity': {
                'High': '1-3 hours',
                'Medium': '3-6 hours',
                'Low': '6-24 hours'
            },
            'Transportation': {
                'High': '30 minutes - 2 hours',
                'Medium': '2-4 hours',
                'Low': '4-8 hours'
            }
        }
        
        return time_matrix.get(category, {}).get(priority, '4-8 hours')
    
    def _get_responsible_department(self, category: str) -> Dict:
        """Get responsible department information"""
        departments = {
            'Water': {
                'name': 'Facilities Management - Water Division',
                'contact': 'water@campus.edu',
                'emergency_contact': '+91-XXX-WATER-HELP'
            },
            'Electricity': {
                'name': 'Facilities Management - Electrical Division',
                'contact': 'electrical@campus.edu',
                'emergency_contact': '+91-XXX-POWER-HELP'
            },
            'Transportation': {
                'name': 'Transportation Services',
                'contact': 'transport@campus.edu',
                'emergency_contact': '+91-XXX-TRANS-HELP'
            }
        }
        
        return departments.get(category, {
            'name': 'General Facilities',
            'contact': 'facilities@campus.edu',
            'emergency_contact': '+91-XXX-HELP-DESK'
        })
    
    def _assess_sustainability_impact(self, category: str, priority: str) -> Dict:
        """Assess sustainability impact of the complaint"""
        impact_data = {
            'Water': {
                'sdg_goals': [6, 12],  # Clean Water, Responsible Consumption
                'environmental_impact': 'High',
                'resource_waste': 'Water wastage affects conservation goals',
                'carbon_footprint': 'Low',
                'recommendations': [
                    'Fix leaks to prevent water wastage',
                    'Implement water recycling where possible',
                    'Monitor water consumption patterns'
                ]
            },
            'Electricity': {
                'sdg_goals': [7, 12, 13],  # Clean Energy, Responsible Consumption, Climate Action
                'environmental_impact': 'High',
                'resource_waste': 'Energy wastage increases carbon footprint',
                'carbon_footprint': 'High',
                'recommendations': [
                    'Optimize energy usage',
                    'Use renewable energy sources where possible',
                    'Implement smart energy management systems'
                ]
            },
            'Transportation': {
                'sdg_goals': [11, 12],  # Sustainable Cities, Responsible Consumption
                'environmental_impact': 'Medium',
                'resource_waste': 'Fuel consumption and emissions',
                'carbon_footprint': 'Medium',
                'recommendations': [
                    'Optimize bus routes for fuel efficiency',
                    'Consider electric or hybrid buses',
                    'Promote carpooling and cycling'
                ]
            }
        }
        
        impact = impact_data.get(category, {})
        impact['priority_impact'] = f"{priority} priority issues require immediate attention to minimize environmental impact"
        
        return impact
    
    def _get_priority_justification(self, priority: str) -> str:
        """Get justification for priority level"""
        justifications = {
            'High': 'Requires immediate attention due to safety concerns, large number of affected users, or critical infrastructure impact',
            'Medium': 'Significant issue requiring prompt resolution to maintain normal campus operations',
            'Low': 'Minor issue that can be addressed during regular maintenance schedule'
        }
        
        return justifications.get(priority, 'Standard priority based on assessment')

# Made with Bob
