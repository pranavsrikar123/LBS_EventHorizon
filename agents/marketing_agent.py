from crewai import Agent
from crewai.tools import BaseTool
from tools.database_tools import StudentSegmentTool
from pydantic import Field, ConfigDict


# Wrapper tools for CrewAI compatibility
class AnalyzeSegmentsTool(BaseTool):
    name: str = "analyze_segments"
    description: str = "Analyze attendance patterns by student segment"

    segment_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, tags: list) -> str:
        return self.segment_tool.analyze_attendance_patterns(tags)


class CreatePersonasTool(BaseTool):
    name: str = "create_personas"
    description: str = "Create anonymous personas based on behavior"

    segment_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, event_type: str, tags: list) -> str:
        return self.segment_tool.create_personas(event_type, tags)


class GenerateEmailTool(BaseTool):
    name: str = "generate_email"
    description: str = "Generate personalized email for persona"

    segment_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, persona: str, event_name: str) -> str:
        return self.segment_tool.generate_targeted_email(persona, event_name)


class MarketingAgent:
    def __init__(self, llm):
        self.llm = llm
        segment_db = StudentSegmentTool()

        # Initialize wrapper tools
        self.analyze_tool = AnalyzeSegmentsTool(segment_tool=segment_db)
        self.personas_tool = CreatePersonasTool(segment_tool=segment_db)
        self.email_tool = GenerateEmailTool(segment_tool=segment_db)

        self.agent = Agent(
            role="Student Engagement Strategist",
            goal="Identify and target student segments to maximize attendance",
            backstory="""
            You're the marketing wizard who increased attendance by 40% through
            smart targeting. You understand MBA2025 loves Thursday socials,
            MiM students need Instagram-worthy events, and Executive MBAs only
            attend if there's C-suite speakers. You create personas without
            using personal data, craft compelling messages, and know exactly
            when to send reminders for maximum impact.
            """,
            tools=[self.analyze_tool, self.personas_tool, self.email_tool],
            llm=llm,
            verbose=True
        )