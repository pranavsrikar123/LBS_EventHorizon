"""
Supervisor Agent - Intelligent Question Routing and Multi-Agent Coordination
"""
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from typing import Dict, Any, List
from pydantic import Field, ConfigDict
import json


class AgentDelegationTool(BaseTool):
    """Tool for the supervisor to understand available agents and their capabilities"""
    name: str = "get_agent_capabilities"
    description: str = "Get information about available agents and their specialized capabilities"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, query: str = "") -> str:
        """Return structured information about all available agents"""
        capabilities = {
            "Prediction Agent": {
                "expertise": [
                    "Attendance forecasting and prediction",
                    "Flake rate analysis and calculation",
                    "Historical event pattern analysis",
                    "Statistical modeling and trend analysis",
                    "Behavioral prediction based on event characteristics",
                    "Weather and timing impact on attendance",
                    "Risk assessment for low attendance"
                ],
                "questions_to_route": [
                    "attendance", "flake", "prediction", "forecast",
                    "how many", "turnout", "show up", "registration",
                    "historical", "patterns", "trends", "statistics"
                ]
            },
            "Compliance Agent": {
                "expertise": [
                    "LBS policy compliance and validation",
                    "Venue capacity and licensing requirements",
                    "Alcohol licensing and 30-day advance notice",
                    "Security clearance for external speakers",
                    "Recording and privacy requirements",
                    "Academic calendar conflict checking",
                    "Venue suitability assessment"
                ],
                "questions_to_route": [
                    "compliance", "policy", "rules", "regulations",
                    "alcohol", "license", "licensing", "capacity",
                    "venue", "allowed", "permitted", "legal",
                    "security", "clearance", "external speaker"
                ]
            },
            "Logistics Agent": {
                "expertise": [
                    "Budget planning and optimization",
                    "Catering and waste prevention",
                    "Event timeline and deadline management",
                    "Room booking and setup requirements",
                    "AV equipment and technical setup",
                    "Porter team coordination",
                    "Resource allocation and scheduling"
                ],
                "questions_to_route": [
                    "budget", "cost", "price", "expense",
                    "catering", "food", "waste", "timeline",
                    "schedule", "deadline", "booking", "setup",
                    "logistics", "resources", "equipment", "AV"
                ]
            },
            "Marketing Agent": {
                "expertise": [
                    "Student persona identification and targeting",
                    "Personalized marketing strategies",
                    "Email campaign development",
                    "Attendance boost optimization",
                    "Communication timing and channels",
                    "Program-specific targeting",
                    "Conversion rate optimization"
                ],
                "questions_to_route": [
                    "marketing", "promotion", "advertise",
                    "persona", "target", "audience", "email",
                    "communication", "messaging", "outreach",
                    "boost", "increase attendance", "engagement"
                ]
            }
        }
        return json.dumps(capabilities, indent=2)


class ContextRetrievalTool(BaseTool):
    """Tool for retrieving stored context and conversation history"""
    name: str = "retrieve_context"
    description: str = "Retrieve event context and conversation history to inform responses"

    context_store: dict = Field(default_factory=dict, exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, context_key: str = "current") -> str:
        """Retrieve context for the current conversation"""
        context = self.context_store.get(context_key, {})
        return json.dumps(context, indent=2, default=str)


