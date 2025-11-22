import random
from typing import Dict


class BookingSystemTool:
    def create_booking(self, venue: str, date: str, requirements: Dict) -> str:
        """Create mock booking"""
        return f"Booking created: {venue} on {date}. Confirmation #LBS{random.randint(1000,9999)}"

    def generate_timeline(self, event_date: str, requirements: Dict) -> str:
        """Generate critical timeline"""
        timeline = [
            f"T-30 days: Submit alcohol request",
            f"T-21 days: Open registration",
            f"T-14 days: Speaker security clearance",
            f"T-7 days: First reminder",
            f"T-2 days: Final headcount",
            f"T-0: Event day"
        ]
        return "\n".join(timeline)


class WasteCalculator:
    def predict_waste(self, registered: int, predicted: int, costs: Dict) -> str:
        """Calculate predicted waste"""
        catering_waste = (registered - predicted) * costs.get('catering_per_head', 15)
        venue_waste = 200 if predicted < 50 else 0

        total = catering_waste + venue_waste

        return f"Predicted waste: £{total} (Catering: £{catering_waste}, Venue underuse: £{venue_waste})"
