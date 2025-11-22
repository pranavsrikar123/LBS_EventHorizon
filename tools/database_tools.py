import json
import random
import os
from typing import Dict, List

class EventDatabaseTool:
    def __init__(self):
        # Get the directory of this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '..', 'mock_data', 'past_events.json')
        with open(json_path, 'r') as f:
            self.events = json.load(f)
    
    def search_similar_events(self, query: str) -> str:
        """
        AI tool to search for similar events
        Returns formatted string for LLM to interpret
        """
        # Parse query and find matches
        results = []
        for event in self.events[:5]:  # Return top 5
            results.append(
                f"{event['event_name']}: {event['actual_attendance']} attended "
                f"(flake: {event['flake_rate']}%) - {event['notes']}"
            )
        
        return f"Found similar events:\n" + "\n".join(results)
    
    def get_flake_patterns(self, factor: str) -> str:
        """Analyze flake patterns by different factors"""
        if 'friday' in factor.lower():
            return "Friday events average 63% flake rate. Thursday: 22%, Tuesday: 18%"
        elif 'alcohol' in factor.lower():
            return "Events with alcohol: 15% avg flake. Without: 38% avg flake"
        elif 'exam' in factor.lower():
            return "During exam period: +45% flake rate increase"
        else:
            return "Average flake rate across all events: 31%"

class VenueDatabaseTool:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '..', 'mock_data', 'venue_constraints.json')
        with open(json_path, 'r') as f:
            self.venues = json.load(f)
    
    def check_venue_rules(self, venue_name: str, requirements: Dict) -> str:
        """Check if venue meets requirements"""
        venue = self.venues.get(venue_name, {})
        
        issues = []
        if requirements.get('size', 0) > venue.get('capacity', 0):
            issues.append(f"Capacity issue: {venue_name} holds {venue.get('capacity')}, need {requirements.get('size')}")
        
        if requirements.get('alcohol') and not venue.get('alcohol_permitted'):
            issues.append(f"Alcohol not permitted in {venue_name}")
        
        if issues:
            return f"Issues found: {'; '.join(issues)}"
        return f"{venue_name} suitable. Capacity: {venue.get('capacity')}. {venue.get('license_note', '')}"
    
    def suggest_alternatives(self, requirements: Dict) -> str:
        """Suggest alternative venues"""
        suitable = []
        for name, venue in self.venues.items():
            if venue['capacity'] >= requirements.get('size', 0):
                if not requirements.get('alcohol') or venue.get('alcohol_permitted'):
                    suitable.append(f"{name} (capacity: {venue['capacity']})")
        
        return f"Alternative venues: {', '.join(suitable[:3])}"
    
    def check_conflicts(self, date: str) -> str:
        """Check calendar conflicts"""
        # Simplified conflict checking
        import random
        if random.random() > 0.7:
            return f"Warning: MBA Finance exam on {date}"
        return f"No major conflicts on {date}"

class StudentSegmentTool:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '..', 'mock_data', 'student_personas.json')
        with open(json_path, 'r') as f:
            self.profiles = json.load(f)
    
    def analyze_attendance_patterns(self, tags: List[str]) -> str:
        """Analyze which segments attend events with these tags"""
        patterns = {
            "Technology": "MBA2025 (75% attendance), MiM (45% attendance)",
            "Finance": "MBA2024 (85% attendance), MFA (90% attendance)",
            "Social": "All segments (60-80% attendance)",
            "Entrepreneurship": "MBA2025 (70% attendance), Executive MBA (65% attendance)"
        }
        
        for tag in tags:
            if tag in patterns:
                return f"Attendance patterns for {tag}: {patterns[tag]}"
        
        return "General attendance: MBA 65%, MiM 55%, Executive MBA 80%"
    
    def create_personas(self, event_type: str, tags: List[str]) -> str:
        """Create anonymous personas"""
        personas = [
            {
                "name": "Persona A: The Career Climber",
                "profile": "Attends all career/finance events, 90% attendance rate",
                "motivators": "Networking, exclusive speakers, career advancement",
                "preferred_time": "Tuesday lunch or Thursday evening"
            },
            {
                "name": "Persona B: The Tech Enthusiast",
                "profile": "Focuses on AI/startup events, 75% attendance when interested",
                "motivators": "Learning, innovation, potential co-founders",
                "preferred_time": "Evening events with demos"
            },
            {
                "name": "Persona C: The Social Connector",
                "profile": "Attends if friends are going, 50% attendance rate",
                "motivators": "Social proof, alcohol, informal networking",
                "preferred_time": "Thursday Sundowners timing"
            }
        ]
        
        return json.dumps(personas[:2], indent=2)
    
    def generate_targeted_email(self, persona: str, event_name: str) -> str:
        """Generate personalized email template"""
        templates = {
            "Career": f"Subject: Exclusive: {event_name} - Advance Your Career\n\nThis is your chance to connect with industry leaders...",
            "Tech": f"Subject: 🚀 {event_name} - Limited Seats\n\nJoin fellow innovators for cutting-edge insights...",
            "Social": f"Subject: Everyone's going: {event_name}\n\n20+ of your classmates already signed up..."
        }
        
        for key, template in templates.items():
            if key.lower() in persona.lower():
                return template
        
        return f"Subject: You're Invited: {event_name}"

class WeatherTool:
    def predict_weather_impact(self, date: str) -> str:
        """Predict weather impact on attendance"""
        import random
        impacts = [
            "Historical data: Rain reduces attendance by 15-20%",
            "Clear weather expected - no weather impact",
            "Cold weather predicted - may reduce attendance by 10%"
        ]
        return random.choice(impacts)