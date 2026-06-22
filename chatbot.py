"""
Campus Sustainability AI Chatbot
Provides intelligent responses to user questions using RAG knowledge base
"""

import os
from typing import Dict, List, Optional
try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    print("[INFO] IBM watsonx.ai not available. Using knowledge base only.")


class SustainabilityChatbot:
    """AI-powered chatbot for campus sustainability questions"""
    
    def __init__(self, knowledge_base):
        """
        Initialize chatbot with RAG knowledge base
        
        Args:
            knowledge_base: RAGKnowledgeBase instance
        """
        self.knowledge_base = knowledge_base
        self.model = None
        self.conversation_history = []
        
        # Initialize IBM Granite if available
        if WATSONX_AVAILABLE:
            self._initialize_granite()
        
        # Predefined responses for common questions
        self.quick_responses = {
            'hello': 'Hello! I\'m your Campus Sustainability AI Assistant. I can help you with questions about water management, electricity usage, transportation, and campus sustainability policies. How can I assist you today?',
            'hi': 'Hi there! I\'m here to help with campus sustainability questions. What would you like to know?',
            'hey': 'Hey! I\'m your Campus Sustainability AI Assistant. How can I help you today?',
            'how are you': 'I\'m doing great, thank you for asking! I\'m here and ready to help you with any campus sustainability questions. What would you like to know?',
            'how r u': 'I\'m doing great, thanks! I\'m here to help you with campus sustainability questions. What can I assist you with?',
            'how are u': 'I\'m doing well, thank you! I\'m here to help with campus sustainability questions. How can I assist you today?',
            'whats up': 'Hello! I\'m here to help with campus sustainability questions. What would you like to know?',
            'help': 'I can help you with:\n• Water conservation and management\n• Electricity and energy efficiency\n• Campus transportation options\n• Sustainability policies and guidelines\n• Complaint resolution processes\n\nJust ask me any question!',
            'thanks': 'You\'re welcome! Feel free to ask if you have more questions.',
            'thank you': 'You\'re welcome! I\'m here to help anytime.',
            'bye': 'Goodbye! Feel free to come back anytime you have questions about campus sustainability.',
            'goodbye': 'Goodbye! Have a great day, and don\'t hesitate to reach out if you need help with sustainability matters.',
        }
    
    def _initialize_granite(self):
        """Initialize IBM Granite model"""
        try:
            api_key = os.getenv('WATSONX_API_KEY')
            project_id = os.getenv('WATSONX_PROJECT_ID')
            
            if api_key and project_id:
                parameters = {
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 300,
                    GenParams.MIN_NEW_TOKENS: 1,
                    GenParams.TEMPERATURE: 0.7,
                    GenParams.TOP_K: 50,
                    GenParams.TOP_P: 1
                }
                
                self.model = Model(
                    model_id="ibm/granite-13b-chat-v2",
                    params=parameters,
                    credentials={
                        "apikey": api_key,
                        "url": "https://us-south.ml.cloud.ibm.com"
                    },
                    project_id=project_id
                )
                print("[OK] IBM Granite chatbot initialized")
            else:
                print("[INFO] IBM Granite credentials not found. Using knowledge base only.")
        except Exception as e:
            print(f"[INFO] Could not initialize IBM Granite: {e}")
            self.model = None
    
    def get_response(self, user_question: str, user_id: Optional[int] = None) -> Dict:
        """
        Get chatbot response to user question with enhanced conversational AI
        
        Args:
            user_question: User's question
            user_id: Optional user ID for personalization
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Clean and normalize question
            question = user_question.strip().lower()
            
            # Check for quick responses (greetings, thanks, etc.)
            for key, response in self.quick_responses.items():
                if key in question:
                    return {
                        'success': True,
                        'response': response,
                        'source': 'quick_response',
                        'confidence': 1.0
                    }
            
            # Try to use IBM Granite model for general conversation if available
            if self.model:
                try:
                    granite_response = self._get_granite_response(user_question)
                    if granite_response:
                        # Store in conversation history
                        self.conversation_history.append({
                            'question': user_question,
                            'response': granite_response,
                            'user_id': user_id
                        })
                        return {
                            'success': True,
                            'response': granite_response,
                            'source': 'granite_ai',
                            'confidence': 0.9
                        }
                except Exception as e:
                    print(f"[INFO] Granite model unavailable, using knowledge base: {e}")
            
            # Search knowledge base for relevant information
            kb_results = self.knowledge_base.search(user_question, top_k=5)
            
            # Check if we have good results (distance < 1.0 means good match in ChromaDB)
            has_good_results = kb_results and len(kb_results) > 0
            if has_good_results and kb_results[0].get('distance') is not None:
                # Lower distance = better match. Reject if distance > 1.5
                has_good_results = kb_results[0].get('distance', 999) < 1.5
            
            # If no relevant results, try general question handling
            if not has_good_results:
                general_response = self._handle_general_question(question)
                if general_response:
                    return {
                        'success': True,
                        'response': general_response,
                        'source': 'general_ai',
                        'confidence': 0.7
                    }
                return {
                    'success': True,
                    'response': self._get_fallback_response(question),
                    'source': 'fallback',
                    'confidence': 0.5
                }
            
            # Generate intelligent response from knowledge base
            response = self._generate_intelligent_response(user_question, kb_results)
            
            # Store in conversation history
            self.conversation_history.append({
                'question': user_question,
                'response': response['response'],
                'user_id': user_id
            })
            
            return response
            
        except Exception as e:
            print(f"[ERROR] Chatbot error: {e}")
            return {
                'success': False,
                'response': 'I apologize, but I encountered an error processing your question. Please try again or rephrase your question.',
                'error': str(e)
            }
    
    def _get_granite_response(self, question: str) -> Optional[str]:
        """Get response from IBM Granite model for general conversation"""
        try:
            if not self.model:
                return None
            
            # Build context-aware prompt
            context = ""
            if self.conversation_history:
                recent = self.conversation_history[-3:]  # Last 3 exchanges
                context = "\n".join([f"User: {h['question']}\nAssistant: {h['response']}" for h in recent])
            
            prompt = f"""You are a helpful and friendly AI assistant for a campus sustainability system.
