"""
Generate comprehensive, realistic event analysis results with detailed reasoning
"""
from datetime import datetime, timedelta
from typing import Dict, List
import random


class EventAnalyzer:
    """Generate detailed event analysis with step-by-step reasoning"""

    def __init__(self, event_details: Dict, student_db, venue_db, event_db):
        self.event = event_details
        self.students = student_db
        self.venues = venue_db
        self.events = event_db

    def analyze_prediction(self) -> Dict:
        """
        Comprehensive prediction with detailed breakdown
        """
        # Step 1: Calculate potential audience pool
        programs = self.event.get('programs', [])
        tags = self.event.get('tags', [])
        event_type = self.event.get('type', '')

        # Estimate interested students per program
        program_sizes = {
            'MBA2025': 500, 'MBA2024': 480, 'MiM2025': 180, 'MiM2024': 170,
            'EMBA': 120, 'EMBA-Global': 90, 'Sloan Masters': 55,
            'MAM (Masters in Analytics & Management)': 65,
            'MFA (Masters in Financial Analysis)': 45,
            'Executive Education': 200, 'PhD Students': 80,
            'Alumni': 1000, 'Faculty & Staff': 150
        }

        # Calculate total pool based on programs
        total_pool = sum(program_sizes.get(p, 100) for p in programs)

        # Interest rate based on event type and tags
        interest_rates = {
            'Finance': 0.35, 'Career': 0.40, 'Recruiting': 0.45,
            'Technology': 0.25, 'Entrepreneurship': 0.20,
            'Social': 0.30, 'Networking': 0.35, 'Workshop': 0.15,
            'Academic': 0.20, 'Panel Discussion': 0.25
        }
        interest_rate = interest_rates.get(event_type, 0.25)

        # Adjust for tags
        if 'Investment Banking' in tags or 'Private Equity' in tags:
            interest_rate += 0.10
        if 'AI & Machine Learning' in tags or 'Data Science' in tags:
            interest_rate += 0.08

        interested_pool = int(total_pool * interest_rate)

        # Step 2: Calculate expected registrations
        # Day of week impact
        day_impact = {
            'Monday': 0.70, 'Tuesday': 0.85, 'Wednesday': 0.90,
            'Thursday': 0.95, 'Friday': 0.60, 'Saturday': 0.55, 'Sunday': 0.40
        }
        event_date = self.event.get('date')
        day_of_week = event_date.strftime('%A') if isinstance(event_date, datetime) else 'Thursday'
        day_factor = day_impact.get(day_of_week, 0.80)

        # Time impact
        event_time = self.event.get('time')
        if isinstance(event_time, str):
            hour = int(event_time.split(':')[0])
        else:
            hour = event_time.hour if event_time else 18

        time_factor = 1.0
        if hour < 12:
            time_factor = 0.70  # Morning events
        elif 12 <= hour < 14:
            time_factor = 0.95  # Lunch events - popular
        elif 14 <= hour < 17:
            time_factor = 0.75  # Afternoon
        elif 17 <= hour < 20:
            time_factor = 1.0   # Evening - prime time
        else:
            time_factor = 0.85  # Late evening

        # Alcohol impact
        alcohol_boost = 1.15 if self.event.get('alcohol', False) else 1.0

        # External speakers boost
        speaker_boost = 1.12 if self.event.get('external', False) else 1.0

        expected_registrations = int(interested_pool * day_factor * time_factor * alcohol_boost * speaker_boost)

        # Cap at venue capacity
        venue_name = self.event.get('venue', '')
        venue_info = self.venues.get(venue_name, {})
        venue_capacity = venue_info.get('capacity', 200)
        expected_registrations = min(expected_registrations, int(venue_capacity * 1.1))  # Allow 10% overbook

        # Step 3: Calculate flake rate
        base_flake_rate = 0.20  # 20% base

        # Day of week adjustment
        if day_of_week == 'Friday':
            base_flake_rate += 0.18
        elif day_of_week == 'Thursday':
            base_flake_rate -= 0.10
        elif day_of_week in ['Saturday', 'Sunday']:
            base_flake_rate += 0.05

        # Time adjustment
        if hour >= 20:
            base_flake_rate += 0.12  # Late events
        elif 12 <= hour < 14:
            base_flake_rate -= 0.08  # Lunch events

        # Event type adjustment
        if event_type in ['Recruiting', 'Career']:
            base_flake_rate -= 0.12  # High commitment
        elif event_type == 'Social':
            base_flake_rate += 0.08
        elif event_type in ['Competition', 'Celebration']:
            base_flake_rate -= 0.10

        # Alcohol adjustment
        if self.event.get('alcohol', False):
            base_flake_rate -= 0.08

        # Ensure reasonable bounds
        flake_rate = max(0.05, min(0.65, base_flake_rate))

        # Step 4: Calculate predicted attendance
        predicted_attendance = int(expected_registrations * (1 - flake_rate))

        # Detailed reasoning
        reasoning = f"""
**STEP 1: AUDIENCE POOL ANALYSIS**
Target Programs: {', '.join(programs)}
Total Student Pool: {total_pool:,} students across selected programs

Interest Analysis:
- Event Type "{event_type}": Base interest rate {interest_rate*100:.0f}%
- Tag Adjustments: {'+8-10%' if any(t in tags for t in ['AI & Machine Learning', 'Investment Banking']) else '0%'}
- Interested Pool: {interested_pool:,} students

**STEP 2: REGISTRATION FORECAST**
Day Impact: {day_of_week} = {day_factor*100:.0f}% registration rate
Time Impact: {hour}:00 = {time_factor*100:.0f}% optimal timing
{'Alcohol Boost: +15%' if self.event.get('alcohol') else 'No Alcohol: 0%'}
{'External Speakers: +12%' if self.event.get('external') else 'Internal Only: 0%'}

Formula: {interested_pool} × {day_factor:.2f} × {time_factor:.2f} × {alcohol_boost:.2f} × {speaker_boost:.2f}
Predicted Registrations: {expected_registrations:,}

**STEP 3: FLAKE RATE CALCULATION**
Base Flake Rate: 20%
- {day_of_week} adjustment: {'+18%' if day_of_week == 'Friday' else '-10%' if day_of_week == 'Thursday' else '0%'}
- Time {hour}:00 adjustment: {'-8%' if 12 <= hour < 14 else '+12%' if hour >= 20 else '0%'}
- Event type "{event_type}": {'-12%' if event_type in ['Recruiting', 'Career'] else '+8%' if event_type == 'Social' else '0%'}
- {'Alcohol: -8%' if self.event.get('alcohol') else 'No alcohol: 0%'}

Final Flake Rate: {flake_rate*100:.0f}%

**STEP 4: FINAL PREDICTION**
{expected_registrations:,} registrations × (1 - {flake_rate:.2%}) = {predicted_attendance:,} actual attendees
"""

        # Recommendations
        recommendations = []
        if flake_rate > 0.30:
            if day_of_week == 'Friday':
                recommendations.append("⚠️ Friday events have high flake rates. Consider moving to Thursday.")
            if hour >= 20:
                recommendations.append("⚠️ Late evening timing increases no-shows. Consider 18:00-19:30.")
            if not self.event.get('alcohol'):
                recommendations.append("💡 Adding alcohol could reduce flake rate by 8%.")

        if event_type == 'Social' and not self.event.get('alcohol'):
            recommendations.append("💡 Social events benefit significantly from alcohol service.")

        confidence = 'HIGH' if flake_rate < 0.25 else 'MEDIUM' if flake_rate < 0.40 else 'LOW'

        return {
            'interested_pool': interested_pool,
            'expected_registration': expected_registrations,
            'predicted_attendance': predicted_attendance,
            'flake_rate': int(flake_rate * 100),
            'confidence': confidence,
            'reasoning': reasoning.strip(),
            'recommendations': recommendations,
            'breakdown': {
                'total_pool': total_pool,
                'interest_rate': interest_rate,
                'day_factor': day_factor,
                'time_factor': time_factor,
                'alcohol_boost': alcohol_boost,
                'speaker_boost': speaker_boost
            }
        }

    def analyze_compliance(self, prediction: Dict) -> Dict:
        """Comprehensive compliance check with detailed reasoning"""
        venue_name = self.event.get('venue', '')
        venue_info = self.venues.get(venue_name, {})

        issues = []
        actions_required = []
        alternatives = []

        # Check capacity
        required_capacity = prediction['expected_registration']
        venue_capacity = venue_info.get('capacity', 200)

        if required_capacity > venue_capacity:
            issues.append(f"Capacity issue: {venue_name} holds {venue_capacity}, you need {required_capacity}")
            # Find alternatives
            for v_name, v_info in self.venues.items():
                if v_info.get('capacity', 0) >= required_capacity:
                    alternatives.append(f"{v_name} (capacity: {v_info['capacity']})")

        # Check alcohol
        wants_alcohol = self.event.get('alcohol', False)
        alcohol_permitted = venue_info.get('alcohol_permitted', False)

        if wants_alcohol and not alcohol_permitted:
            issues.append(f"❌ {venue_name} does NOT permit alcohol")
            actions_required.append("Choose a different venue or remove alcohol requirement")
            # Find alcohol-friendly alternatives
            for v_name, v_info in self.venues.items():
                if v_info.get('alcohol_permitted') and v_info.get('capacity', 0) >= required_capacity:
                    if v_name not in alternatives:
                        alternatives.append(f"{v_name} (capacity: {v_info['capacity']}, alcohol permitted)")

        if wants_alcohol and alcohol_permitted:
            event_date = self.event.get('date')
            days_until = (event_date - datetime.now().date()).days if hasattr(event_date, '__sub__') else 30

            if days_until < 30:
                issues.append(f"⚠️ Alcohol requires 30-day advance notice. You have {days_until} days.")
                actions_required.append(f"Contact cateringevents@london.edu IMMEDIATELY")
            else:
                actions_required.append(f"Email cateringevents@london.edu by {(event_date - timedelta(days=30)).strftime('%B %d')} for alcohol approval")

        # External speakers
        if self.event.get('external', False):
            actions_required.append("Submit external speaker details for security clearance (14 days before event)")
            actions_required.append("Prepare speaker bio, photo, and emergency contact info")

        # Check booking lead time
        lead_time_required = venue_info.get('booking_lead_time', 7)
        actions_required.append(f"Book venue at least {lead_time_required} days in advance")

        venue_suitable = len(issues) == 0

        reasoning = f"""
**VENUE ANALYSIS: {venue_name}**
Capacity: {venue_capacity} (Required: {required_capacity})
Alcohol Permitted: {'✅ Yes' if alcohol_permitted else '❌ No'}
AV Equipment: {'✅ Available' if venue_info.get('av_equipped') else '❌ Not available'}
Booking Lead Time: {lead_time_required} days
Cost: {venue_info.get('cost_indicator', 'N/A')}

**COMPLIANCE CHECK:**
{'✅ All checks passed!' if venue_suitable else '❌ Issues found - see below'}
"""

        return {
            'venue_suitable': venue_suitable,
            'issues': issues,
            'alternatives': alternatives[:3],
            'actions_required': actions_required,
            'reasoning': reasoning,
            'venue_info': venue_info
        }

    def analyze_logistics(self, prediction: Dict, compliance: Dict) -> Dict:
        """Detailed logistics planning with waste calculation"""
        event_date = self.event.get('date')
        expected_reg = prediction['expected_registration']
        predicted_attendance = prediction['predicted_attendance']

        # Calculate actual dates for timeline
        if hasattr(event_date, 'strftime'):
            t_30 = event_date - timedelta(days=30)
            t_21 = event_date - timedelta(days=21)
            t_14 = event_date - timedelta(days=14)
            t_7 = event_date - timedelta(days=7)
            t_2 = event_date - timedelta(days=2)

            timeline = [
                (t_30.strftime('%b %d'), 'Submit alcohol request (if required)'),
                (t_21.strftime('%b %d'), 'Open event registration'),
                (t_14.strftime('%b %d'), 'External speaker security clearance due'),
                (t_7.strftime('%b %d'), 'Send first reminder email'),
                (t_2.strftime('%b %d'), 'Finalize headcount with catering'),
                (event_date.strftime('%b %d'), '🎉 Event Day!')
            ]
        else:
            timeline = [
                ('T-30', 'Submit alcohol request'),
                ('T-21', 'Open registration'),
                ('T-14', 'Speaker clearance'),
                ('T-7', 'First reminder'),
                ('T-2', 'Final headcount')
            ]

        # Budget calculation
        cost_per_head = 35 if self.event.get('alcohol') else 25
        venue_cost = {
            '£': 200, '££': 500, '£££': 1000, '££££': 2000
        }.get(compliance.get('venue_info', {}).get('cost_indicator', '££'), 500)

        av_cost = 300 if compliance.get('venue_info', {}).get('av_equipped') else 0

        # Wastage calculation - THE KEY INSIGHT
        if_order_for_registered = expected_reg * cost_per_head
        smart_order_for_predicted = predicted_attendance * cost_per_head
        waste_if_overorder = (expected_reg - predicted_attendance) * cost_per_head

        total_budget = smart_order_for_predicted + venue_cost + av_cost

        reasoning = f"""
**BUDGET OPTIMIZATION ANALYSIS**

Catering Strategy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Traditional Approach (Order for all registered):
- {expected_reg:,} registrations × £{cost_per_head} per person
- Total: £{if_order_for_registered:,}

⚠️ THE PROBLEM:
Based on {prediction['flake_rate']}% predicted flake rate, only {predicted_attendance:,} will actually attend.
- Unused meals: {expected_reg - predicted_attendance}
- Wasted food cost: {expected_reg - predicted_attendance} × £{cost_per_head} = £{waste_if_overorder:,}

✅ SMART APPROACH (Order for predicted attendance):
- {predicted_attendance:,} predicted attendees × £{cost_per_head}
- Catering cost: £{smart_order_for_predicted:,}
- **SAVINGS: £{waste_if_overorder:,}**

Additional Costs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Venue: £{venue_cost:,} ({compliance.get('venue_info', {}).get('cost_indicator', '££')})
{'AV Equipment: £' + f'{av_cost:,}' if av_cost > 0 else 'AV: Included'}

**TOTAL SMART BUDGET: £{total_budget:,}**

💡 Key Insight: Order for {predicted_attendance}, not {expected_reg}
This prevents £{waste_if_overorder:,} in wasted catering!
"""

        return {
            'timeline': timeline,
            'budget': total_budget,
            'predicted_waste': waste_if_overorder,
            'catering_cost': smart_order_for_predicted,
            'venue_cost': venue_cost,
            'av_cost': av_cost,
            'reasoning': reasoning,
            'breakdown': {
                'cost_per_head': cost_per_head,
                'smart_order_quantity': predicted_attendance,
                'waste_if_overorder': waste_if_overorder
            }
        }

    def analyze_marketing(self, prediction: Dict) -> Dict:
        """Marketing strategy with actual persona matching"""
        event_type = self.event.get('type', '')
        tags = self.event.get('tags', [])
        programs = self.event.get('programs', [])

        # Match to actual personas from database
        persona_scores = {}
        for persona in self.students:
            score = 0
            persona_id = persona.get('persona_id', '')

            # Type matching
            if event_type in persona.get('preferred_event_types', []):
                score += 30

            # Tag matching
            persona_tags = [persona.get('description', '').lower()]
            for tag in tags:
                if any(keyword in tag.lower() for keyword in ['tech', 'ai', 'data']) and 'tech' in persona_id:
                    score += 15
                if any(keyword in tag.lower() for keyword in ['finance', 'banking', 'investment']) and 'finance' in persona_id:
                    score += 15
                if 'entrepreneur' in tag.lower() and 'entrepreneur' in persona_id:
                    score += 15

            # Program matching
            persona_programs = persona.get('programs', [])
            common_programs = set(programs) & set(persona_programs)
            score += len(common_programs) * 10

            if score > 0:
                persona_scores[persona_id] = {
                    'score': score,
                    'persona': persona
                }

        # Get top 3 personas
        top_personas = sorted(persona_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:3]

        personas = []
        for persona_id, data in top_personas:
            p = data['persona']
            personas.append({
                'name': p.get('description', 'Unknown Persona'),
                'id': persona_id,
                'conversion': f"{p.get('conversion_rate', 70)}%",
                'avg_attendance': p.get('avg_attendance_rate', 70),
                'motivators': ', '.join(p.get('motivators', [])[:2])
            })

        # If we don't have enough, add generic ones
        while len(personas) < 3:
            personas.append({
                'name': 'General Student Population',
                'conversion': '55%',
                'avg_attendance': 55,
                'motivators': 'Learning, Networking'
            })

        expected_boost = sum(p['avg_attendance'] for p in personas) // len(personas) - 50

        reasoning = f"""
**TARGET AUDIENCE IDENTIFICATION**

Based on event type "{event_type}" and tags, identified {len(personas)} key personas:

1. **{personas[0]['name']}**
   - Conversion Rate: {personas[0]['conversion']}
   - Key Motivators: {personas[0]['motivators']}

2. **{personas[1]['name']}**
   - Conversion Rate: {personas[1]['conversion']}
   - Key Motivators: {personas[1]['motivators']}

3. **{personas[2]['name']}**
   - Conversion Rate: {personas[2]['conversion']}
   - Key Motivators: {personas[2]['motivators']}

**EXPECTED IMPACT:**
Targeted marketing to these personas can boost attendance by {expected_boost}% vs. generic approach.

**RECOMMENDATION:**
Create personalized email campaigns for each persona type, emphasizing their specific motivators.
"""

        return {
            'personas': personas,
            'expected_boost': expected_boost,
            'reasoning': reasoning
        }


def generate_comprehensive_results(event_details: Dict, students, venues, events) -> Dict:
    """Generate all results with comprehensive reasoning"""
    analyzer = EventAnalyzer(event_details, students, venues, events)

    prediction = analyzer.analyze_prediction()
    compliance = analyzer.analyze_compliance(prediction)
    logistics = analyzer.analyze_logistics(prediction, compliance)
    marketing = analyzer.analyze_marketing(prediction)

    return {
        'prediction': prediction,
        'compliance': compliance,
        'logistics': logistics,
        'marketing': marketing
    }
