"""
Context Storage System for Multi-Agent Memory and State Management

This module provides persistent context storage across agent interactions,
maintaining event details, analysis results, and conversation history.
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class ContextStore:
    """
    Centralized context storage for all agents

    Maintains:
    - Current event details
    - Initial analysis results from all agents
    - Conversation history (questions and answers)
    - Agent-specific notes and observations
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the context store

        Args:
            storage_path: Optional path to persist context to disk
        """
        self.storage_path = storage_path or os.path.join("event_horizon", "outputs", "context_storage")
        self.contexts = {}
        self.current_session_id = None

        # Create storage directory if it doesn't exist
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    def create_session(self, event_details: Dict[str, Any]) -> str:
        """
        Create a new session for an event

        Args:
            event_details: Dictionary containing event information

        Returns:
            session_id: Unique identifier for this event session
        """
        session_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id

        self.contexts[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'event_details': event_details,
            'initial_results': {},
            'conversation_history': [],
            'agent_notes': {
                'Prediction Agent': [],
                'Compliance Agent': [],
                'Logistics Agent': [],
                'Marketing Agent': []
            },
            'metadata': {
                'total_questions': 0,
                'agents_consulted': set()
            }
        }

        self._save_to_disk(session_id)
        return session_id

    def store_initial_results(self, session_id: str, results: Dict[str, Any]):
        """
        Store the initial comprehensive analysis results

        Args:
            session_id: Session identifier
            results: Dictionary with results from all four agents
        """
        if session_id not in self.contexts:
            raise ValueError(f"Session {session_id} not found")

        self.contexts[session_id]['initial_results'] = results
        self._save_to_disk(session_id)

    def add_conversation(
        self,
        session_id: str,
        question: str,
        answer: str,
        agent_used: str,
        reasoning: Optional[str] = None
    ):
        """
        Add a conversation exchange to the history

        Args:
            session_id: Session identifier
            question: User's question
            answer: Agent's answer
            agent_used: Which agent(s) provided the answer
            reasoning: Optional detailed reasoning from the agent
        """
        if session_id not in self.contexts:
            raise ValueError(f"Session {session_id} not found")

        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'agent_used': agent_used,
            'reasoning': reasoning
        }

        self.contexts[session_id]['conversation_history'].append(conversation_entry)
        self.contexts[session_id]['metadata']['total_questions'] += 1

        # Safely update agents_consulted (handle both list and string)
        if not isinstance(self.contexts[session_id]['metadata']['agents_consulted'], set):
            self.contexts[session_id]['metadata']['agents_consulted'] = set()

        if isinstance(agent_used, list):
            for agent in agent_used:
                self.contexts[session_id]['metadata']['agents_consulted'].add(agent)
        else:
            self.contexts[session_id]['metadata']['agents_consulted'].add(agent_used)

        self._save_to_disk(session_id)

    def add_agent_note(self, session_id: str, agent_name: str, note: str):
        """
        Add an internal note or observation from an agent

        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            note: The note/observation to store
        """
        if session_id not in self.contexts:
            raise ValueError(f"Session {session_id} not found")

        if agent_name not in self.contexts[session_id]['agent_notes']:
            self.contexts[session_id]['agent_notes'][agent_name] = []

        self.contexts[session_id]['agent_notes'][agent_name].append({
            'timestamp': datetime.now().isoformat(),
            'note': note
        })

        self._save_to_disk(session_id)

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve full context for a session

        Args:
            session_id: Session identifier

        Returns:
            Complete context dictionary
        """
        if session_id not in self.contexts:
            # Try to load from disk
            self._load_from_disk(session_id)

        context = self.contexts.get(session_id, {})

        # Convert set to list for JSON serialization
        if 'metadata' in context and 'agents_consulted' in context['metadata']:
            context['metadata']['agents_consulted'] = list(context['metadata']['agents_consulted'])

        return context

    def get_current_context(self) -> Dict[str, Any]:
        """
        Get context for the current active session

        Returns:
            Current context dictionary
        """
        if not self.current_session_id:
            return {}

        return self.get_context(self.current_session_id)

    def get_event_details(self, session_id: str) -> Dict[str, Any]:
        """Get just the event details for a session"""
        context = self.get_context(session_id)
        return context.get('event_details', {})

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        context = self.get_context(session_id)
        return context.get('conversation_history', [])

    def get_initial_results(self, session_id: str) -> Dict[str, Any]:
        """Get initial analysis results for a session"""
        context = self.get_context(session_id)
        return context.get('initial_results', {})

    def get_formatted_context_for_agent(self, session_id: str) -> str:
        """
        Get a formatted context string suitable for passing to an agent

        Args:
            session_id: Session identifier

        Returns:
            Formatted context string
        """
        context = self.get_context(session_id)

        if not context:
            return "No context available"

        event = context.get('event_details', {})
        results = context.get('initial_results', {})
        history = context.get('conversation_history', [])

        formatted = f"""
=== EVENT CONTEXT ===
Event Name: {event.get('name', 'N/A')}
Type: {event.get('type', 'N/A')}
Date: {event.get('date', 'N/A')} at {event.get('time', 'N/A')}
Venue: {event.get('venue', 'N/A')}
Expected Registrations: {event.get('size', 'N/A')}
Serving Alcohol: {'Yes' if event.get('alcohol') else 'No'}
External Speakers: {'Yes' if event.get('external') else 'No'}
Target Programs: {', '.join(event.get('programs', []))}
Event Tags: {', '.join(event.get('tags', []))}

=== INITIAL ANALYSIS RESULTS ===
"""

        # Add prediction results
        if 'prediction' in results:
            pred = results['prediction']
            formatted += f"""
Prediction Agent Analysis:
- Predicted Flake Rate: {pred.get('flake_rate', 'N/A')}%
- Confidence: {pred.get('confidence', 'N/A')}
- Recommendations: {', '.join(pred.get('recommendations', []))}
"""

        # Add compliance results
        if 'compliance' in results:
            comp = results['compliance']
            formatted += f"""
Compliance Agent Analysis:
- Issues Found: {len(comp.get('issues', []))}
- Actions Required: {len(comp.get('actions_required', []))}
- Venue Alternatives Suggested: {len(comp.get('alternatives', []))}
"""

        # Add logistics results
        if 'logistics' in results:
            log = results['logistics']
            formatted += f"""
Logistics Agent Analysis:
- Optimized Budget: £{log.get('budget', 'N/A'):,}
- Predicted Waste Savings: £{log.get('predicted_waste', 'N/A'):,}
- Timeline Items: {len(log.get('timeline', []))}
"""

        # Add marketing results
        if 'marketing' in results:
            mark = results['marketing']
            formatted += f"""
Marketing Agent Analysis:
- Target Personas Identified: {len(mark.get('personas', []))}
- Expected Attendance Boost: +{mark.get('expected_boost', 'N/A')}%
"""

        # Add conversation history
        if history:
            formatted += f"""
=== CONVERSATION HISTORY ===
Previous {len(history)} question(s) asked:
"""
            for i, conv in enumerate(history[-3:], 1):  # Show last 3 conversations
                formatted += f"""
Q{i}: {conv.get('question', 'N/A')}
A{i} (by {conv.get('agent_used', 'Unknown')}): {conv.get('answer', 'N/A')[:200]}...
"""

        return formatted

    def _save_to_disk(self, session_id: str):
        """Save context to disk for persistence"""
        if session_id not in self.contexts:
            return

        filepath = os.path.join(self.storage_path, f"{session_id}.json")

        context = self.contexts[session_id].copy()

        # Convert set to list for JSON serialization
        if 'metadata' in context and 'agents_consulted' in context['metadata']:
            context['metadata']['agents_consulted'] = list(context['metadata']['agents_consulted'])

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save context to disk: {e}")

    def _load_from_disk(self, session_id: str):
        """Load context from disk"""
        filepath = os.path.join(self.storage_path, f"{session_id}.json")

        if not os.path.exists(filepath):
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                context = json.load(f)

            # Convert list back to set
            if 'metadata' in context and 'agents_consulted' in context['metadata']:
                context['metadata']['agents_consulted'] = set(context['metadata']['agents_consulted'])

            self.contexts[session_id] = context
        except Exception as e:
            print(f"Warning: Could not load context from disk: {e}")

    def list_sessions(self) -> List[str]:
        """List all available session IDs"""
        disk_sessions = []
        if os.path.exists(self.storage_path):
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    disk_sessions.append(filename.replace('.json', ''))

        return list(set(list(self.contexts.keys()) + disk_sessions))

    def clear_session(self, session_id: str):
        """Clear a specific session from memory and disk"""
        if session_id in self.contexts:
            del self.contexts[session_id]

        filepath = os.path.join(self.storage_path, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)


# Global context store instance
_global_context_store = None


def get_context_store() -> ContextStore:
    """Get the global context store instance"""
    global _global_context_store
    if _global_context_store is None:
        _global_context_store = ContextStore()
    return _global_context_store