You can answer general questions and have natural conversations, but you specialize in campus sustainability topics like water management, electricity, transportation, and environmental policies.

{context}

User: {question}
Assistant:"""
            
            response = self.model.generate_text(prompt=prompt)
            if response and len(response.strip()) > 0:
                return response.strip()
            return None
        except Exception as e:
            print(f"[INFO] Granite response error: {e}")
            return None
    
    def _handle_general_question(self, question: str) -> Optional[str]:
        """Handle general questions with intelligent responses"""
        
        # Math questions
        if any(word in question for word in ['calculate', 'math', 'add', 'subtract', 'multiply', 'divide', '+', '-', '*', '/']):
            return "I can help with basic calculations! However, for complex math problems, I recommend using a calculator or math-specific tool. Is there anything related to campus sustainability I can help you with?"
        
        # Time/date questions
        if any(word in question for word in ['time', 'date', 'today', 'tomorrow', 'day', 'month', 'year']):
            from datetime import datetime
            now = datetime.now()
            return f"The current date and time is {now.strftime('%B %d, %Y at %I:%M %p')}. How can I assist you with campus sustainability matters today?"
        
        # Weather questions
        if any(word in question for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy']):
            return "I don't have access to real-time weather data, but I can help you understand how weather affects campus sustainability! For example, rainy days are great for water conservation awareness. What would you like to know about sustainability?"
        
        # Personal questions about the AI
        if any(word in question for word in ['who are you', 'what are you', 'your name', 'who made you', 'who created you']):
            return "I'm the Campus Sustainability AI Assistant, designed to help students and staff with sustainability-related questions and complaint management. I can assist with water conservation, energy efficiency, transportation, and environmental policies. How can I help you today?"
        
        # Capability questions
        if any(word in question for word in ['what can you do', 'help me', 'capabilities', 'features']):
            return """I'm here to help you with:

