"""
IBM Granite AI Classifier Module
Uses IBM watsonx.ai Granite LLM for intelligent complaint classification
"""

try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    Model = None
    GenParams = None

import os
from typing import Dict, List
import json
import re

class GraniteClassifier:
    """Classifies complaints using IBM Granite LLM"""
    
    def __init__(self):
        """Initialize IBM Granite model"""
        self.model = None
        self.categories = ['Water', 'Electricity', 'Transportation']
        self.urgency_levels = ['Low', 'Medium', 'High']
        
        # Initialize model if credentials are available
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize IBM watsonx.ai Granite model"""
        if not WATSONX_AVAILABLE:
            print("IBM watsonx.ai not installed. Using rule-based classification.")
            return
            
        try:
            api_key = os.getenv('IBM_WATSONX_API_KEY')
            project_id = os.getenv('IBM_WATSONX_PROJECT_ID')
            url = os.getenv('IBM_WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
            
            if api_key and project_id:
                credentials = {
                    "url": url,
                    "apikey": api_key
                }
                
                # Model parameters
                model_params = {
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 200,
                    GenParams.MIN_NEW_TOKENS: 1,
                    GenParams.TEMPERATURE: 0.1,
                    GenParams.TOP_K: 50,
                    GenParams.TOP_P: 1
                }
                
                # Initialize Granite model
                self.model = Model(
                    model_id="ibm/granite-13b-chat-v2",
                    params=model_params,
                    credentials=credentials,
                    project_id=project_id
                )
                print("[OK] IBM Granite model initialized")
            else:
                print("IBM watsonx credentials not found. Using rule-based classification.")
        except Exception as e:
            print(f"Could not initialize IBM Granite: {e}")
            print("Using rule-based classification fallback.")
    
    def classify_complaint(self, complaint_text: str) -> Dict:
        """
        Classify a complaint using IBM Granite LLM
        
        Args:
            complaint_text: The complaint text to classify
            
        Returns:
            Dictionary with category, urgency, affected_area, and recommended_action
        """
        if self.model:
            return self._classify_with_granite(complaint_text)
        else:
            return self._classify_with_rules(complaint_text)
    
    def _classify_with_granite(self, complaint_text: str) -> Dict:
        """Classify using IBM Granite LLM"""
        try:
            prompt = f"""You are an AI assistant for a campus sustainability management system. Analyze the following student complaint and provide a structured classification.

Complaint: "{complaint_text}"

Classify this complaint into one of these categories: Water, Electricity, or Transportation.
Determine the urgency level: Low, Medium, or High.
Identify the affected area on campus.
Suggest immediate recommended actions.

Provide your response in the following JSON format:
{{
    "category": "Water/Electricity/Transportation",
    "urgency": "Low/Medium/High",
    "affected_area": "specific location",
    "recommended_action": "brief action description",
    "reasoning": "brief explanation"
}}

