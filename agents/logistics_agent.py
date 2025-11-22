from crewai import Agent
from crewai.tools import BaseTool
from tools.booking_tools import BookingSystemTool, WasteCalculator
from pydantic import Field, ConfigDict


# Wrapper tools for CrewAI compatibility
class CreateBookingTool(BaseTool):
    name: str = "create_booking"
    description: str = "Create room booking with requirements"

    booking_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, venue: str, date: str, requirements: dict) -> str:
        return self.booking_tool.create_booking(venue, date, requirements)


class CalculateWasteTool(BaseTool):
    name: str = "calculate_waste"
    description: str = "Calculate predicted financial waste"

    waste_calc: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, registered: int, predicted: int, costs: dict) -> str:
        return self.waste_calc.predict_waste(registered, predicted, costs)


class GenerateTimelineTool(BaseTool):
    name: str = "generate_timeline"
    description: str = "Create critical deadlines timeline"

    booking_tool: object = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, event_date: str, requirements: dict) -> str:
        return self.booking_tool.generate_timeline(event_date, requirements)


class LogisticsAgent:
    def __init__(self, llm):
        self.llm = llm
        booking_system = BookingSystemTool()
        waste_calculator = WasteCalculator()

        # Initialize wrapper tools
        self.booking_tool_wrapper = CreateBookingTool(booking_tool=booking_system)
        self.waste_tool = CalculateWasteTool(waste_calc=waste_calculator)
        self.timeline_tool = GenerateTimelineTool(booking_tool=booking_system)

        self.agent = Agent(
            role="Event Operations Manager",
            goal="Optimize event logistics to minimize waste and maximize efficiency",
            backstory="""
            You're the operational genius who's saved LBS £500K in event costs.
            You know that ordering catering for registered vs predicted attendance
            can waste thousands. You've mastered the art of porter team coordination,
            AV setup timing, and backup planning. Your superpower is predicting
            and preventing operational waste before it happens.
            """,
            tools=[self.booking_tool_wrapper, self.waste_tool, self.timeline_tool],
            llm=llm,
            verbose=True
        )