🌊 **Water Management**: Report leaks, get conservation tips, understand water policies
⚡ **Energy Efficiency**: Learn about electricity saving, report power issues
🚌 **Transportation**: Sustainable commuting options, campus shuttle info
📝 **Complaints**: Submit and track sustainability-related complaints
🌱 **General Sustainability**: Campus policies, SDG goals, environmental initiatives

I can also have friendly conversations and answer general questions! What would you like to know?"""
        
        # Jokes or fun
        if any(word in question for word in ['joke', 'funny', 'laugh', 'humor']):
            return "Here's a sustainability joke: Why did the solar panel go to school? To get brighter! 😄 Now, how can I help you with campus sustainability?"
        
        # Compliments
        if any(word in question for word in ['good job', 'well done', 'great', 'awesome', 'amazing', 'excellent']):
            return "Thank you so much! I'm glad I could help. Is there anything else you'd like to know about campus sustainability?"
        
        # Try to provide helpful response for any question
        # Extract key topics from the question
        question_lower = question.lower()
        
        # Check for sustainability-related keywords
        sustainability_keywords = {
            'water': 'water management and conservation',
            'electric': 'electricity and energy efficiency',
            'energy': 'energy conservation and renewable sources',
            'transport': 'sustainable transportation options',
            'bus': 'campus transportation services',
            'waste': 'waste management and recycling',
            'recycle': 'recycling programs',
            'environment': 'environmental sustainability initiatives',
            'green': 'green campus initiatives',
            'sustain': 'sustainability programs',
            'sdg': 'Sustainable Development Goals',
            'complaint': 'complaint submission and tracking',
            'report': 'reporting issues and concerns',
            'issue': 'campus issues and resolution',
            'problem': 'problem reporting and solutions'
        }
        
        # Find matching topics
        matched_topics = [topic for keyword, topic in sustainability_keywords.items() if keyword in question_lower]
        
        if matched_topics:
            topics_str = ', '.join(matched_topics[:3])
            return f"I can help you with {topics_str}! Could you please provide more specific details about what you'd like to know? For example:\n\n• How to report an issue\n• Conservation tips and best practices\n• Campus policies and guidelines\n• Contact information for relevant departments\n\nWhat specific information are you looking for?"
        
        # For completely unrelated questions, provide a helpful redirect
        return "I'm specialized in campus sustainability topics including water, electricity, transportation, waste management, and environmental policies. While I may not have specific information about your question, I'd be happy to help with:\n\n• Reporting campus issues (water leaks, power problems, etc.)\n• Sustainability tips and best practices\n• SDG goals and campus initiatives\n• Complaint tracking and resolution\n• Contact information for campus services\n\nCould you rephrase your question to relate to campus sustainability, or ask about one of these topics?"
    
    def _generate_intelligent_response(self, question: str, kb_results: List[Dict]) -> Dict:
        """Generate intelligent response based on question analysis"""
        try:
            question_lower = question.lower()
            
            # Collect relevant information
            all_info = []
            for result in kb_results[:5]:
                content = result.get('content', result.get('text', ''))
                metadata = result.get('metadata', {})
                all_info.append({'content': content, 'metadata': metadata})
            
            # Analyze question intent and craft response
            response_text = self._craft_smart_response(question, question_lower, all_info)
            
            return {
                'success': True,
                'response': response_text,
                'source': 'knowledge_base',
                'confidence': 0.85,
                'references': [r['metadata'] for r in all_info[:3]]
            }
        except Exception as e:
            print(f"[ERROR] Response generation error: {e}")
            return {
                'success': True,
                'response': self._get_fallback_response(question),
                'source': 'fallback',
                'confidence': 0.5
            }
    
    def _craft_smart_response(self, question: str, question_lower: str, all_info: List[Dict]) -> str:
        """Craft intelligent, context-aware response"""
        
        # Identify question type and topic
        is_howto = any(word in question_lower for word in ['how', 'how to', 'steps', 'process', 'procedure'])
        is_what = 'what' in question_lower
        is_why = 'why' in question_lower
        is_when = 'when' in question_lower
        
        # Identify topic
        is_water = any(word in question_lower for word in ['water', 'leak', 'pipe', 'tap', 'drinking'])
        is_electricity = any(word in question_lower for word in ['electric', 'power', 'light', 'ac', 'energy'])
        is_transport = any(word in question_lower for word in ['bus', 'transport', 'vehicle', 'traffic'])
        is_report = any(word in question_lower for word in ['report', 'submit', 'complaint'])
        is_tips = any(word in question_lower for word in ['tip', 'save', 'conserve', 'reduce', 'help'])
        
        # Build response based on intent
        if is_howto and is_report:
            return self._build_report_guide(all_info, is_water, is_electricity, is_transport)
        elif is_tips or (is_howto and any([is_water, is_electricity, is_transport])):
            return self._build_tips_response(all_info, is_water, is_electricity, is_transport)
        elif is_what:
            return self._build_what_response(all_info, question_lower)
        elif is_why:
            return self._build_why_response(all_info)
        elif is_when:
            return self._build_when_response(all_info)
        else:
            return self._build_general_response(all_info)
    
    def _build_report_guide(self, all_info: List[Dict], is_water: bool, is_electricity: bool, is_transport: bool) -> str:
        """Build guide for reporting issues"""
        response = "📝 **How to Report an Issue:**\n\n"
        
        if is_water:
            response += "**For Water Issues:**\n"
            response += "1. Note the exact location and severity\n"
            response += "2. Take photos if possible\n"
            response += "3. Report immediately to maintenance (ext. 2345)\n"
            response += "4. Submit online complaint for tracking\n"
            response += "5. Expected response: Within 2-4 hours\n\n"
        elif is_electricity:
            response += "**For Electrical Issues:**\n"
            response += "1. Ensure safety - evacuate if dangerous\n"
            response += "2. Do NOT attempt repairs yourself\n"
            response += "3. Call electrical maintenance (ext. 3456)\n"
            response += "4. Provide location and issue description\n"
            response += "5. Expected response: Immediate for emergencies\n\n"
        elif is_transport:
            response += "**For Transportation Issues:**\n"
            response += "1. Note route number and time\n"
            response += "2. Contact transport office (ext. 4567)\n"
            response += "3. Check for alternative arrangements\n"
            response += "4. Submit feedback for improvements\n"
            response += "5. Expected response: Same day\n\n"
        else:
            response += "**General Reporting Process:**\n"
            response += "1. Identify the issue category\n"
            response += "2. Gather relevant details (location, time, severity)\n"
            response += "3. Contact appropriate department\n"
            response += "4. Submit online complaint for tracking\n"
            response += "5. Follow up if needed\n\n"
        
        # Add knowledge base info
        if all_info:
            response += f"📚 **From Campus Guidelines:**\n{all_info[0]['content'][:300]}...\n"
        
        return response
    
    def _build_tips_response(self, all_info: List[Dict], is_water: bool, is_electricity: bool, is_transport: bool) -> str:
        """Build tips and conservation advice"""
        response = "💡 **Helpful Tips:**\n\n"
        
        if is_water:
            response += "**💧 Water Conservation:**\n"
            response += "• Fix leaks immediately - even small drips waste gallons\n"
            response += "• Use water-efficient fixtures and appliances\n"
            response += "• Report wastage when you see it\n"
            response += "• Avoid leaving taps running unnecessarily\n"
            response += "• Reuse water where possible (e.g., for plants)\n\n"
        
        if is_electricity:
            response += "**⚡ Energy Saving:**\n"
            response += "• Turn off lights when leaving rooms\n"
            response += "• Use natural light during daytime\n"
            response += "• Set AC to 24°C for optimal efficiency\n"
            response += "• Unplug devices when not in use\n"
            response += "• Use energy-efficient LED bulbs\n\n"
        
        if is_transport:
            response += "**🚌 Sustainable Transportation:**\n"
            response += "• Use campus shuttle services regularly\n"
            response += "• Carpool with classmates and colleagues\n"
            response += "• Walk or cycle for short distances\n"
            response += "• Plan trips to reduce frequency\n"
            response += "• Use public transport when possible\n\n"
        
        # Add knowledge base insights
        if all_info:
            response += f"📖 **Campus Policy:**\n{all_info[0]['content']}\n"
        
        return response
    
    def _build_what_response(self, all_info: List[Dict], question_lower: str) -> str:
        """Build response for 'what' questions"""
        response = "ℹ️ **Here's what you need to know:**\n\n"
        
        if all_info:
            response += f"{all_info[0]['content']}\n\n"
            
            if len(all_info) > 1:
                response += "**Additional Information:**\n"
                for i, info in enumerate(all_info[1:3], 1):
                    response += f"{i}. {info['content'][:200]}...\n"
        
        return response
    
    def _build_why_response(self, all_info: List[Dict]) -> str:
        """Build explanation response"""
        response = "🤔 **Let me explain:**\n\n"
        
        if all_info:
            response += f"{all_info[0]['content']}\n\n"
        
        response += "**Why this matters:**\n"
        response += "• Supports campus sustainability goals (SDGs 6, 11, 12)\n"
        response += "• Improves quality of life for students and staff\n"
        response += "• Prevents larger problems through early action\n"
        response += "• Reduces environmental impact and costs\n"
        
        return response
    
    def _build_when_response(self, all_info: List[Dict]) -> str:
        """Build timing-related response"""
        response = "⏰ **Timing Information:**\n\n"
        
        # Extract timing from knowledge base
        for info in all_info:
            content = info['content']
            if any(word in content.lower() for word in ['hour', 'day', 'time', 'immediate', 'within']):
                response += f"{content}\n\n"
                break
        
        response += "**General Response Times:**\n"
        response += "• 🚨 Emergency: Immediate (< 1 hour)\n"
        response += "• 🔴 High Priority: Within 24 hours\n"
        response += "• 🟡 Medium Priority: 2-3 days\n"
        response += "• 🟢 Low Priority: Within a week\n"
        
        return response
    
    def _build_general_response(self, all_info: List[Dict]) -> str:
        """Build general informational response"""
        if not all_info:
            return "I don't have specific information about that. Could you rephrase or ask about water, electricity, or transportation?"
        
        response = "📋 **Based on campus information:**\n\n"
        response += f"{all_info[0]['content']}\n\n"
        
        if len(all_info) > 1:
            response += "**Related Topics:**\n"
            for i, info in enumerate(all_info[1:3], 1):
                response += f"{i}. {info['content'][:150]}...\n"
        
        response += "\n💬 **Need more help?**\n"
        response += "• Submit a detailed complaint\n"
        response += "• Contact the sustainability office\n"
        response += "• Check campus guidelines portal\n"
        
        return response
    
    def _get_fallback_response(self, question: str) -> str:
        """Get fallback response when no relevant information found"""
        question_lower = question.lower()
        
        # Provide context-aware fallback based on question content
        if 'water' in question_lower:
            return """I can help you with water-related topics! Here's what I know about:

