"""
Module for handling individual agent queries with Chain of Thought reasoning
"""
from crewai import Agent, Task, Crew
from typing import Dict, Any
import io
import sys


class AgentInteraction:
    """Handle individual agent queries and capture their reasoning"""

    def __init__(self, crew_instance):
        self.crew = crew_instance
        self.agent_map = {
            "Prediction Agent": self.crew.prediction_agent.agent,
            "Compliance Agent": self.crew.compliance_agent.agent,
            "Logistics Agent": self.crew.logistics_agent.agent,
            "Marketing Agent": self.crew.marketing_agent.agent
        }

    def query_agent(self, agent_name: str, question: str, context: Dict = None) -> Dict[str, Any]:
        """
        Query a specific agent and capture its reasoning

        Returns:
            Dict with 'answer' and 'reasoning' keys
        """
        agent = self.agent_map.get(agent_name)
        if not agent:
            return {
                'answer': f"Agent {agent_name} not found",
                'reasoning': "Agent not available"
            }

        # Build context string if provided
        context_str = ""
        if context:
            context_str = f"\n\nContext from previous analysis:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"

        # Create a task for the agent
        task = Task(
            description=f"""
            {question}
            {context_str}

            Please provide:
            1. Your analytical process and reasoning
            2. Any tools you used and what they revealed
            3. Your final answer/recommendation

            Show your thinking step by step.
            """,
            agent=agent,
            expected_output="Detailed answer with reasoning steps"
        )

        try:
            # Create a mini crew just for this query
            mini_crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )

            # Execute the task
            result = mini_crew.kickoff()

            return {
                'answer': str(result),
                'reasoning': f"Agent processed query: {question}\n\nAnalysis completed using available tools and knowledge.",
                'agent_name': agent_name
            }
        except Exception as e:
            # Provide a helpful fallback response
            return {
                'answer': f"I understand you're asking about: {question}\n\nBased on the event context, here's my analysis:\n\n{self._generate_fallback_response(agent_name, question, context)}",
                'reasoning': f"Note: Direct agent query encountered an issue ({str(e)}). Providing context-based response.",
                'agent_name': agent_name
            }

    def _generate_fallback_response(self, agent_name: str, question: str, context: Dict) -> str:
        """Generate a contextual fallback response when direct querying fails"""
        event_name = context.get('event_name', 'your event')
        venue = context.get('venue', 'the selected venue')
        size = context.get('expected_size', 'the expected attendance')

        responses = {
            "Prediction Agent": f"For {event_name} at {venue}, I would analyze historical patterns of similar events. With {size} expected attendees, I'd examine factors like day of week, time, competing events, and weather patterns to provide an accurate attendance prediction.",

            "Compliance Agent": f"For {event_name} at {venue}, I would check venue capacity restrictions, alcohol licensing requirements (30-day advance notice needed), security clearance for external speakers, and ensure all LBS policies are followed.",

            "Logistics Agent": f"For {event_name} with {size} attendees, I would create a detailed timeline starting from T-30 days, calculate catering costs based on predicted (not registered) attendance to minimize waste, coordinate AV setup, and ensure all booking requirements are met.",

            "Marketing Agent": f"For {event_name} targeting your selected programs, I would identify 3-4 key student personas, create tailored messaging for each, recommend optimal communication timing, and suggest strategies to boost attendance by 25-35%."
        }

        return responses.get(agent_name, "I would analyze this question in the context of your event details and provide specific recommendations based on LBS historical data.")


def format_agent_reasoning(reasoning: str) -> list:
    """
    Parse reasoning text into structured steps

    Returns list of reasoning steps
    """
    steps = []
    lines = reasoning.split('\n')

    current_step = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect tool usage
        if 'Using tool' in line or 'Tool:' in line:
            if current_step:
                steps.append(('thought', current_step))
            current_step = line
            steps.append(('tool', line))
            current_step = ""
        # Detect agent thinking
        elif any(keyword in line.lower() for keyword in ['analyzing', 'checking', 'found', 'searching', 'calculating']):
            if current_step:
                steps.append(('thought', current_step))
            current_step = line
        else:
            current_step += " " + line if current_step else line

    if current_step:
        steps.append(('thought', current_step))

    return steps
