"""
Module for handling individual agent queries with Chain of Thought reasoning
Now powered by the Supervisor Agent for intelligent routing
"""
from crewai import Agent, Task, Crew
from typing import Dict, Any, Optional
from .supervisor_agent import SupervisorAgent
from .context_store import get_context_store


class AgentInteraction:
    """
    Handle individual agent queries using the Supervisor Agent

    This class now uses intelligent routing via the SupervisorAgent instead of
    requiring users to manually select which agent to query.
    """

    def __init__(self, crew_instance):
        """
        Initialize the agent interaction handler

        Args:
            crew_instance: The EventPlanningCrew instance with all agents
        """
        self.crew = crew_instance
        self.context_store = get_context_store()

        # Initialize the Supervisor Agent for intelligent routing
        self.supervisor = SupervisorAgent(
            llm=crew_instance.llm,
            crew_instance=crew_instance
        )

        # Keep the direct agent map for backwards compatibility if needed
        self.agent_map = {
            "Prediction Agent": self.crew.prediction_agent.agent,
            "Compliance Agent": self.crew.compliance_agent.agent,
            "Logistics Agent": self.crew.logistics_agent.agent,
            "Marketing Agent": self.crew.marketing_agent.agent
        }

    def query_agent(
        self,
        agent_name: str,
        question: str,
        context: Dict = None,
        use_supervisor: bool = True
    ) -> Dict[str, Any]:
        """
        Query an agent with a question

        NOW WITH INTELLIGENT ROUTING: If use_supervisor=True (default), the
        supervisor will analyze the question and route it to the most appropriate
        agent(s) automatically, ignoring the agent_name parameter.

        Args:
            agent_name: DEPRECATED - kept for backwards compatibility
            question: The user's question
            context: Optional event context
            use_supervisor: If True, use supervisor for intelligent routing (default)

        Returns:
            Dict with 'answer', 'reasoning', and 'agent_name' keys
        """
        if use_supervisor:
            # Use the intelligent supervisor agent to route the question
            return self._query_with_supervisor(question, context)
        else:
            # Legacy direct querying (kept for backwards compatibility)
            return self._query_direct(agent_name, question, context)

    def _query_with_supervisor(self, question: str, context: Dict = None) -> Dict[str, Any]:
        """
        Query using the supervisor agent for intelligent routing

        This is the new recommended approach that doesn't require manual agent selection
        """
        try:
            # Build event context
            event_context = self._build_event_context(context)

            print(f"\n[DEBUG] Question received: {question}")
            print(f"[DEBUG] Event context keys: {list(event_context.keys())}")

            # Let the supervisor route and handle the question
            result = self.supervisor.route_question(question, event_context)

            print(f"[DEBUG] Routing result - Agent used: {result.get('agents_used', 'Unknown')}")
            print(f"[DEBUG] Has answer: {bool(result.get('answer'))}")
            print(f"[DEBUG] Error if any: {result.get('error', 'None')}")

            # Log the interaction to context store
            if self.context_store.current_session_id:
                self.context_store.add_conversation(
                    session_id=self.context_store.current_session_id,
                    question=question,
                    answer=result.get('answer', ''),
                    agent_used=result.get('agents_used', ['Supervisor Agent']),
                    reasoning=result.get('reasoning', '')
                )

            return {
                'answer': result.get('answer', 'No response generated'),
                'reasoning': result.get('reasoning', 'Analysis completed'),
                'agent_name': ', '.join(result.get('agents_used', ['Supervisor Agent'])),
                'supervisor_routing': result.get('supervisor_reasoning', '')
            }

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"\n[ERROR] Exception in _query_with_supervisor:")
            print(error_trace)

            # Provide a clear error message
            return {
                'answer': f"Error processing question: {str(e)}\n\nPlease check the console for details.",
                'reasoning': f"Error details: {error_trace}",
                'agent_name': 'Supervisor Agent',
                'error': str(e)
            }

    def _query_direct(self, agent_name: str, question: str, context: Dict = None) -> Dict[str, Any]:
        """
        Legacy direct agent querying (without supervisor routing)

        This method is kept for backwards compatibility but is not recommended.
        Use the supervisor-based routing instead.
        """
        agent = self.agent_map.get(agent_name)
        if not agent:
            return {
                'answer': f"Agent {agent_name} not found",
                'reasoning': "Agent not available",
                'agent_name': agent_name
            }

        # Build context string
        event_context = self._build_event_context(context)
        context_str = ""
        if event_context:
            context_str = "\n\nEVENT CONTEXT:\n"
            for key, value in event_context.items():
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

            response = {
                'answer': str(result),
                'reasoning': f"Analysis completed by {agent_name} using specialized tools and domain expertise.",
                'agent_name': agent_name
            }

            # Log to context store
            if self.context_store.current_session_id:
                self.context_store.add_conversation(
                    session_id=self.context_store.current_session_id,
                    question=question,
                    answer=response['answer'],
                    agent_used=agent_name,
                    reasoning=response['reasoning']
                )

            return response

        except Exception as e:
            return {
                'answer': f"Error querying {agent_name}: {str(e)}",
                'reasoning': f"Technical issue occurred: {str(e)}",
                'agent_name': agent_name,
                'error': str(e)
            }

    def _build_event_context(self, context: Dict = None) -> Dict:
        """Build comprehensive event context from various sources"""
        event_context = {}

        # Start with provided context
        if context:
            event_context.update(context)

        # Enhance with context store if available
        if self.context_store.current_session_id:
            stored_context = self.context_store.get_current_context()
            if stored_context:
                event_details = stored_context.get('event_details', {})
                event_context.update(event_details)

        return event_context

    def initialize_context(self, event_details: Dict, results: Dict = None):
        """
        Initialize context for a new event session

        Args:
            event_details: Dictionary with event information
            results: Optional initial analysis results
        """
        session_id = self.context_store.create_session(event_details)

        if results:
            self.context_store.store_initial_results(session_id, results)

        # Also update the supervisor's context
        self.supervisor.store_context(event_details, results)

        return session_id


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