**💧 Water Issues I Can Help With:**
• How to report water leaks, contamination, or supply problems
• Water conservation tips and best practices
• Campus water management policies and guidelines
• Contact information: Facilities Management (ext. 2345)

**Try asking:**
• "How do I report a water leak?"
• "What are water conservation tips?"
• "Who handles water issues?"

Or describe your specific water concern, and I'll do my best to help!"""
        
        elif any(word in question_lower for word in ['electric', 'energy', 'power', 'light']):
            return """I can help you with electricity and energy topics! Here's what I know about:

**⚡ Electricity Issues I Can Help With:**
• Reporting power outages, electrical hazards, or equipment problems
• Energy saving tips and efficiency guidelines
• Campus energy policies and initiatives
• Contact information: Electrical Maintenance (ext. 3456)

**Try asking:**
• "How do I report an electrical issue?"
• "What are energy saving tips?"
• "Who handles power problems?"

Or describe your specific electricity concern, and I'll assist you!"""
        
        elif any(word in question_lower for word in ['transport', 'bus', 'parking', 'vehicle', 'traffic']):
            return """I can help you with transportation topics! Here's what I know about:

**🚌 Transportation Issues I Can Help With:**
• Campus bus schedules and routes
• Reporting transportation problems or delays
• Sustainable commuting options
• Contact information: Transport Office (ext. 4567)

**Try asking:**
• "What are sustainable transportation options?"
• "How do I report a bus issue?"
• "Who handles transportation?"

Or describe your specific transportation concern!"""
        
        elif any(word in question_lower for word in ['sdg', 'sustainability', 'environment', 'green']):
            return """I can help you with sustainability topics! Here's what I know about:

**🌱 Sustainability Topics I Can Help With:**
• SDG 6, 11, and 12 goals and campus initiatives
• Environmental policies and programs
• Green campus initiatives
• How to participate in sustainability efforts

**Try asking:**
• "What is SDG 6/11/12?"
• "What are campus sustainability initiatives?"
• "How can I contribute to sustainability?"

What specific sustainability topic interests you?"""
        
        elif any(word in question_lower for word in ['complaint', 'report', 'issue', 'problem']):
            return """I can help you with reporting and complaint management! Here's what I know:

**📝 Complaint & Reporting Help:**
• Step-by-step guide to submit complaints
• How to track your complaint status
• Resolution timelines and processes
• Contact information for all departments

**Try asking:**
• "How do I submit a complaint?"
• "How can I track my complaint?"
• "How long does resolution take?"

What would you like to know about the complaint process?"""
        
        else:
            return """I'm your Campus Sustainability AI Assistant! While I don't have specific information about that question, I can help you with:

**🌊 Water** - Leaks, conservation, policies
**⚡ Energy** - Power issues, efficiency tips
**🚌 Transportation** - Bus services, sustainable commuting
**🌱 Sustainability** - SDG goals, green initiatives
**📝 Complaints** - Reporting, tracking, resolution

**Popular Questions:**
• "How do I report a water leak?"
• "What are energy saving tips?"
• "What is SDG 6?"
• "How do I submit a complaint?"

Could you rephrase your question to relate to one of these topics, or ask something specific about campus sustainability?"""
    
    def get_suggestions(self, partial_question: str) -> List[str]:
        """Get question suggestions based on partial input"""
        suggestions = []
        partial_lower = partial_question.lower()
        
        templates = {
            'water': [
                "How can I report a water leak?",
                "What are the water conservation guidelines?",
                "How do I reduce water usage?",
                "What should I do if I see water wastage?"
            ],
            'electric': [
                "How can I save electricity on campus?",
                "What are the energy efficiency guidelines?",
                "How do I report an electrical issue?",
                "What are power-saving tips?"
            ],
            'transport': [
                "What are the sustainable transportation options?",
                "How can I reduce my carbon footprint?",
                "What are the campus shuttle timings?",
                "How do I report transportation issues?"
            ],
            'complaint': [
                "How do I submit a complaint?",
                "What happens after I submit a complaint?",
                "How long does complaint resolution take?",
                "Can I track my complaint status?"
            ]
        }
        
        for category, questions in templates.items():
            if category in partial_lower:
                suggestions.extend(questions[:3])
        
        if not suggestions:
            suggestions = [
                "How can I contribute to campus sustainability?",
                "What are the main sustainability initiatives?",
                "How do I report a sustainability issue?",
                "What resources are available for sustainable living?"
            ]
        
        return suggestions[:5]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self, user_id: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        if user_id:
            return [e for e in self.conversation_history if e.get('user_id') == user_id]
        return self.conversation_history

# Made with Bob
