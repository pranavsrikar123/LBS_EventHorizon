from crewai import Agent
from crewai.tools import BaseTool
from tools.database_tools import EventDatabaseTool
from pydantic import Field, ConfigDict

# --- 1. Define Wrapper Tools ---
# We wrap your existing database methods in a class that CrewAI accepts.
class SearchSimilarEventsTool(BaseTool):
    name: str = "search_similar_events"
    description: str = "Search historical events by tags, type, or date"
    
    # We use Field(exclude=True) so Pydantic doesn't try to validate the complex DB object
    db_tool: object = Field(exclude=True) 
    
    # Allow arbitrary types (like your DB tool)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, query: str) -> str:
        return self.db_tool.search_similar_events(query)

class GetFlakePatternsTool(BaseTool):
    name: str = "get_flake_patterns"
    description: str = "Analyze flake rate patterns by various factors"
    
    db_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, query: str) -> str:
        # Assuming get_flake_patterns takes a query string or arguments
        return self.db_tool.get_flake_patterns(query)

# --- 2. Your Agent Class ---
class PredictionAgent:
    def __init__(self, llm):
        self.llm = llm
        
        # Initialize the original database logic
        db_instance = EventDatabaseTool()
        
        # Initialize the Wrappers with the db instance
        self.search_tool = SearchSimilarEventsTool(db_tool=db_instance)
        self.flake_tool = GetFlakePatternsTool(db_tool=db_instance)
        
        # Create agent
        self.agent = Agent(
            role="Senior Event Analytics Specialist",
            goal="Predict event attendance with >85% accuracy using historical data and environmental factors",
            backstory="""
            You are LBS's premier event analyst with 10 years of experience.
            You've analyzed over 500 campus events and discovered patterns others miss.
            You know that Thursday Sundowners never fail, Friday events are risky,
            and alcohol reduces flake rate by 50%. You consider weather, exam schedules,
            competing events, and behavioral psychology in your predictions.
            You're known for your data-driven decisions and bold recommendations.
            """,
            # Pass the wrapper instances here
            tools=[self.search_tool, self.flake_tool],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=5
        )
    
    def think(self, thought):
        """Log agent's thinking process for UI display"""
        return f"🤔 Prediction Agent: {thought}"