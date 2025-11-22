from crewai import Agent
from crewai.tools import BaseTool
from tools.database_tools import VenueDatabaseTool
from pydantic import Field, ConfigDict


# Wrapper tools for CrewAI compatibility
class CheckVenueRulesTool(BaseTool):
    name: str = "check_venue_rules"
    description: str = "Check venue capacity, alcohol permission, and restrictions"

    venue_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, venue_name: str, requirements: dict) -> str:
        return self.venue_tool.check_venue_rules(venue_name, requirements)


class CheckCalendarConflictsTool(BaseTool):
    name: str = "check_calendar_conflicts"
    description: str = "Check for academic calendar conflicts"

    venue_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, date: str) -> str:
        return self.venue_tool.check_conflicts(date)


class SuggestAlternativeVenueTool(BaseTool):
    name: str = "suggest_alternative_venue"
    description: str = "Find alternative venues if current one has issues"

    venue_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, requirements: dict) -> str:
        return self.venue_tool.suggest_alternatives(requirements)


class ComplianceAgent:
    def __init__(self, llm):
        self.llm = llm
        venue_db = VenueDatabaseTool()

        # Initialize wrapper tools
        self.check_venue_tool = CheckVenueRulesTool(venue_tool=venue_db)
        self.check_conflicts_tool = CheckCalendarConflictsTool(venue_tool=venue_db)
        self.suggest_venue_tool = SuggestAlternativeVenueTool(venue_tool=venue_db)

        self.agent = Agent(
            role="Campus Compliance Officer",
            goal="Ensure all events comply with LBS policies and venue regulations",
            backstory="""
            You are the guardian of LBS event policies with encyclopedic knowledge
            of venue rules, licensing requirements, and safety regulations.
            You know Sainsbury Theatre has teaching priority, alcohol needs 30-day notice,
            and external speakers require security clearance. You've prevented countless
            event disasters by catching compliance issues early. You're strict but helpful,
            always offering solutions when you spot problems.
            """,
            tools=[self.check_venue_tool, self.check_conflicts_tool, self.suggest_venue_tool],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )