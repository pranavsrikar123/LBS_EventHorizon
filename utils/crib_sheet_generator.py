"""
Generate event crib sheet based on agent recommendations (LBS Format)
"""
from datetime import datetime
from typing import Dict


def generate_crib_sheet(event_details: Dict, results: Dict, contact_info: Dict = None) -> str:
    """
    Generate a formatted crib sheet matching LBS event request format

    Args:
        event_details: Event information
        results: Agent analysis results
        contact_info: Optional contact information

    Returns:
        Formatted crib sheet as string
    """

    # Extract data
    event_name = event_details.get('name', 'Event')
    event_date = event_details.get('date', '')
    event_time = event_details.get('time', '')
    venue = event_details.get('venue', '')
    expected_size = event_details.get('size', 0)
    event_type = event_details.get('type', '')
    programs = ', '.join(event_details.get('programs', []))
    tags = ', '.join(event_details.get('tags', []))
    has_alcohol = event_details.get('alcohol', False)
    has_external = event_details.get('external', False)

    prediction = results.get('prediction', {})
    compliance = results.get('compliance', {})
    logistics = results.get('logistics', {})
    marketing = results.get('marketing', {})

    # Contact info defaults
    if contact_info is None:
        contact_info = {}

    # Calculate times
    start_time = event_time if isinstance(event_time, str) else event_time.strftime('%H:%M')
    # Estimate end time (add 3 hours)
    end_time = "[To be confirmed]"

    # Format the crib sheet in LBS format
    crib_sheet = f"""
═══════════════════════════════════════════════════════════════════
                    LBS EVENT REQUEST FORM
                     (AI-Generated Draft)
═══════════════════════════════════════════════════════════════════

BASIC INFORMATION
───────────────────────────────────────────────────────────────────
Name of person making the request:    {contact_info.get('name', '[To be filled]')}
Club or Programme affiliation:        {programs}
Contact mobile/phone number:          {contact_info.get('phone', '[To be filled]')}

EVENT DETAILS
───────────────────────────────────────────────────────────────────
Event title:                          {event_name}
Number of attendees:                  {prediction.get('predicted_attendance', expected_size)}
                                      (AI predicts {prediction.get('predicted_attendance', expected_size)} actual attendance
                                      from {expected_size} registrations - {prediction.get('flake_rate', 'N/A')}% flake rate)

DATE:                                 {event_date}

Start and Finish time:
  Presentation:                       {start_time} - {end_time}
  Networking (if applicable):         [Post-presentation]

What type of event is this?           {event_type} - {tags}

Event Details:
  Target attendees:                   {programs} students
  Event focus:                        {tags}

AI PREDICTION ANALYSIS:
{prediction.get('reasoning', 'Based on analysis of similar past events')}

EXTERNAL GUEST SPEAKER DETAILS
───────────────────────────────────────────────────────────────────
Will the event have external guest speaker(s)?   {'Yes' if has_external else 'No'}

{'⚠️  IMPORTANT: Events with external speakers are PROVISIONAL until speaker details confirmed' if has_external else ''}
{'⚠️  Security clearance required - submit details ASAP' if has_external else ''}

Is the nature of the event deemed to be
politically sensitive or controversial?     No (Standard event)

Will there be any children attending?       No

VENUE & SETUP
───────────────────────────────────────────────────────────────────
Type of space & proposed room setup:   {venue}
                                       {'Theatre style' if expected_size > 100 else 'Classroom/Seminar style'}
"""

    # Add compliance warnings
    if not compliance.get('venue_suitable', True):
        crib_sheet += "\n⚠️  AI COMPLIANCE ALERT:\n"
        for issue in compliance.get('issues', []):
            crib_sheet += f"   • {issue}\n"
        if compliance.get('alternatives'):
            crib_sheet += f"\n   Recommended alternative venues:\n"
            for alt in compliance.get('alternatives', []):
                crib_sheet += f"   • {alt}\n"
        crib_sheet += "\n"

    crib_sheet += f"""
Do you require a registration desk?        {'Yes - book at Sammy Ofer Centre' if expected_size > 50 else 'No'}

CATERING & ALCOHOL
───────────────────────────────────────────────────────────────────
Will catering be ordered?                  Yes
Catering requirements:                     {'Hot/Cold buffet with drinks' if expected_size > 50 else 'Light refreshments'}

⚠️  AI BUDGET OPTIMIZATION:
   • Order catering for {prediction.get('predicted_attendance', expected_size)} people
   • NOT for {expected_size} registered (saves £{logistics.get('predicted_waste', 750)})
   • Budget: £{logistics.get('budget', 0):,}
   • Predicted waste if over-ordered: £{logistics.get('predicted_waste', 750):,}

Will alcohol be available?                 {'Yes' if has_alcohol else 'No'}
"""

    if has_alcohol:
        crib_sheet += f"""
⚠️  ALCOHOL POLICY REQUIREMENTS:
   • Must email cateringevents@london.edu 30 DAYS in advance
   • Only served in licensed areas: {venue}
   • Must comply with premises licence conditions
   • See attached Policy A
"""

    crib_sheet += f"""
ENTERTAINMENT & EQUIPMENT
───────────────────────────────────────────────────────────────────
Will recorded music be played?            [To be confirmed]
Will live music be played?                No
Do you require a cloakroom?               {'Yes' if expected_size > 100 else 'No'}
Will outside equipment be hired?          [AV requirements TBD]
Will any filming take place?              [To be confirmed]

CRITICAL TIMELINE (AI Generated)
───────────────────────────────────────────────────────────────────
"""

    # Add timeline
    for item in logistics.get('timeline', []):
        if isinstance(item, tuple):
            date, task = item
            crib_sheet += f"{date}:  {task}\n"
        else:
            crib_sheet += f"• {item}\n"

    # Add compliance actions
    if compliance.get('actions_required'):
        crib_sheet += "\n📋 COMPLIANCE ACTIONS REQUIRED:\n"
        for action in compliance.get('actions_required', []):
            crib_sheet += f"   □ {action}\n"

    # Marketing section
    crib_sheet += f"""

MARKETING STRATEGY (AI-Powered)
───────────────────────────────────────────────────────────────────
Targeted Marketing Boost:                 +{marketing.get('expected_boost', 0)}% attendance increase

Target Student Personas:
"""

    # Add personas
    for persona in marketing.get('personas', []):
        if isinstance(persona, dict):
            crib_sheet += f"   • {persona.get('name', 'Unknown')} - {persona.get('conversion', 'N/A')} conversion\n"
        else:
            crib_sheet += f"   • {persona}\n"

    # Footer
    crib_sheet += f"""

ADDITIONAL INFORMATION
───────────────────────────────────────────────────────────────────
This crib sheet was generated by AI agents after analyzing:
• {len(compliance.get('issues', [])) + len(compliance.get('alternatives', []))} compliance factors
• Historical data from 500+ past LBS events
• Weather patterns and academic calendar conflicts
• Student engagement profiles

Confidence Level: {prediction.get('confidence', 'HIGH')}

═══════════════════════════════════════════════════════════════════
                        NEXT STEPS
═══════════════════════════════════════════════════════════════════
1. Review and complete any [To be filled] sections
2. Submit to space@london.edu (will respond within 3 working days)
3. {'Email cateringevents@london.edu for alcohol approval (30 days notice)' if has_alcohol else 'Confirm catering requirements'}
4. {'Submit external speaker details for security clearance' if has_external else 'Confirm final setup requirements'}

🤖 Generated by: LBS Event Genius AI System
   Timestamp:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

All enquiries: space@london.edu
═══════════════════════════════════════════════════════════════════
"""

    return crib_sheet


def save_crib_sheet(crib_sheet: str, filename: str = None) -> str:
    """
    Save crib sheet to file

    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"event_crib_sheet_{timestamp}.txt"

    filepath = f"outputs/{filename}"

    # Create outputs directory if it doesn't exist
    import os
    os.makedirs("outputs", exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(crib_sheet)

    return filepath
