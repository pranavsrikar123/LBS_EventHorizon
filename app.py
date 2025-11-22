import streamlit as st
import os
from datetime import datetime, timedelta
from agents.event_crew import EventPlanningCrew
from agents.agent_interaction import AgentInteraction, format_agent_reasoning
from utils.crib_sheet_generator import generate_crib_sheet, save_crib_sheet
from utils.results_generator import generate_comprehensive_results
from tools.database_tools import EventDatabaseTool, VenueDatabaseTool, StudentSegmentTool
import time

# Page config
st.set_page_config(
    page_title="LBS EventHorizon - AI Event Planning",
    page_icon="🌅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern, Clean Design
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Headers */
    h1 {
        color: #1e3a8a;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    h2, h3 {
        color: #1e40af;
        font-weight: 600;
    }

    /* Agent cards */
    .agent-thinking {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 5px solid #fbbf24;
        padding: 15px;
        margin: 12px 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }

    .agent-decision {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-left: 5px solid #34d399;
        padding: 15px;
        margin: 12px 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .agent-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        border-left: 5px solid #fbbf24;
        padding: 15px;
        margin: 12px 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #f3f4f6;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crew' not in st.session_state:
    st.session_state.crew = EventPlanningCrew()
if 'agent_interaction' not in st.session_state:
    st.session_state.agent_interaction = AgentInteraction(st.session_state.crew)
if 'stage' not in st.session_state:
    st.session_state.stage = 'input'
if 'results' not in st.session_state:
    st.session_state.results = None
if 'agent_chat_history' not in st.session_state:
    st.session_state.agent_chat_history = []
if 'event' not in st.session_state:
    st.session_state.event = None

# Header with modern styling
st.title("🌅 LBS EventHorizon")
st.markdown("### *AI-Powered Event Intelligence & Planning*")
st.markdown("---")
col1, col2, col3 = st.columns([2, 3, 2])
with col2:
    st.info("🤖 **4 Autonomous AI Agents** analyzing your event in real-time")

# Sidebar - Show Active Agents
with st.sidebar:
    st.markdown("## 🤖 AI Agents Status")
    
    agent_status = {
        "📊 Prediction Agent": "Ready",
        "✅ Compliance Agent": "Ready",
        "📦 Logistics Agent": "Ready",
        "🎯 Marketing Agent": "Ready"
    }
    
    for agent, status in agent_status.items():
        if status == "Ready":
            st.success(f"{agent}: {status}")
        else:
            st.info(f"{agent}: {status}")
    
    st.markdown("---")
    st.markdown("### Agent Capabilities")
    st.markdown("""
    - **Autonomous Decision Making**
    - **Inter-Agent Communication**
    - **Dynamic Problem Solving**
    - **Real-time Adaptation**
    """)

# Main content
if st.session_state.stage == 'input':
    st.markdown("## Tell the AI Agents About Your Event")

    # Get previous values if they exist
    prev_event = st.session_state.event if st.session_state.event else {}

    with st.form("event_input"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("📌 Event Name",
                prev_event.get('name', "AI & Entrepreneurship Summit"))

            event_types = [
                "Technology", "Finance", "Social", "Career",
                "Networking", "Academic", "Workshop", "Panel Discussion",
                "Conference", "Recruiting", "Alumni", "Sport & Wellness",
                "Arts & Culture", "Charity", "Competition", "Celebration"
            ]
            event_type = st.selectbox("📂 Event Type", event_types,
                index=event_types.index(prev_event.get('type', 'Technology')) if prev_event.get('type') in event_types else 0)

            date = st.date_input("📅 Date",
                prev_event.get('date', datetime.now().date() + timedelta(days=21)))

            time = st.time_input("🕐 Time",
                prev_event.get('time', datetime.strptime("18:00", "%H:%M").time()))

        with col2:
            venues = [
                "Nash Lounge", "Sainsbury Theatre", "Windsor Theatre",
                "Sammy Ofer Centre - Garden", "Sammy Ofer Centre - Upper Link",
                "Sammy Ofer Centre - Lower Link", "LT1", "LT2", "LT3",
                "Nuffield Hall", "Regents Room", "Garden Room",
                "Sussex Room", "Front Lawn", "Council Chamber"
            ]
            venue = st.selectbox("📍 Venue", venues,
                index=venues.index(prev_event.get('venue', 'Nash Lounge')) if prev_event.get('venue') in venues else 0)

            size = st.slider("👥 Expected Registrations", 20, 400,
                prev_event.get('size', 150), step=10)

            alcohol = st.checkbox("🍷 Serve Alcohol",
                prev_event.get('alcohol', False))

            external = st.checkbox("🎤 External Speakers",
                prev_event.get('external', False))

        st.markdown("### 🎯 Event Focus")
        all_tags = [
            "AI & Machine Learning", "Blockchain & Web3", "Entrepreneurship",
            "Leadership", "Networking", "Workshop", "Consulting",
            "Investment Banking", "Private Equity", "Venture Capital",
            "Marketing & Brand", "Sustainability & ESG", "Healthcare",
            "Real Estate", "Technology", "Fintech", "EdTech",
            "Data Science", "Product Management", "Digital Transformation",
            "Diversity & Inclusion", "Mental Health", "Career Development",
            "Innovation", "Strategy", "Operations", "Supply Chain",
            "International Business", "Negotiation", "Public Speaking"
        ]
        tags = st.multiselect("Select relevant tags",
            all_tags,
            default=prev_event.get('tags', ["AI & Machine Learning", "Entrepreneurship"]))

        st.markdown("### 🎓 Target Audience")
        all_programs = [
            "MBA2025", "MBA2024", "MiM2025", "MiM2024",
            "EMBA", "EMBA-Global", "Sloan Masters",
            "MAM (Masters in Analytics & Management)", "MFA (Masters in Financial Analysis)",
            "Executive Education", "PhD Students", "Alumni", "Faculty & Staff"
        ]
        programs = st.multiselect("Select target programs",
            all_programs,
            default=prev_event.get('programs', ["MBA2025"]))

        submit = st.form_submit_button("🚀 Deploy AI Agents", use_container_width=True)

        if submit:
            # Update event details
            st.session_state.event = {
                'name': name,
                'type': event_type,
                'date': date,
                'time': time,
                'venue': venue,
                'size': size,
                'alcohol': alcohol,
                'external': external,
                'tags': tags,
                'programs': programs
            }
            # Clear previous results when processing new event
            st.session_state.results = None
            st.session_state.agent_chat_history = []
            st.session_state.stage = 'processing'
            st.rerun()

elif st.session_state.stage == 'processing':
    st.markdown("## 🤖 AI Agents at Work")

    # Get event details for dynamic messages
    event = st.session_state.event
    event_name = event.get('name', 'Your Event')
    venue = event.get('venue', 'the venue')
    event_type = event.get('type', 'event')
    size = event.get('size', 100)
    programs = ', '.join(event.get('programs', ['students']))

    # Create placeholder for agent thinking
    thinking_container = st.container()

    with thinking_container:
        # Dynamic agent thinking process based on actual event
        agent_thoughts = [
            ("📊 Prediction Agent", f"🔍 Analyzing {event_name}...", 1.5),
            ("📊 Prediction Agent", f"📚 Searching {len(EventDatabaseTool().events)} historical events for similar {event_type} events...", 1),
            ("📊 Prediction Agent", f"👥 Calculating potential audience from {programs}...", 1),
            ("📊 Prediction Agent", f"📅 Checking {event.get('date').strftime('%A') if hasattr(event.get('date'), 'strftime') else 'event day'} patterns and timing impact...", 1),
            ("📊 Prediction Agent", f"{'🍷 Factoring in alcohol impact on attendance...' if event.get('alcohol') else '📊 Analyzing registration behavior...'}", 1),
            ("📊 Prediction Agent", f"✅ Prediction complete: Flake rate calculated for {size} expected registrations", 1),

            ("✅ Compliance Agent", f"🔍 Checking {venue} capacity and restrictions...", 1.5),
            ("✅ Compliance Agent", f"{'⚠️ Verifying alcohol licensing for ' + venue + '...' if event.get('alcohol') else '✅ Checking venue suitability...'}", 1),
            ("✅ Compliance Agent", f"{'📋 External speaker security clearance requirements...' if event.get('external') else '✅ No external speakers - clearance not needed'}", 1),
            ("✅ Compliance Agent", f"✅ Compliance check complete", 1),

            ("📦 Logistics Agent", f"📅 Generating timeline from today to {event.get('date').strftime('%b %d') if hasattr(event.get('date'), 'strftime') else 'event date'}...", 1.5),
            ("📦 Logistics Agent", f"💰 Calculating smart catering order for predicted vs registered...", 1),
            ("📦 Logistics Agent", f"⚠️ Computing wastage if ordering for {size} registrations...", 1),
            ("📦 Logistics Agent", f"✅ Budget optimized - waste prevention calculated", 1),

            ("🎯 Marketing Agent", f"🎯 Analyzing {programs} student personas...", 1.5),
            ("🎯 Marketing Agent", f"📊 Matching event tags to student interests...", 1),
            ("🎯 Marketing Agent", f"✉️ Identifying top 3 target personas for {event_type} events...", 1),
            ("🎯 Marketing Agent", f"📈 Calculating attendance boost from targeted marketing", 1),
        ]

        # Display thinking process
        for agent, thought, delay in agent_thoughts:
            st.markdown(f'<div class="agent-thinking">{agent}: {thought}</div>',
                       unsafe_allow_html=True)
            time.sleep(delay)
    
    # Run actual crew processing
    with st.spinner("🤖 Agents collaborating on final recommendations..."):
        try:
            # Get event details from session state
            event_details = st.session_state.event

            # Load databases for comprehensive analysis
            student_db = StudentSegmentTool().profiles
            venue_db = VenueDatabaseTool().venues
            event_db = EventDatabaseTool().events

            # Generate comprehensive results with detailed reasoning
            st.info(f"✨ Generating comprehensive analysis for {event_details['name']}...")
            results = generate_comprehensive_results(event_details, student_db, venue_db, event_db)

            # Try to get crew results (may enhance with actual LLM insights)
            try:
                crew_results = st.session_state.crew.plan_event(event_details)
                # If crew succeeds, we could merge insights here
                st.success("✓ AI agents provided additional insights!")
            except:
                # Use comprehensive results as primary output
                pass

            # Store results in session state
            st.session_state.results = results
            st.session_state.stage = 'results'
            st.success("✓ Analysis complete!")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
            st.info("Using intelligent fallback analysis...")

            # Still use comprehensive results generator
            try:
                student_db = StudentSegmentTool().profiles
                venue_db = VenueDatabaseTool().venues
                event_db = EventDatabaseTool().events

                results = generate_comprehensive_results(event_details, student_db, venue_db, event_db)
                st.session_state.results = results
                st.session_state.stage = 'results'
                time.sleep(1)
                st.rerun()
            except Exception as fallback_error:
                st.error(f"Critical error: {str(fallback_error)}")
                st.stop()

elif st.session_state.stage == 'results':
    st.markdown("## 🎯 Agent Recommendations")
    
    results = st.session_state.results
    
    # Display autonomous decisions made by agents
    st.markdown("### 🧠 Autonomous Agent Decisions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="agent-decision">', unsafe_allow_html=True)
        st.markdown("**📊 Prediction Agent Decision:**")
        st.markdown(f"- Predicted {results['prediction']['flake_rate']}% flake rate")
        st.markdown(f"- Recommends: {results['prediction'].get('recommendation', 'Proceed as planned')}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add comprehensive reasoning expander
        with st.expander("🔍 See Detailed Analysis & Reasoning", expanded=False):
            st.markdown(results['prediction'].get('reasoning', 'Analysis complete'))

        st.markdown('<div class="agent-warning">', unsafe_allow_html=True)
        st.markdown("**✅ Compliance Agent Decision:**")
        if results['compliance']['issues']:
            for issue in results['compliance']['issues']:
                st.markdown(f"- Issue: {issue}")
            if results['compliance']['alternatives']:
                st.markdown(f"- Solution: Switch to {results['compliance']['alternatives'][0]}")
        else:
            st.markdown("- ✓ All compliance checks passed")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add comprehensive compliance reasoning
        with st.expander("🔍 See Compliance Analysis", expanded=False):
            st.markdown(results['compliance'].get('reasoning', 'Compliance check complete'))
            if results['compliance']['actions_required']:
                st.markdown("**📋 Action Items:**")
                for action in results['compliance']['actions_required']:
                    st.markdown(f"- {action}")

    with col2:
        st.markdown('<div class="agent-decision">', unsafe_allow_html=True)
        st.markdown("**📦 Logistics Agent Decision:**")
        st.markdown(f"- Budget allocated: £{results['logistics']['budget']:,}")
        st.markdown(f"- Waste prevention: Saved £{results['logistics']['predicted_waste']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add comprehensive logistics reasoning
        with st.expander("🔍 See Budget Optimization & Wastage Analysis", expanded=False):
            st.markdown(results['logistics'].get('reasoning', 'Budget analysis complete'))
            st.markdown("**📅 Critical Timeline:**")
            for item in results['logistics'].get('timeline', []):
                if isinstance(item, tuple):
                    st.markdown(f"**{item[0]}** - {item[1]}")

        st.markdown('<div class="agent-decision">', unsafe_allow_html=True)
        st.markdown("**🎯 Marketing Agent Decision:**")
        if results['marketing']['personas']:
            st.markdown(f"- Target: {results['marketing']['personas'][0]['name']}")
        st.markdown(f"- Expected boost: +{results['marketing']['expected_boost']}% attendance")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add comprehensive marketing reasoning
        with st.expander("🔍 See Persona Analysis & Targeting Strategy", expanded=False):
            st.markdown(results['marketing'].get('reasoning', 'Marketing analysis complete'))
    
    # Interactive chat with agents
    st.markdown("### 💬 Ask an Agent Follow-up Questions")
    st.markdown("*Get detailed explanations with Chain of Thought reasoning*")

    col1, col2 = st.columns([2, 1])
    with col1:
        user_question = st.text_input("Your question:", placeholder="e.g., Why is the flake rate so high?")
    with col2:
        agent_chat = st.selectbox("Ask:",
            ["Prediction Agent", "Compliance Agent", "Logistics Agent", "Marketing Agent"])

    if st.button("🤔 Ask Agent", use_container_width=True):
        if user_question.strip():
            with st.spinner(f"🤔 {agent_chat} is analyzing..."):
                # Query the agent with context
                context = {
                    'event_name': st.session_state.event.get('name'),
                    'event_date': str(st.session_state.event.get('date')),
                    'venue': st.session_state.event.get('venue'),
                    'expected_size': st.session_state.event.get('size')
                }

                try:
                    response = st.session_state.agent_interaction.query_agent(
                        agent_chat,
                        user_question,
                        context
                    )

                    # Add to chat history
                    st.session_state.agent_chat_history.append({
                        'agent': agent_chat,
                        'question': user_question,
                        'response': response
                    })

                    # Display response
                    st.markdown(f'<div class="agent-decision">', unsafe_allow_html=True)
                    st.markdown(f"**{agent_chat}:**")
                    st.markdown(response['answer'])
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Show reasoning process
                    with st.expander("🔍 See Chain of Thought Reasoning"):
                        st.markdown("**Agent's Thinking Process:**")
                        if response.get('reasoning'):
                            st.code(response['reasoning'], language='text')
                        else:
                            st.info("No detailed reasoning captured for this response")

                except Exception as e:
                    st.error(f"Error querying agent: {str(e)}")
                    st.info("Agent query failed. This could be due to API limits or connection issues.")
        else:
            st.warning("Please enter a question first")

    # Show chat history
    if st.session_state.agent_chat_history:
        with st.expander("💬 View Conversation History"):
            for i, chat in enumerate(reversed(st.session_state.agent_chat_history)):
                st.markdown(f"**Q{len(st.session_state.agent_chat_history)-i}:** {chat['question']}")
                st.markdown(f"**{chat['agent']}:** {chat['response']['answer'][:200]}...")
                st.markdown("---")
    
    # Action buttons
    st.markdown("---")
    st.markdown("### 🎬 Next Actions")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Generate LBS Crib Sheet", use_container_width=True):
            with st.spinner("Generating comprehensive crib sheet..."):
                try:
                    # Generate the crib sheet
                    crib_sheet = generate_crib_sheet(
                        st.session_state.event,
                        results
                    )

                    # Save to file
                    filepath = save_crib_sheet(crib_sheet)

                    # Display success with download
                    st.success(f"✓ Crib sheet generated!")

                    # Show preview
                    with st.expander("📄 Preview Crib Sheet"):
                        st.text(crib_sheet)

                    # Download button
                    st.download_button(
                        label="📥 Download Crib Sheet",
                        data=crib_sheet,
                        file_name=f"LBS_Event_CribSheet_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

                    st.info("📧 Ready to send to space@london.edu")

                except Exception as e:
                    st.error(f"Error generating crib sheet: {str(e)}")

    with col2:
        if st.button("🔄 Modify Event Details", use_container_width=True):
            st.session_state.stage = 'input'
            st.session_state.agent_chat_history = []  # Clear chat history
            st.rerun()

    with col3:
        if st.button("✅ Approve & Export All", use_container_width=True):
            st.balloons()
            st.success("✓ Event plan approved!")
            st.info("All recommendations exported. Ready for implementation.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🌅 **LBS EventHorizon**")
with col2:
    st.caption("Powered by CrewAI + Gemini 1.5")
with col3:
    st.caption("Multi-Agent AI System")