Response:"""

            # Generate response from Granite
            if self.model is None:
                return self._classify_with_rules(complaint_text)
            
            response = self.model.generate_text(prompt=prompt)
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        'category': result.get('category', 'Water'),
                        'urgency': result.get('urgency', 'Medium'),
                        'affected_area': result.get('affected_area', 'Unknown'),
                        'recommended_action': result.get('recommended_action', 'Investigate issue'),
                        'reasoning': result.get('reasoning', ''),
                        'confidence': 0.9
                    }
            except json.JSONDecodeError:
                pass
            
            # Fallback to rule-based if parsing fails
            return self._classify_with_rules(complaint_text)
            
        except Exception as e:
            print(f"Error in Granite classification: {e}")
            return self._classify_with_rules(complaint_text)
    
    def _classify_with_rules(self, complaint_text: str) -> Dict:
        """Rule-based classification fallback"""
        text_lower = complaint_text.lower()
        
        # Category classification
        category = 'Water'
        if any(word in text_lower for word in ['water', 'leak', 'pipe', 'tank', 'supply', 'purifier', 'contamination', 'tap', 'faucet', 'drain']):
            category = 'Water'
        elif any(word in text_lower for word in ['power', 'electricity', 'light', 'generator', 'ac', 'electrical', 'sparks', 'cut', 'fan', 'bulb', 'switch', 'socket', 'wiring', 'voltage', 'blackout', 'outage', 'appliance', 'heater', 'cooler']):
            category = 'Electricity'
        elif any(word in text_lower for word in ['bus', 'transport', 'traffic', 'route', 'driver', 'vehicle', 'overcrowded', 'shuttle', 'auto', 'rickshaw']):
            category = 'Transportation'
        
        # Urgency classification
        urgency = 'Medium'
        if any(word in text_lower for word in ['emergency', 'urgent', 'critical', 'danger', 'sparks', 'contamination', 'no water', 'no power']):
            urgency = 'High'
        elif any(word in text_lower for word in ['minor', 'slight', 'small', 'delayed']):
            urgency = 'Low'
        
        # Extract location
        affected_area = 'Campus'
        location_keywords = ['hostel', 'block', 'cafeteria', 'library', 'lab', 'gate', 'route', 'mess', 'admin']
        for keyword in location_keywords:
            if keyword in text_lower:
                # Find the phrase containing the keyword
                words = complaint_text.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        affected_area = ' '.join(words[max(0, i-1):min(len(words), i+2)])
                        break
                break
        
        # Recommended action based on category
        actions = {
            'Water': 'Inspect water supply line and check overhead tank level',
            'Electricity': 'Check electrical infrastructure and ensure backup power availability',
            'Transportation': 'Add additional bus during peak hours and optimize routes'
        }
        
        return {
            'category': category,
            'urgency': urgency,
            'affected_area': affected_area,
            'recommended_action': actions.get(category, 'Investigate and resolve issue'),
            'reasoning': f'Rule-based classification based on keywords in complaint',
            'confidence': 0.7
        }
    
    def batch_classify(self, complaints: List[str]) -> List[Dict]:
        """
        Classify multiple complaints at once
        
        Args:
            complaints: List of complaint texts
            
        Returns:
            List of classification results
        """
        results = []
        for complaint in complaints:
            results.append(self.classify_complaint(complaint))
        return results
    
    def get_category_insights(self, complaint_text: str) -> Dict:
        """
        Get detailed insights about a complaint category
        
        Args:
            complaint_text: The complaint text
            
        Returns:
            Dictionary with detailed category insights
        """
        classification = self.classify_complaint(complaint_text)
        
        # Category-specific insights
        insights = {
            'Water': {
                'common_causes': ['Pipeline damage', 'Tank overflow', 'Supply disruption', 'Purifier malfunction'],
                'typical_resolution_time': '2-4 hours',
                'responsible_department': 'Facilities Management - Water Division',
                'sustainability_impact': 'High - affects water conservation goals'
            },
            'Electricity': {
                'common_causes': ['Generator failure', 'Power fluctuation', 'Equipment malfunction', 'Overload'],
                'typical_resolution_time': '1-3 hours',
                'responsible_department': 'Facilities Management - Electrical Division',
                'sustainability_impact': 'High - affects energy efficiency targets'
            },
            'Transportation': {
                'common_causes': ['Bus breakdown', 'Route congestion', 'Driver shortage', 'Overcrowding'],
                'typical_resolution_time': '30 minutes - 2 hours',
                'responsible_department': 'Transportation Services',
                'sustainability_impact': 'Medium - affects carbon footprint reduction'
            }
        }
        
        category = classification['category']
        return {
            'classification': classification,
            'insights': insights.get(category, {}),
            'sdg_alignment': self._get_sdg_alignment(category)
        }
    
    def _get_sdg_alignment(self, category: str) -> List[Dict]:
        """Get UN Sustainable Development Goals alignment"""
        sdg_mapping = {
            'Water': [
                {'goal': 6, 'name': 'Clean Water and Sanitation', 'relevance': 'High'},
                {'goal': 12, 'name': 'Responsible Consumption and Production', 'relevance': 'Medium'}
            ],
            'Electricity': [
                {'goal': 7, 'name': 'Affordable and Clean Energy', 'relevance': 'High'},
                {'goal': 12, 'name': 'Responsible Consumption and Production', 'relevance': 'High'}
            ],
            'Transportation': [
                {'goal': 11, 'name': 'Sustainable Cities and Communities', 'relevance': 'High'},
                {'goal': 12, 'name': 'Responsible Consumption and Production', 'relevance': 'Medium'}
            ]
        }
        return sdg_mapping.get(category, [])

# Made with Bob
