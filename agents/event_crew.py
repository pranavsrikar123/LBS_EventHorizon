from crewai import Crew, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.prediction_agent import PredictionAgent
from agents.compliance_agent import ComplianceAgent
from agents.logistics_agent import LogisticsAgent
from agents.marketing_agent import MarketingAgent
import os
from datetime import datetime

class EventPlanningCrew:
    def __init__(self, api_key=None):
        # Initialize LLM (will use GPT-5 later)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            api_key= "AIzaSyBQp7y7VLNbyd6Vfo2uzYB0KhxdgctuFws"
        )
        
        # Initialize agents
        self.prediction_agent = PredictionAgent(self.llm)
        self.compliance_agent = ComplianceAgent(self.llm)
        self.logistics_agent = LogisticsAgent(self.llm)
        self.marketing_agent = MarketingAgent(self.llm)
        
        # Agent thinking logs (for UI display)
        self.thinking_log = []
    
    def plan_event(self, event_details, show_thinking=True):
        """
        Main orchestration function - agents work together
        """
        self.thinking_log = []
        
        # Create the crew
        crew = Crew(
            agents=[
                self.prediction_agent.agent,
                self.compliance_agent.agent,
                self.logistics_agent.agent,
                self.marketing_agent.agent
            ],
            tasks=self._create_tasks(event_details),
            verbose=True,  # Shows agent communication
            process="sequential"  # Agents work in sequence
        )
        
        # Execute crew tasks
        results = crew.kickoff()
        
        # Parse and structure results
        return self._structure_results(results, event_details)
    
    def _create_tasks(self, event_details):
        """Create tasks for each agent"""
        
        # Task 1: Prediction Analysis
        prediction_task = Task(
            description=f"""
            Analyze the following event and predict attendance:
            Event: {event_details['name']}
            Type: {event_details['type']}
            Date: {event_details['date']} at {event_details['time']}
            Venue: {event_details['venue']}
            Expected Size: {event_details['size']}
            Has Alcohol: {event_details.get('alcohol', False)}
            Tags: {', '.join(event_details.get('tags', []))}
            
            You must:
            1. Query historical events database for similar events
            2. Check weather patterns for this date
            3. Calculate expected registration and actual attendance
            4. Predict flake rate with reasoning
            5. Suggest improvements if flake rate > 30%
            
            Output format:
            - Expected Registration: [number]
            - Predicted Attendance: [number]  
            - Flake Rate: [percentage]
            - Confidence: [HIGH/MEDIUM/LOW]
            - Reasoning: [detailed explanation]
            - Recommendations: [if flake rate is high]
            """,
            agent=self.prediction_agent.agent,
            expected_output="Detailed attendance prediction with reasoning"
        )
        
        # Task 2: Compliance Check
        compliance_task = Task(
            description=f"""
            Review event for compliance and venue suitability:
            Venue: {event_details['venue']}
            Size: {event_details['size']}
            Alcohol: {event_details.get('alcohol', False)}
            External Speakers: {event_details.get('external', False)}
            Recording: {event_details.get('recording', False)}
            Date: {event_details['date']}
            
            Check:
            1. Venue capacity vs expected size
            2. Alcohol licensing rules
            3. Recording requirements (48hr notice)
            4. Security clearance for external speakers
            5. Academic calendar conflicts
            
            If issues found, suggest alternative venues or solutions.
            
            Output format:
            - Venue Suitable: [YES/NO]
            - Issues Found: [list]
            - Required Actions: [list with deadlines]
            - Alternative Solutions: [if issues exist]
            """,
            agent=self.compliance_agent.agent,
            expected_output="Compliance validation with actionable recommendations"
        )
        
        # Task 3: Logistics Planning
        logistics_task = Task(
            description=f"""
            Based on prediction and compliance results, plan logistics:

            Create:
            1. Timeline with critical deadlines
            2. Room booking requirements
            3. Catering and waste prediction
            4. Setup requirements (porter team, AV, etc.)
            5. Budget breakdown with predicted waste

            Calculate potential waste based on predicted vs registered attendees.

            Output format:
            - Timeline: [list of deadline-task pairs]
            - Total Budget: [amount]
            - Predicted Waste: [amount and breakdown]
            - Setup Requirements: [detailed list]
            """,
            agent=self.logistics_agent.agent,
            expected_output="Complete logistics plan with budget",
            context=[prediction_task, compliance_task]  # Uses previous results
        )
        
        # Task 4: Marketing Strategy
        marketing_task = Task(
            description=f"""
            Create targeted marketing strategy based on all previous analyses:
            
            Target Programs: {event_details.get('programs', [])}
            Event Tags: {event_details.get('tags', [])}
            Predicted Attendance: [from prediction agent]
            
            Deliver:
            1. Identify student personas (without using PII)
            2. Create 3 persona types most likely to attend
            3. Generate personalized email template for each persona
            4. Estimate attendance boost from targeted marketing
            5. Recommend reminder schedule
            
            Output format:
            - Top 3 Personas: [descriptions without PII]
            - Expected Conversion Rate: [per persona]
            - Email Templates: [3 personalized versions]
            - Predicted Attendance Boost: [percentage]
            """,
            agent=self.marketing_agent.agent,
            expected_output="Targeted marketing strategy with personas",
            context=[prediction_task, compliance_task, logistics_task]
        )
        
        return [prediction_task, compliance_task, logistics_task, marketing_task]
    
    def _structure_results(self, raw_results, event_details):
        """Structure agent outputs for UI display"""
        return {
            'prediction': self._parse_prediction(raw_results),
            'compliance': self._parse_compliance(raw_results),
            'logistics': self._parse_logistics(raw_results),
            'marketing': self._parse_marketing(raw_results),
            'thinking_log': self.thinking_log,
            'event_details': event_details
        }
    
    def _parse_prediction(self, results):
        # Parse prediction agent output
        # This would parse the structured output from the agent
        return {
            'expected_registration': 100,
            'predicted_attendance': 75,
            'flake_rate': 25,
            'confidence': 'HIGH',
            'reasoning': results.get('prediction_reasoning', ''),
            'recommendations': []
        }
    
    def _parse_compliance(self, results):
        return {
            'venue_suitable': True,
            'issues': [],
            'actions_required': [],
            'alternatives': []
        }
    
    def _parse_logistics(self, results):
        return {
            'timeline': [],
            'budget': 5000,
            'predicted_waste': 750,
            'setup_requirements': []
        }
    
    def _parse_marketing(self, results):
        return {
            'personas': [],
            'email_templates': [],
            'expected_boost': 15
        }