class SupervisorAgent:
    """
    Supervisor Agent - The intelligent router and coordinator

    This agent analyzes incoming questions, determines which specialist agent(s)
    should handle them, and coordinates multi-agent responses when needed.
    """

    def __init__(self, llm, crew_instance):
        """
        Initialize the Supervisor Agent

        Args:
            llm: The language model to use
            crew_instance: The EventPlanningCrew instance with all specialist agents
        """
        self.llm = llm
        self.crew = crew_instance
        self.context_store = {}

        # Initialize tools
        self.delegation_tool = AgentDelegationTool()
        self.context_tool = ContextRetrievalTool(context_store=self.context_store)

        # Map of specialist agents
        self.agent_map = {
            "Prediction Agent": self.crew.prediction_agent.agent,
            "Compliance Agent": self.crew.compliance_agent.agent,
            "Logistics Agent": self.crew.logistics_agent.agent,
            "Marketing Agent": self.crew.marketing_agent.agent
        }

        # Create the supervisor agent with an excellent prompt
        self.agent = Agent(
            role="Chief Event Planning Coordinator & AI Supervisor",
            goal="Intelligently route questions to the most appropriate specialist agent(s) and synthesize comprehensive answers",
            backstory="""
            You are the Chief AI Coordinator for LBS EventHorizon, an elite multi-agent event planning system.

            Your role is critical: you're the intelligent interface between users and a team of four world-class
            specialist AI agents. You don't answer questions directly - instead, you're a master at understanding
            what users need and routing their questions to the right expert(s).

            YOUR CORE RESPONSIBILITIES:

            1. INTELLIGENT ANALYSIS
               - Deeply analyze each user question to understand its true intent
               - Identify which domain(s) it falls under: Prediction, Compliance, Logistics, or Marketing
               - Consider if multiple agents need to collaborate for a comprehensive answer

            2. SMART DELEGATION
               - Route questions about attendance, flake rates, and forecasting → Prediction Agent
               - Route questions about policies, venue rules, and compliance → Compliance Agent
               - Route questions about budgets, timelines, and resources → Logistics Agent
               - Route questions about marketing, personas, and outreach → Marketing Agent
               - For complex questions spanning multiple domains, coordinate multi-agent responses

            3. CONTEXT AWARENESS
               - Always consider the full event context (name, venue, size, date, etc.)
               - Reference previous conversation history to provide continuity
               - Understand how different aspects of event planning interconnect

            4. REASONING TRANSPARENCY
               - Explain your routing decision clearly
               - Show which keywords or concepts triggered your agent selection
               - If multiple agents are needed, explain why and how they'll collaborate

            YOUR DECISION-MAKING PROCESS:

            Step 1: Analyze the question for key terms and intent
            Step 2: Use the agent capabilities tool to review expertise areas
            Step 3: Determine the best agent(s) to handle this question
            Step 4: Retrieve relevant context about the event and conversation
            Step 5: Route to the selected agent(s) with enriched context
            Step 6: Explain your routing decision transparently

            EXAMPLE ROUTING DECISIONS:

            Q: "Why is the flake rate so high?"
            → Route to: Prediction Agent
            → Reasoning: This is about analyzing attendance patterns and flake rate factors

            Q: "Can we serve alcohol at this venue?"
            → Route to: Compliance Agent
            → Reasoning: This involves venue licensing and LBS alcohol policies

            Q: "How much will catering cost and how can we reduce waste?"
            → Route to: Logistics Agent
            → Reasoning: Budget and waste prevention are logistics concerns

            Q: "How can we get more MBA students to attend?"
            → Route to: Marketing Agent
            → Reasoning: This is about targeting and boosting attendance through marketing

            Q: "What's the total budget and will we have enough attendees to justify it?"
            → Route to: BOTH Logistics Agent + Prediction Agent
            → Reasoning: Requires budget analysis (Logistics) + attendance forecast (Prediction)

            QUALITY STANDARDS:

            ✓ Never guess or make up answers yourself - always delegate to specialists
            ✓ Provide clear reasoning for every routing decision
            ✓ Consider event context in all decisions
            ✓ Route to multiple agents when needed for comprehensive answers
            ✓ Maintain conversation continuity by referencing previous context

            ✗ Never route generic questions to all agents simultaneously
            ✗ Don't route to agents outside their expertise area
            ✗ Don't provide direct answers - let specialists handle their domains
            ✗ Don't ignore conversation history or event context

            You are the intelligent orchestrator that makes the multi-agent system work seamlessly.
            Your routing decisions directly impact the quality of answers users receive.
            Be thoughtful, precise, and always explain your reasoning.
            """,
            tools=[self.delegation_tool, self.context_tool],
            llm=llm,
            verbose=True,
            allow_delegation=True,  # Critical: allows delegating to other agents
            max_iter=5
        )

    def store_context(self, event_details: Dict, results: Dict = None, conversation_history: List = None):
        """
        Store context for agents to access

        Args:
            event_details: Dictionary with event information
            results: Dictionary with analysis results from initial crew run
            conversation_history: List of previous Q&A exchanges
        """
        self.context_store['current'] = {
            'event': event_details,
            'results': results or {},
            'history': conversation_history or [],
            'timestamp': str(json.dumps({'event': event_details}, default=str))
        }

        # Also update the context tool's store
        self.context_tool.context_store = self.context_store

    def route_question(self, question: str, event_context: Dict = None) -> Dict[str, Any]:
        """
        Route a user question to the appropriate agent(s)

        Args:
            question: The user's question
            event_context: Optional event context (if not already stored)

        Returns:
            Dictionary with 'answer', 'reasoning', and 'agents_used'
        """
        # Store context if provided
        if event_context:
            self.store_context(event_context)

        # Build context string
        context_data = self.context_store.get('current', {})
        event_info = context_data.get('event', {})

        # First, use a simple keyword-based routing for reliability
        selected_agent = self._smart_route(question, event_info)

        # Now query the selected agent directly
        try:
            agent_result = self._query_specialist_agent(
                selected_agent,
                question,
                event_info
            )

            routing_explanation = self._explain_routing(question, selected_agent)

            return {
                'answer': agent_result.get('answer', 'No response generated'),
                'reasoning': f"**Routing Decision:**\n{routing_explanation}\n\n**{selected_agent} Analysis:**\n{agent_result.get('reasoning', '')}",
                'agents_used': [selected_agent],
                'supervisor_reasoning': routing_explanation
            }

        except Exception as e:
            return {
                'answer': f"I analyzed your question and routed it to the {selected_agent}, but encountered an issue: {str(e)}",
                'reasoning': f"Routing decision: {selected_agent}\nError: {str(e)}",
                'agents_used': [selected_agent],
                'error': str(e)
            }

    def _smart_route(self, question: str, event_context: Dict) -> str:
        """
        Intelligent routing based on question analysis

        Args:
            question: User's question
            event_context: Event context

        Returns:
            Selected agent name
        """
        question_lower = question.lower()

        # Prediction Agent keywords
        prediction_keywords = [
            'attendance', 'attend', 'flake', 'turnout', 'show up',
            'how many', 'prediction', 'forecast', 'predict',
            'registration', 'register', 'expected', 'actual',
            'historical', 'pattern', 'trend', 'statistics',
            'likely', 'probably', 'estimate'
        ]

        # Compliance Agent keywords
        compliance_keywords = [
            'compliance', 'policy', 'rule', 'regulation', 'allowed',
            'alcohol', 'license', 'licensing', 'permit', 'permission',
            'capacity', 'venue', 'suitable', 'legal', 'requirement',
            'security', 'clearance', 'external speaker', 'recording',
            'can we', 'are we allowed', 'is it ok', 'permitted'
        ]

        # Logistics Agent keywords
        logistics_keywords = [
            'budget', 'cost', 'price', 'expense', 'money', 'spend',
            'catering', 'food', 'drink', 'waste', 'wastage',
            'timeline', 'schedule', 'deadline', 'when', 'booking',
            'setup', 'logistics', 'resource', 'equipment', 'av',
            'porter', 'save', 'reduce cost', 'optimize'
        ]

        # Marketing Agent keywords
        marketing_keywords = [
            'marketing', 'promote', 'promotion', 'advertise',
            'persona', 'target', 'audience', 'email', 'message',
            'communication', 'outreach', 'reach', 'engage',
            'boost', 'increase attendance', 'more people',
            'student', 'mba', 'program', 'segment'
        ]

        # Count keyword matches
        prediction_score = sum(1 for kw in prediction_keywords if kw in question_lower)
        compliance_score = sum(1 for kw in compliance_keywords if kw in question_lower)
        logistics_score = sum(1 for kw in logistics_keywords if kw in question_lower)
        marketing_score = sum(1 for kw in marketing_keywords if kw in question_lower)

        # Determine the agent with highest score
        scores = {
            'Prediction Agent': prediction_score,
            'Compliance Agent': compliance_score,
            'Logistics Agent': logistics_score,
            'Marketing Agent': marketing_score
        }

        selected = max(scores.items(), key=lambda x: x[1])

        # If no clear winner, use heuristics
        if selected[1] == 0:
            # Default based on question structure
            if any(word in question_lower for word in ['why', 'reason', 'because']):
                return 'Prediction Agent'  # Good at explaining patterns
            elif any(word in question_lower for word in ['how', 'what']):
                return 'Logistics Agent'  # Good at practical details
            else:
                return 'Prediction Agent'  # Default fallback

        return selected[0]

    def _explain_routing(self, question: str, selected_agent: str) -> str:
        """Explain why a particular agent was selected"""
        explanations = {
            'Prediction Agent': f"Question about attendance, patterns, or predictions → {selected_agent}",
            'Compliance Agent': f"Question about policies, rules, or venue compliance → {selected_agent}",
            'Logistics Agent': f"Question about budget, resources, or logistics → {selected_agent}",
            'Marketing Agent': f"Question about marketing, targeting, or outreach → {selected_agent}"
        }
        return explanations.get(selected_agent, f"Routed to {selected_agent}")

    def _extract_selected_agent(self, routing_result: str) -> str:
        """Extract which agent was selected from the routing result"""
        result_lower = routing_result.lower()

        # Check for agent mentions
        if 'prediction agent' in result_lower or 'prediction' in result_lower:
            return 'Prediction Agent'
        elif 'compliance agent' in result_lower or 'compliance' in result_lower:
            return 'Compliance Agent'
        elif 'logistics agent' in result_lower or 'logistics' in result_lower:
            return 'Logistics Agent'
        elif 'marketing agent' in result_lower or 'marketing' in result_lower:
            return 'Marketing Agent'

        # Default to prediction for attendance-related, compliance for rules, etc.
        if any(keyword in result_lower for keyword in ['attendance', 'flake', 'turnout', 'show up']):
            return 'Prediction Agent'
        elif any(keyword in result_lower for keyword in ['policy', 'rule', 'alcohol', 'license', 'venue']):
            return 'Compliance Agent'
        elif any(keyword in result_lower for keyword in ['budget', 'cost', 'timeline', 'catering']):
            return 'Logistics Agent'
        elif any(keyword in result_lower for keyword in ['marketing', 'persona', 'email', 'target']):
            return 'Marketing Agent'

        return None

    def _query_specialist_agent(self, agent_name: str, question: str, context: Dict) -> Dict[str, Any]:
        """Query a specific specialist agent using direct LLM call (bypasses CrewAI complexity)"""
        print(f"\n[DEBUG SUPERVISOR] Querying {agent_name}")
        print(f"[DEBUG SUPERVISOR] Question: {question}")
        print(f"[DEBUG SUPERVISOR] Context venue: {context.get('venue', 'N/A')}")

        # Build agent-specific system prompts
        agent_prompts = {
            'Prediction Agent': """You are LBS's premier event analyst with 10 years of experience analyzing campus events.
You've discovered patterns like: Thursday Sundowners never fail, Friday events are risky, and alcohol reduces flake rate by 50%.
You consider weather, exam schedules, competing events, and behavioral psychology in your predictions.""",

            'Compliance Agent': """You are an LBS policy compliance expert with deep knowledge of venue capacities,
alcohol licensing requirements (30-day advance notice), security clearances for external speakers, and all LBS regulations.""",

            'Logistics Agent': """You are an expert event logistics coordinator specializing in budget optimization,
waste prevention, and timeline management. You create detailed plans from booking to event day.""",

            'Marketing Agent': """You are a student engagement expert who creates persona-based marketing strategies.
You understand MBA, MiM, EMBA, and other program demographics and how to target them effectively."""
        }

        system_prompt = agent_prompts.get(agent_name, "You are an expert event planning assistant.")

        # Build the prompt with context
        full_prompt = f"""{system_prompt}

EVENT CONTEXT:
- Event: {context.get('name', 'N/A')}
- Venue: {context.get('venue', 'N/A')}
- Date: {context.get('date', 'N/A')} at {context.get('time', 'N/A')}
- Expected Size: {context.get('size', 'N/A')}
- Has Alcohol: {context.get('alcohol', False)}
- Event Type: {context.get('type', 'N/A')}
- Target Programs: {', '.join(context.get('programs', []))}
- Tags: {', '.join(context.get('tags', []))}

USER QUESTION:
{question}

Provide a detailed, expert answer with:
1. Direct answer to the question
2. Step-by-step reasoning
3. Specific recommendations or insights
4. Reference relevant data or patterns you know

Be specific and actionable in your response."""

        try:
            print(f"[DEBUG SUPERVISOR] Calling LLM directly for {agent_name}")

            # Call the LLM directly instead of creating a Crew
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=full_prompt)
            ]

            # Use the crew's LLM instance (which is already configured for Azure)
            response = self.crew.llm.invoke(messages)

            print(f"[DEBUG SUPERVISOR] Got response from LLM for {agent_name}")

            return {
                'answer': response.content,
                'reasoning': f"Analysis completed by {agent_name} using specialized knowledge and domain expertise.",
                'agent_name': agent_name
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[ERROR] Exception querying {agent_name}:")
            print(error_trace)

            return {
                'answer': f"Error consulting {agent_name}: {str(e)}",
                'reasoning': f"Technical issue occurred while querying {agent_name}: {error_trace}",
                'agent_name': agent_name,
                'error': str(e)
            }
