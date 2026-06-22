"""
RAG (Retrieval-Augmented Generation) Knowledge Base Module
Stores and retrieves campus policies, guidelines, and best practices
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os

class RAGKnowledgeBase:
    """Manages RAG knowledge base for complaint resolution"""
    
    def __init__(self):
        """Initialize RAG knowledge base with ChromaDB and embeddings"""
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB with new API
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection("campus_knowledge")
            print("[OK] Loaded existing knowledge base")
        except:
            self.collection = self.chroma_client.create_collection(
                name="campus_knowledge",
                metadata={"description": "Campus sustainability policies and guidelines"}
            )
            self._initialize_knowledge_base()
            print("[OK] Created new knowledge base")
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base with campus policies and guidelines"""
        
        # Water Management Guidelines
        water_guidelines = [
            {
                "id": "water_001",
                "category": "Water",
                "title": "Water Supply Disruption Protocol",
                "content": "If water supply is disrupted for more than 12 hours, arrange tanker water immediately. Check overhead tank levels and inspect pipeline for damage. Notify hostel residents about the update.",
                "source": "Water Management Policy 2026"
            },
            {
                "id": "water_002",
                "category": "Water",
                "title": "Water Contamination Response",
                "content": "Water contamination reports require immediate action. Stop water supply to affected area, test water quality, arrange alternative safe water source, and inform all users. Resolution time: 2-4 hours.",
                "source": "Health & Safety Guidelines"
            },
            {
                "id": "water_003",
                "category": "Water",
                "title": "Pipeline Maintenance",
                "content": "Pipeline damage should be inspected within 1 hour. Deploy tanker if required. Regular maintenance checks should be conducted monthly to prevent leakage and ensure water conservation.",
                "source": "Facilities Maintenance Manual"
            },
            {
                "id": "water_004",
                "category": "Water",
                "title": "Water Purifier Maintenance",
                "content": "Broken water purifiers should be repaired or replaced within 24 hours. Arrange alternative drinking water source immediately. Regular filter replacement every 3 months is mandatory.",
                "source": "Equipment Maintenance Policy"
            }
        ]
        
        # Electricity Management Guidelines
        electricity_guidelines = [
            {
                "id": "elec_001",
                "category": "Electricity",
                "title": "Generator Failure Protocol",
                "content": "Generator failure requires immediate attention. Check fuel levels, inspect electrical connections, and call maintenance team. Backup generator should be activated within 30 minutes. Critical areas like hospitals and labs get priority.",
                "source": "Electrical Safety Manual"
            },
            {
                "id": "elec_002",
                "category": "Electricity",
                "title": "Electrical Sparks Emergency",
                "content": "Electrical sparks indicate serious hazard. Evacuate area immediately, cut power supply to affected section, and call emergency electrical team. Do not attempt repairs without qualified electrician. Resolution time: 1-2 hours.",
                "source": "Emergency Response Protocol"
            },
            {
                "id": "elec_003",
                "category": "Electricity",
                "title": "Power Fluctuation Management",
                "content": "Power fluctuation affecting equipment requires voltage stabilizer check and load balancing. Protect sensitive equipment by using UPS systems. Regular electrical audits should be conducted quarterly.",
                "source": "Energy Management Policy"
            },
            {
                "id": "elec_004",
                "category": "Electricity",
                "title": "Street Lights Maintenance",
                "content": "Non-functional street lights should be reported and fixed within 24 hours for safety. Use LED lights for energy efficiency. Regular inspection of all outdoor lighting every month.",
                "source": "Campus Safety Guidelines"
            },
            {
                "id": "elec_005",
                "category": "Electricity",
                "title": "Energy Conservation",
                "content": "AC and lights left running after hours waste energy. Implement automatic timers and motion sensors. Conduct awareness programs for students and staff about energy conservation.",
                "source": "Sustainability Action Plan"
            }
        ]
        
        # Transportation Guidelines
        transport_guidelines = [
            {
                "id": "trans_001",
                "category": "Transportation",
                "title": "Bus Breakdown Response",
                "content": "Bus breakdown requires immediate replacement bus deployment. Inform affected students via SMS/app. Maintain backup buses for emergencies. Regular vehicle maintenance every 2 weeks is mandatory.",
                "source": "Transportation Services Manual"
            },
            {
                "id": "trans_002",
                "category": "Transportation",
                "title": "Overcrowding Management",
                "content": "Bus overcrowding during peak hours requires additional buses on that route. Monitor passenger count and adjust frequency. Maximum capacity should not exceed safety limits. Add buses during exam periods.",
                "source": "Transport Safety Policy"
            },
            {
                "id": "trans_003",
                "category": "Transportation",
                "title": "Route Optimization",
                "content": "Route coverage issues should be reviewed monthly. Analyze student residence patterns and adjust routes accordingly. Use GPS tracking for real-time monitoring. Collect student feedback quarterly.",
                "source": "Route Planning Guidelines"
            },
            {
                "id": "trans_004",
                "category": "Transportation",
                "title": "Traffic Congestion Solutions",
                "content": "Traffic congestion at entrance requires staggered timing for different departments. Implement one-way systems during peak hours. Encourage carpooling and cycling for sustainability.",
                "source": "Campus Traffic Management"
            },
            {
                "id": "trans_005",
                "category": "Transportation",
                "title": "Driver Management",
                "content": "Driver shortage causing delays requires maintaining pool of backup drivers. Provide proper training and ensure adequate rest periods. Monitor driver performance and safety records.",
                "source": "HR & Operations Manual"
            }
        ]
        
        # SDG (Sustainable Development Goals) Information
        sdg_guidelines = [
            {
                "id": "sdg_001",
                "category": "SDG",
                "title": "SDG 6: Clean Water and Sanitation",
                "content": "SDG 6 ensures availability and sustainable management of water and sanitation for all. Our campus focuses on: reducing water wastage, fixing leaks promptly, ensuring clean drinking water, implementing rainwater harvesting, and monitoring water quality regularly. Target: Reduce water consumption by 20% by 2030.",
                "source": "UN Sustainable Development Goals"
            },
            {
                "id": "sdg_002",
                "category": "SDG",
                "title": "SDG 11: Sustainable Cities and Communities",
                "content": "SDG 11 aims to make cities inclusive, safe, resilient and sustainable. Campus initiatives include: efficient public transportation, green spaces, waste management, accessible facilities, and reducing environmental impact. We promote walkable campus design and cycling infrastructure.",
                "source": "UN Sustainable Development Goals"
            },
            {
                "id": "sdg_003",
                "category": "SDG",
                "title": "SDG 12: Responsible Consumption and Production",
                "content": "SDG 12 ensures sustainable consumption and production patterns. Campus actions: energy-efficient appliances, renewable energy sources, waste reduction and recycling programs, sustainable procurement policies, and awareness campaigns about responsible resource use.",
                "source": "UN Sustainable Development Goals"
            },
            {
                "id": "sdg_004",
                "category": "SDG",
                "title": "Campus SDG Integration",
                "content": "Our campus integrates SDGs 6, 11, and 12 through: smart water meters, solar panels, electric buses, waste segregation, composting, LED lighting, motion sensors, green buildings, and regular sustainability audits. Students can contribute by reporting issues, conserving resources, and participating in awareness programs.",
                "source": "Campus Sustainability Policy 2026"
            }
        ]
        
        # Complaint Reporting Procedures
        reporting_guidelines = [
            {
                "id": "report_001",
                "category": "Reporting",
                "title": "How to Report a Complaint - Step by Step",
                "content": "To report a complaint: 1) Access the dashboard or chatbot, 2) Click 'Submit Complaint' button, 3) Describe the issue clearly with location details, 4) Estimate users affected, 5) Submit and receive a Complaint ID, 6) Track status using your Complaint ID. You can also report via phone (ext. 2345 for water, 3456 for electricity, 4567 for transport) or email sustainability@campus.edu.",
                "source": "Complaint Management System Guide"
            },
            {
                "id": "report_002",
                "category": "Reporting",
                "title": "What Information to Include in Complaints",
                "content": "When reporting, include: 1) Exact location (building, floor, room number), 2) Detailed description of the issue, 3) When you first noticed it, 4) Severity level (emergency, urgent, normal), 5) Number of people affected, 6) Photos if possible, 7) Your contact information for follow-up. More details help faster resolution.",
                "source": "Complaint Submission Guidelines"
            },
            {
                "id": "report_003",
                "category": "Reporting",
                "title": "Emergency vs Non-Emergency Reporting",
                "content": "EMERGENCY (call immediately): electrical sparks, major water leaks, gas leaks, fire hazards, structural damage. Report to emergency hotline: 100. NON-EMERGENCY (use online system): minor leaks, light bulbs out, AC issues, bus delays, general maintenance. Emergency complaints get immediate response within 1 hour.",
                "source": "Emergency Response Protocol"
            },
            {
                "id": "report_004",
                "category": "Reporting",
                "title": "Anonymous Reporting Option",
                "content": "You can submit complaints anonymously through the system. However, providing contact information helps us: 1) Get more details if needed, 2) Update you on progress, 3) Verify the issue quickly, 4) Close the loop after resolution. Anonymous complaints are treated with equal priority but may take longer to resolve.",
                "source": "Privacy and Reporting Policy"
            }
        ]
        
        # Issue Resolution Procedures
        resolution_guidelines = [
            {
                "id": "resolve_001",
                "category": "Resolution",
                "title": "Complaint Resolution Workflow",
                "content": "Resolution process: 1) Complaint submitted and assigned Complaint ID, 2) AI classifies category and priority (High/Medium/Low), 3) Assigned to relevant department, 4) Status changes to 'In Progress' when work starts, 5) Issue resolved and verified, 6) Status updated to 'Resolved', 7) Feedback requested from reporter. Average resolution time: High priority 2-4 hours, Medium 24-48 hours, Low 3-7 days.",
                "source": "Complaint Resolution SOP"
            },
            {
                "id": "resolve_002",
                "category": "Resolution",
                "title": "Priority Levels Explained",
                "content": "HIGH Priority: Affects 50+ users, safety hazard, critical infrastructure (water/electricity outage), emergency situations. Response: Immediate (within 1 hour). MEDIUM Priority: Affects 10-50 users, significant inconvenience, equipment malfunction. Response: Within 24 hours. LOW Priority: Affects <10 users, minor issues, cosmetic problems. Response: Within 7 days.",
                "source": "Priority Classification System"
            },
            {
                "id": "resolve_003",
                "category": "Resolution",
                "title": "Who Handles What - Department Responsibilities",
                "content": "WATER issues: Facilities Management Team (ext. 2345), handles leaks, supply, quality, purifiers. ELECTRICITY: Electrical Maintenance (ext. 3456), handles power, generators, lights, AC. TRANSPORTATION: Transport Office (ext. 4567), handles buses, routes, drivers, schedules. Each department has 24/7 emergency contact for critical issues.",
                "source": "Department Contact Directory"
            },
            {
                "id": "resolve_004",
                "category": "Resolution",
                "title": "What Happens After You Report",
                "content": "After reporting: 1) Instant confirmation with Complaint ID, 2) AI analyzes and categorizes (within seconds), 3) Email/SMS notification sent to you, 4) Department receives alert, 5) Team inspects issue (within priority timeframe), 6) Work begins and status updated, 7) You receive progress updates, 8) Final resolution notification sent, 9) Feedback form shared. You can track anytime using Complaint ID.",
                "source": "User Communication Protocol"
            },
            {
                "id": "resolve_005",
                "category": "Resolution",
                "title": "Escalation Process",
                "content": "If issue not resolved in expected time: 1) System auto-escalates after deadline, 2) Senior supervisor notified, 3) Additional resources allocated, 4) You receive escalation notification. You can also manually escalate by: calling helpdesk (ext. 1000), emailing complaints@campus.edu, or visiting Admin Block Room 101. Escalated complaints get priority attention.",
                "source": "Escalation and Appeals Policy"
            }
        ]
        
        # Complaint Tracking Information
        tracking_guidelines = [
            {
                "id": "track_001",
                "category": "Tracking",
                "title": "How to Track Your Complaint Status",
                "content": "Track your complaint: 1) Login to dashboard at campus.edu/complaints, 2) Go to 'My Complaints' section, 3) View all your submitted complaints with status, 4) Click on Complaint ID for detailed timeline, 5) See updates, assigned team, expected resolution time. You can also track via chatbot by asking 'What is the status of complaint C0123?' or call helpdesk with your Complaint ID.",
                "source": "Complaint Tracking Guide"
            },
            {
                "id": "track_002",
                "category": "Tracking",
                "title": "Understanding Complaint Status",
                "content": "Status meanings: OPEN - Complaint received, awaiting assignment. IN PROGRESS - Team working on it, issue being resolved. RESOLVED - Issue fixed, awaiting your confirmation. CLOSED - Confirmed resolved by you. ESCALATED - Moved to higher priority due to delay. You receive notifications at each status change via email and SMS.",
                "source": "Status Definitions"
            },
            {
                "id": "track_003",
                "category": "Tracking",
                "title": "Complaint History and Analytics",
                "content": "View your complaint history: See all past complaints, resolution times, categories, feedback given. Campus analytics show: total complaints by category, average resolution times, most common issues, improvement trends. This data helps improve services. Access analytics in dashboard under 'Analytics' tab.",
                "source": "Analytics and Reporting"
            },
            {
                "id": "track_004",
                "category": "Tracking",
                "title": "Notifications and Updates",
                "content": "Stay updated: Enable notifications in settings for real-time updates. You'll receive: 1) Confirmation when complaint submitted, 2) Status change alerts, 3) Team assignment notification, 4) Resolution completion message, 5) Feedback request. Choose notification method: Email, SMS, Push notifications, or All. Update preferences in Profile > Notification Settings.",
                "source": "Notification System Guide"
            }
        ]
        
        # General Help and FAQ
        help_guidelines = [
            {
                "id": "help_001",
                "category": "Help",
                "title": "Frequently Asked Questions",
                "content": "FAQ: Q: How long does resolution take? A: High priority 2-4 hours, Medium 24-48 hours, Low 3-7 days. Q: Can I submit anonymously? A: Yes, but providing contact helps faster resolution. Q: How do I escalate? A: Call ext. 1000 or email complaints@campus.edu. Q: Can I track multiple complaints? A: Yes, view all in 'My Complaints' section. Q: What if I'm not satisfied? A: Provide feedback and request re-inspection.",
                "source": "FAQ Database"
            },
            {
                "id": "help_002",
                "category": "Help",
                "title": "Contact Information and Support",
                "content": "Need help? EMERGENCY: Call 100 (24/7). WATER: ext. 2345, water@campus.edu. ELECTRICITY: ext. 3456, electrical@campus.edu. TRANSPORT: ext. 4567, transport@campus.edu. GENERAL HELPDESK: ext. 1000, helpdesk@campus.edu. SUSTAINABILITY OFFICE: Admin Block Room 101, sustainability@campus.edu. Office hours: Mon-Fri 9 AM - 6 PM, Sat 9 AM - 1 PM.",
                "source": "Contact Directory"
            },
            {
                "id": "help_003",
                "category": "Help",
                "title": "Tips for Effective Complaint Submission",
                "content": "Best practices: 1) Be specific about location and issue, 2) Include photos if possible, 3) Mention urgency level accurately, 4) Provide contact info for follow-up, 5) Check if issue already reported, 6) Submit as soon as you notice the problem, 7) Follow up if no response in expected time. Clear, detailed complaints get resolved faster.",
                "source": "User Best Practices Guide"
            },
            {
                "id": "help_004",
                "category": "Help",
                "title": "Sustainability Awareness and Participation",
                "content": "Get involved: 1) Report issues promptly to prevent waste, 2) Participate in awareness campaigns, 3) Join Green Campus Club, 4) Attend sustainability workshops, 5) Suggest improvements via feedback form, 6) Practice conservation (turn off lights, save water, use public transport), 7) Spread awareness among peers. Every action counts toward our sustainability goals!",
                "source": "Student Engagement Program"
            }
        ]
        
        # Combine all guidelines
        all_guidelines = (water_guidelines + electricity_guidelines + transport_guidelines +
                         sdg_guidelines + reporting_guidelines + resolution_guidelines +
                         tracking_guidelines + help_guidelines)
        
        # Add to knowledge base
        for guideline in all_guidelines:
            self.add_document(
                doc_id=guideline["id"],
                content=guideline["content"],
                metadata={
                    "category": guideline["category"],
                    "title": guideline["title"],
                    "source": guideline["source"]
                }
            )
        
        print(f"[OK] Initialized knowledge base with {len(all_guidelines)} guidelines")
    
    def add_document(self, doc_id: str, content: str, metadata: Dict):
        """Add a document to the knowledge base"""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Error adding document: {e}")
    
    def search(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict]:
        """
        Search knowledge base for relevant information
        
        Args:
            query: Search query
            top_k: Number of results to return
            category: Optional category filter
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build where clause for category filter
            where_clause = {"category": category} if category else None
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def initialize_from_complaints(self, complaints: List[Dict]):
        """
        Initialize knowledge base from historical complaints
        
        Args:
            complaints: List of complaint dictionaries
        """
        try:
            # Group resolved complaints by category
            resolved_complaints = [c for c in complaints if c.get('Status') == 'Resolved']
            
            # Create knowledge entries from resolved complaints
            for i, complaint in enumerate(resolved_complaints[:50]):  # Limit to 50 for performance
                doc_id = f"complaint_{complaint.get('Complaint_ID', i)}"
                content = f"Issue: {complaint.get('Complaint', '')}. Location: {complaint.get('Location', '')}. Resolution: Successfully resolved."
                
                self.add_document(
                    doc_id=doc_id,
                    content=content,
                    metadata={
                        "category": complaint.get('Category', ''),
                        "priority": complaint.get('Priority', ''),
                        "location": complaint.get('Location', ''),
                        "type": "historical_complaint"
                    }
                )
            
            print(f"[OK] Added {len(resolved_complaints[:50])} historical complaints to knowledge base")
            
        except Exception as e:
            print(f"Error initializing from complaints: {e}")
    
    def get_category_guidelines(self, category: str) -> List[Dict]:
        """Get all guidelines for a specific category"""
        return self.search(query=f"{category} guidelines", top_k=10, category=category)
    
    def get_similar_cases(self, complaint_text: str, category: str, top_k: int = 3) -> List[Dict]:
        """Find similar historical cases"""
        results = self.search(
            query=complaint_text,
            top_k=top_k,
            category=category
        )
        
        # Filter for historical complaints
        return [r for r in results if r['metadata'].get('type') == 'historical_complaint']

# Made with Bob
