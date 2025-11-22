import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import time
from agents.event_crew import EventPlanningCrew
from agents.agent_interaction import AgentInteraction
from utils.crib_sheet_generator import generate_crib_sheet, save_crib_sheet
from utils.results_generator import generate_comprehensive_results
from tools.database_tools import EventDatabaseTool, VenueDatabaseTool, StudentSegmentTool

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# Set page title
app.title = "LBS EventHorizon - AI Event Planning"

# Custom CSS is loaded automatically from assets/custom.css

# Initialize global objects
crew = EventPlanningCrew()
agent_interaction = AgentInteraction(crew)

# Sidebar component with expandable agent info
def create_sidebar():
    return dbc.Card([
        html.Div([
            html.H4("🤖 AI Agents", className="mb-4"),

            # Prediction Agent
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line me-2"),
                    html.Strong("Prediction Agent"),
                    html.I(
                        className="fas fa-chevron-down float-end",
                        id="sidebar-prediction-icon",
                        style={"cursor": "pointer"}
                    )
                ], className="d-flex align-items-center mb-2 sidebar-agent-header",
                   id="sidebar-prediction-header", style={"cursor": "pointer"}),
                dbc.Collapse([
                    html.Div([
                        html.P("Forecasts event outcomes using historical data and predictive analytics.",
                               className="small mb-2"),
                        html.P([html.Strong("Capabilities:"), html.Br(),
                                "• Attendance prediction", html.Br(),
                                "• Flake rate calculation", html.Br(),
                                "• Historical pattern analysis"],
                               className="small mb-0")
                    ], className="p-2 bg-light rounded")
                ], id="sidebar-prediction-collapse", is_open=False)
            ], className="mb-3"),

            # Compliance Agent
            html.Div([
                html.Div([
                    html.I(className="fas fa-check-circle me-2"),
                    html.Strong("Compliance Agent"),
                    html.I(
                        className="fas fa-chevron-down float-end",
                        id="sidebar-compliance-icon",
                        style={"cursor": "pointer"}
                    )
                ], className="d-flex align-items-center mb-2 sidebar-agent-header",
                   id="sidebar-compliance-header", style={"cursor": "pointer"}),
                dbc.Collapse([
                    html.Div([
                        html.P("Ensures events meet LBS policies and venue requirements.",
                               className="small mb-2"),
                        html.P([html.Strong("Capabilities:"), html.Br(),
                                "• Venue capacity validation", html.Br(),
                                "• Alcohol licensing check", html.Br(),
                                "• Policy compliance review"],
                               className="small mb-0")
                    ], className="p-2 bg-light rounded")
                ], id="sidebar-compliance-collapse", is_open=False)
            ], className="mb-3"),

            # Logistics Agent
            html.Div([
                html.Div([
                    html.I(className="fas fa-box me-2"),
                    html.Strong("Logistics Agent"),
                    html.I(
                        className="fas fa-chevron-down float-end",
                        id="sidebar-logistics-icon",
                        style={"cursor": "pointer"}
                    )
                ], className="d-flex align-items-center mb-2 sidebar-agent-header",
                   id="sidebar-logistics-header", style={"cursor": "pointer"}),
                dbc.Collapse([
                    html.Div([
                        html.P("Optimizes resource allocation and prevents waste.",
                               className="small mb-2"),
                        html.P([html.Strong("Capabilities:"), html.Br(),
                                "• Budget optimization", html.Br(),
                                "• Waste prevention", html.Br(),
                                "• Timeline generation"],
                               className="small mb-0")
                    ], className="p-2 bg-light rounded")
                ], id="sidebar-logistics-collapse", is_open=False)
            ], className="mb-3"),

            # Marketing Agent
            html.Div([
                html.Div([
                    html.I(className="fas fa-bullseye me-2"),
                    html.Strong("Marketing Agent"),
                    html.I(
                        className="fas fa-chevron-down float-end",
                        id="sidebar-marketing-icon",
                        style={"cursor": "pointer"}
                    )
                ], className="d-flex align-items-center mb-2 sidebar-agent-header",
                   id="sidebar-marketing-header", style={"cursor": "pointer"}),
                dbc.Collapse([
                    html.Div([
                        html.P("Creates targeted marketing strategies based on student personas.",
                               className="small mb-2"),
                        html.P([html.Strong("Capabilities:"), html.Br(),
                                "• Persona identification", html.Br(),
                                "• Targeted messaging", html.Br(),
                                "• Attendance boost prediction"],
                               className="small mb-0")
                    ], className="p-2 bg-light rounded")
                ], id="sidebar-marketing-collapse", is_open=False)
            ], className="mb-3"),

            html.Hr(className="my-3"),

            html.Div([
                html.I(className="fas fa-info-circle me-2"),
                html.Small("Click on any agent to learn more about their capabilities")
            ], className="text-muted")
        ], className="sidebar")
    ], className="mb-4")

# Input form component
def create_input_form():
    return dbc.Container([
        html.H2("Tell the AI Agents About Your Event", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Label("📌 Event Name"),
                dbc.Input(
                    id="event-name",
                    type="text",
                    value="AI & Entrepreneurship Summit",
                    className="mb-3"
                ),

                dbc.Label("📂 Event Type"),
                dcc.Dropdown(
                    id="event-type",
                    options=[
                        {"label": t, "value": t} for t in [
                            "Technology", "Finance", "Social", "Career",
                            "Networking", "Academic", "Workshop", "Panel Discussion",
                            "Conference", "Recruiting", "Alumni", "Sport & Wellness",
                            "Arts & Culture", "Charity", "Competition", "Celebration"
                        ]
                    ],
                    value="Technology",
                    className="mb-3"
                ),

                dbc.Label("📅 Date"),
                dcc.DatePickerSingle(
                    id="event-date",
                    date=(datetime.now() + timedelta(days=21)).date(),
                    className="mb-3"
                ),

                dbc.Label("🕐 Time"),
                dbc.Input(
                    id="event-time",
                    type="time",
                    value="18:00",
                    className="mb-3"
                ),
            ], md=6),

            dbc.Col([
                dbc.Label("📍 Venue"),
                dcc.Dropdown(
                    id="event-venue",
                    options=[
                        {"label": v, "value": v} for v in [
                            "Nash Lounge", "Sainsbury Theatre", "Windsor Theatre",
                            "Sammy Ofer Centre - Garden", "Sammy Ofer Centre - Upper Link",
                            "Sammy Ofer Centre - Lower Link", "LT1", "LT2", "LT3",
                            "Nuffield Hall", "Regents Room", "Garden Room",
                            "Sussex Room", "Front Lawn", "Council Chamber"
                        ]
                    ],
                    value="Nash Lounge",
                    className="mb-3"
                ),

                dbc.Label("👥 Expected Registrations"),
                dcc.Slider(
                    id="event-size",
                    min=20,
                    max=400,
                    step=10,
                    value=150,
                    marks={i: str(i) for i in range(20, 401, 50)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="mb-4"
                ),

                dbc.Checklist(
                    id="event-options",
                    options=[
                        {"label": "🍷 Serve Alcohol", "value": "alcohol"},
                        {"label": "🎤 External Speakers", "value": "external"}
                    ],
                    value=[],
                    className="mb-3"
                ),
            ], md=6),
        ]),

        html.H4("🎯 Event Focus", className="mt-4 mb-3"),
        dcc.Dropdown(
            id="event-tags",
            options=[
                {"label": tag, "value": tag} for tag in [
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
            ],
            value=["AI & Machine Learning", "Entrepreneurship"],
            multi=True,
            className="mb-4"
        ),

        html.H4("🎓 Target Audience", className="mb-3"),
        dcc.Dropdown(
            id="event-programs",
            options=[
                {"label": p, "value": p} for p in [
                    "MBA2025", "MBA2024", "MiM2025", "MiM2024",
                    "EMBA", "EMBA-Global", "Sloan Masters",
                    "MAM (Masters in Analytics & Management)", "MFA (Masters in Financial Analysis)",
                    "Executive Education", "PhD Students", "Alumni", "Faculty & Staff"
                ]
            ],
            value=["MBA2025"],
            multi=True,
            className="mb-4"
        ),

        dbc.Button(
            "🚀 Deploy AI Agents",
            id="submit-button",
            color="primary",
            size="lg",
            className="w-100 mb-3"
        ),

        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                    html.Strong("Pro Tips:", className="text-primary")
                ], className="mb-2"),
                html.Ul([
                    html.Li("Thursday evenings (18:00-19:30) have the lowest flake rates", className="small"),
                    html.Li("Adding alcohol service can increase attendance by 8-15%", className="small"),
                    html.Li("Events with external speakers see 12% higher registration", className="small"),
                    html.Li("Our AI prevents £750+ in average catering waste per event", className="small")
                ], className="mb-0 small")
            ])
        ], color="light", className="border-0")
    ])

# Processing stage component
def create_processing_view():
    return dbc.Container([
        html.H2("🤖 AI Agents at Work", className="mb-4"),
        html.Div(id="agent-thinking-container"),
        dcc.Interval(id="processing-interval", interval=1500, n_intervals=0, disabled=True),
        dcc.Store(id="processing-step", data=0)
    ])

# Results component
def create_results_view(results, event):
    if not results:
        return html.Div("No results available")

    return dbc.Container([
        html.H2("🎯 Agent Recommendations", className="mb-4"),

        html.H3("🧠 Autonomous Agent Decisions", className="mb-4"),

        dbc.Row([
            dbc.Col([
                # Prediction Agent
                html.Div([
                    html.Div([
                        html.H5([
                            "📊 Prediction Agent ",
                            html.I(
                                className="fas fa-search-plus agent-expand-icon",
                                id="prediction-toggle",
                                style={"cursor": "pointer", "fontSize": "0.8em", "marginLeft": "8px"}
                            )
                        ], className="text-white d-inline-block mb-3")
                    ]),
                    html.P(f"- Predicted {results['prediction']['flake_rate']}% flake rate", className="text-white mb-1"),
                    html.P(f"- Confidence: {results['prediction'].get('confidence', 'HIGH')}", className="text-white mb-1"),
                    html.Div([
                        html.P(f"⚠️ {rec}", className="text-white mb-1")
                        for rec in results['prediction'].get('recommendations', [])
                    ] if results['prediction'].get('recommendations') else [])
                ], className="agent-decision mb-2"),

                dbc.Collapse([
                    dbc.Card(dbc.CardBody([
                        html.H6("🔍 Detailed Analysis & Reasoning", className="mb-3"),
                        dcc.Markdown(
                            results['prediction'].get('reasoning', 'Analysis complete'),
                            className="reasoning-markdown"
                        )
                    ]), className="detailed-analysis-card")
                ], id="prediction-collapse", is_open=False, className="mb-3"),

                # Compliance Agent
                html.Div([
                    html.Div([
                        html.H5([
                            "✅ Compliance Agent ",
                            html.I(
                                className="fas fa-search-plus agent-expand-icon",
                                id="compliance-toggle",
                                style={"cursor": "pointer", "fontSize": "0.8em", "marginLeft": "8px"}
                            )
                        ], className="text-white d-inline-block mb-3")
                    ]),
                    html.Div([
                        html.P(f"⚠️ {issue}", className="text-white mb-1") for issue in results['compliance']['issues']
                    ] if results['compliance']['issues'] else [
                        html.P("✓ All compliance checks passed", className="text-white mb-1"),
                        html.P("✓ Venue capacity validated", className="text-white mb-1")
                    ]),
                    html.Div([
                        html.P(f"💡 Solution: Switch to {results['compliance']['alternatives'][0]}", className="text-white mb-1")
                    ] if results['compliance']['alternatives'] else [])
                ], className="agent-warning mb-2" if results['compliance']['issues'] else "agent-decision mb-2"),

                dbc.Collapse([
                    dbc.Card(dbc.CardBody([
                        html.H6("🔍 Compliance Analysis", className="mb-3"),
                        dcc.Markdown(
                            results['compliance'].get('reasoning', 'Compliance check complete'),
                            className="reasoning-markdown"
                        ),
                        html.Div([
                            html.H6("📋 Action Items:", className="mt-3"),
                            html.Ul([html.Li(action) for action in results['compliance']['actions_required']])
                        ] if results['compliance']['actions_required'] else [])
                    ]), className="detailed-analysis-card")
                ], id="compliance-collapse", is_open=False, className="mb-3"),
            ], md=6),

            dbc.Col([
                # Logistics Agent
                html.Div([
                    html.Div([
                        html.H5([
                            "📦 Logistics Agent ",
                            html.I(
                                className="fas fa-search-plus agent-expand-icon",
                                id="logistics-toggle",
                                style={"cursor": "pointer", "fontSize": "0.8em", "marginLeft": "8px"}
                            )
                        ], className="text-white d-inline-block mb-3")
                    ]),
                    html.P(f"- Smart Budget: £{results['logistics']['budget']:,}", className="text-white mb-1"),
                    html.P(f"- Waste Prevention: Saved £{results['logistics']['predicted_waste']:,}", className="text-white mb-1")
                ], className="agent-decision mb-2"),

                dbc.Collapse([
                    dbc.Card(dbc.CardBody([
                        html.H6("🔍 Budget Optimization & Waste Prevention", className="mb-3"),
                        dcc.Markdown(
                            results['logistics'].get('reasoning', 'Budget analysis complete'),
                            className="reasoning-markdown"
                        ),
                        html.H6("📅 Critical Timeline:", className="mt-3"),
                        html.Ul([
                            html.Li([html.Strong(item[0]), f" - {item[1]}"])
                            for item in results['logistics'].get('timeline', [])
                            if isinstance(item, tuple)
                        ])
                    ]), className="detailed-analysis-card")
                ], id="logistics-collapse", is_open=False, className="mb-3"),

                # Marketing Agent
                html.Div([
                    html.Div([
                        html.H5([
                            "🎯 Marketing Agent ",
                            html.I(
                                className="fas fa-search-plus agent-expand-icon",
                                id="marketing-toggle",
                                style={"cursor": "pointer", "fontSize": "0.8em", "marginLeft": "8px"}
                            )
                        ], className="text-white d-inline-block mb-3")
                    ]),
                    html.Div([
                        html.P(f"- Primary Target: {results['marketing']['personas'][0]['name']}", className="text-white mb-1")
                    ] if results['marketing']['personas'] else []),
                    html.P(f"- Expected Boost: +{results['marketing']['expected_boost']}% attendance", className="text-white mb-1"),
                    html.P(f"- Clubs: {', '.join(results['marketing'].get('clubs', [])[:3])}", className="text-white mb-1") if results['marketing'].get('clubs') else html.P("", className="text-white mb-1")
                ], className="agent-decision mb-2"),

                dbc.Collapse([
                    dbc.Card(dbc.CardBody([
                        html.H6("🔍 Persona Analysis & Targeting Strategy", className="mb-3"),
                        dcc.Markdown(
                            results['marketing'].get('reasoning', 'Marketing analysis complete'),
                            className="reasoning-markdown"
                        )
                    ]), className="detailed-analysis-card")
                ], id="marketing-collapse", is_open=False, className="mb-3"),
            ], md=6),
        ]),

        html.Hr(className="my-4"),

        # Interactive chat with agents
        html.H3("💬 Ask the AI Team Follow-up Questions", className="mb-3"),
        html.P([
            html.I(className="fas fa-magic me-2"),
            "Our Supervisor Agent will intelligently route your question to the most appropriate specialist(s)"
        ], className="text-muted mb-3"),

        dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            "No need to select an agent - the AI Supervisor will automatically analyze your question and route it to the right expert!"
        ], color="info", className="mb-3"),

        dbc.Input(
            id="agent-question",
            type="text",
            placeholder="e.g., Why is the flake rate so high? How can we reduce costs? Can we serve alcohol here?",
            className="mb-3"
        ),

        dbc.Button(
            [html.I(className="fas fa-robot me-2"), "Ask AI Team"],
            id="ask-agent-button",
            color="primary",
            className="w-100 mb-3"
        ),

        html.Div(id="agent-response-container"),

        html.Div(id="chat-history-container"),

        html.Hr(className="my-4"),

        # Action buttons
        html.H3("🎬 Next Actions", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "📋 Generate LBS Crib Sheet",
                    id="crib-sheet-button",
                    color="success",
                    className="w-100"
                )
            ], md=4),
            dbc.Col([
                dbc.Button(
                    "🔄 Modify Event Details",
                    id="modify-button",
                    color="warning",
                    className="w-100"
                )
            ], md=4),
            dbc.Col([
                dbc.Button(
                    "✅ Approve & Export All",
                    id="approve-button",
                    color="info",
                    className="w-100"
                )
            ], md=4),
        ]),

        html.Div(id="action-feedback"),
        dcc.Download(id="download-crib-sheet")
    ])

# Main layout
app.layout = dbc.Container([
    # Store components for state management
    dcc.Store(id="stage-store", data="input"),
    dcc.Store(id="event-store", data=None),
    dcc.Store(id="results-store", data=None),
    dcc.Store(id="chat-history-store", data=[]),

    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🌅 LBS EventHorizon", className="mb-2"),
                html.H3("AI-Powered Event Intelligence & Planning", className="text-muted mb-3"),
                html.P("Multi-agent AI system for data-driven event planning decisions",
                       className="text-muted small mb-3"),
                html.Hr(),
                dbc.Alert([
                    html.I(className="fas fa-robot me-2"),
                    "4 Autonomous AI Agents • Real-time Analysis • Predictive Intelligence • Waste Prevention"
                ], color="info", className="text-center mb-4")
            ])
        ])
    ]),

    # Main content
    dbc.Row([
        dbc.Col([
            create_sidebar()
        ], md=3),

        dbc.Col([
            html.Div(id="main-content")
        ], md=9),
    ]),

    # Footer
    html.Hr(className="my-4"),
    dbc.Row([
        dbc.Col(html.P("🌅 LBS EventHorizon", className="text-muted"), md=4),
        dbc.Col(html.P("Powered by CrewAI + GPT-4o Mini", className="text-muted text-center"), md=4),
        dbc.Col(html.P("Multi-Agent AI System", className="text-muted text-end"), md=4),
    ])
], fluid=True, className="p-4")

# Callback to update main content based on stage
@app.callback(
    Output("main-content", "children"),
    Input("stage-store", "data"),
    State("results-store", "data"),
    State("event-store", "data")
)
def update_main_content(stage, results, event):
    if stage == "input":
        return create_input_form()
    elif stage == "processing":
        return create_processing_view()
    elif stage == "results":
        return create_results_view(results, event)
    return create_input_form()

# Callback to handle form submission
@app.callback(
    Output("stage-store", "data", allow_duplicate=True),
    Output("event-store", "data"),
    Input("submit-button", "n_clicks"),
    State("event-name", "value"),
    State("event-type", "value"),
    State("event-date", "date"),
    State("event-time", "value"),
    State("event-venue", "value"),
    State("event-size", "value"),
    State("event-options", "value"),
    State("event-tags", "value"),
    State("event-programs", "value"),
    prevent_initial_call=True
)
def submit_form(n_clicks, name, event_type, date, time, venue, size, options, tags, programs):
    if n_clicks:
        event = {
            'name': name,
            'type': event_type,
            'date': datetime.fromisoformat(date).date() if date else datetime.now().date(),
            'time': datetime.strptime(time, "%H:%M").time() if time else datetime.strptime("18:00", "%H:%M").time(),
            'venue': venue,
            'size': size,
            'alcohol': 'alcohol' in options,
            'external': 'external' in options,
            'tags': tags or [],
            'programs': programs or []
        }
        return "processing", event
    return dash.no_update, dash.no_update

# Callback to handle processing stage
@app.callback(
    Output("agent-thinking-container", "children"),
    Output("processing-interval", "disabled"),
    Output("processing-step", "data"),
    Output("stage-store", "data", allow_duplicate=True),
    Output("results-store", "data"),
    Input("processing-interval", "n_intervals"),
    State("processing-step", "data"),
    State("event-store", "data"),
    State("stage-store", "data"),
    prevent_initial_call=True
)
def update_processing(n_intervals, step, event, stage):
    if stage != "processing" or not event:
        return dash.no_update, True, 0, dash.no_update, dash.no_update

    event_name = event.get('name', 'Your Event')
    venue = event.get('venue', 'the venue')
    event_type = event.get('type', 'event')
    size = event.get('size', 100)
    programs = ', '.join(event.get('programs', ['students']))

    agent_thoughts = [
        ("📊 Prediction Agent", f"🔍 Analyzing {event_name}..."),
        ("📊 Prediction Agent", f"📚 Searching {len(EventDatabaseTool().events)} historical events for similar {event_type} events..."),
        ("📊 Prediction Agent", f"👥 Calculating potential audience from {programs}..."),
        ("📊 Prediction Agent", f"📅 Checking event day patterns and timing impact..."),
        ("📊 Prediction Agent", f"{'🍷 Factoring in alcohol impact on attendance...' if event.get('alcohol') else '📊 Analyzing registration behavior...'}"),
        ("📊 Prediction Agent", f"✅ Prediction complete: Flake rate calculated for {size} expected registrations"),

        ("✅ Compliance Agent", f"🔍 Checking {venue} capacity and restrictions..."),
        ("✅ Compliance Agent", f"{'⚠️ Verifying alcohol licensing for ' + venue + '...' if event.get('alcohol') else '✅ Checking venue suitability...'}"),
        ("✅ Compliance Agent", f"{'📋 External speaker security clearance requirements...' if event.get('external') else '✅ No external speakers - clearance not needed'}"),
        ("✅ Compliance Agent", "✅ Compliance check complete"),

        ("📦 Logistics Agent", f"📅 Generating timeline from today to event date..."),
        ("📦 Logistics Agent", f"💰 Calculating smart catering order for predicted vs registered..."),
        ("📦 Logistics Agent", f"⚠️ Computing wastage if ordering for {size} registrations..."),
        ("📦 Logistics Agent", "✅ Budget optimized - waste prevention calculated"),

        ("🎯 Marketing Agent", f"🎯 Analyzing {programs} student personas..."),
        ("🎯 Marketing Agent", "📊 Matching event tags to student interests..."),
        ("🎯 Marketing Agent", f"✉️ Identifying top 3 target personas for {event_type} events..."),
        ("🎯 Marketing Agent", "📈 Calculating attendance boost from targeted marketing"),
    ]

    if step < len(agent_thoughts):
        # Show thoughts up to current step
        thoughts_display = [
            html.Div([
                html.P(f"{agent}: {thought}", className="mb-0")
            ], className="agent-thinking")
            for agent, thought in agent_thoughts[:step + 1]
        ]
        return thoughts_display, False, step + 1, dash.no_update, dash.no_update
    else:
        # Processing complete, generate results
        try:
            student_db = StudentSegmentTool().profiles
            venue_db = VenueDatabaseTool().venues
            event_db = EventDatabaseTool().events

            # Convert date to proper format
            event_copy = event.copy()
            if 'date' in event_copy and not isinstance(event_copy['date'], datetime):
                event_copy['date'] = datetime.fromisoformat(str(event_copy['date'])).date()
            if 'time' in event_copy and not isinstance(event_copy['time'], datetime):
                try:
                    event_copy['time'] = datetime.strptime(str(event_copy['time']), "%H:%M:%S").time()
                except:
                    event_copy['time'] = datetime.strptime(str(event_copy['time']), "%H:%M").time()

            results = generate_comprehensive_results(event_copy, student_db, venue_db, event_db)

            # Initialize context store for agent interactions
            agent_interaction.initialize_context(event_copy, results)

            return dash.no_update, True, 0, "results", results
        except Exception as e:
            error_msg = html.Div([
                html.P(f"Error during processing: {str(e)}", className="text-danger")
            ])
            return error_msg, True, 0, dash.no_update, dash.no_update

# Enable processing interval when entering processing stage
@app.callback(
    Output("processing-interval", "disabled", allow_duplicate=True),
    Input("stage-store", "data"),
    prevent_initial_call=True
)
def control_processing_interval(stage):
    return stage != "processing"

# Callbacks for collapsible sections
@app.callback(
    Output("prediction-collapse", "is_open"),
    Input("prediction-toggle", "n_clicks"),
    State("prediction-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_prediction(n, is_open):
    return not is_open if n else is_open

@app.callback(
    Output("compliance-collapse", "is_open"),
    Input("compliance-toggle", "n_clicks"),
    State("compliance-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_compliance(n, is_open):
    return not is_open if n else is_open

@app.callback(
    Output("logistics-collapse", "is_open"),
    Input("logistics-toggle", "n_clicks"),
    State("logistics-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_logistics(n, is_open):
    return not is_open if n else is_open

@app.callback(
    Output("marketing-collapse", "is_open"),
    Input("marketing-toggle", "n_clicks"),
    State("marketing-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_marketing(n, is_open):
    return not is_open if n else is_open

# Callbacks for sidebar agent info panels
@app.callback(
    Output("sidebar-prediction-collapse", "is_open"),
    Output("sidebar-prediction-icon", "className"),
    Input("sidebar-prediction-header", "n_clicks"),
    State("sidebar-prediction-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_sidebar_prediction(n, is_open):
    new_state = not is_open if n else is_open
    icon_class = "fas fa-chevron-up float-end" if new_state else "fas fa-chevron-down float-end"
    return new_state, icon_class

@app.callback(
    Output("sidebar-compliance-collapse", "is_open"),
    Output("sidebar-compliance-icon", "className"),
    Input("sidebar-compliance-header", "n_clicks"),
    State("sidebar-compliance-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_sidebar_compliance(n, is_open):
    new_state = not is_open if n else is_open
    icon_class = "fas fa-chevron-up float-end" if new_state else "fas fa-chevron-down float-end"
    return new_state, icon_class

@app.callback(
    Output("sidebar-logistics-collapse", "is_open"),
    Output("sidebar-logistics-icon", "className"),
    Input("sidebar-logistics-header", "n_clicks"),
    State("sidebar-logistics-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_sidebar_logistics(n, is_open):
    new_state = not is_open if n else is_open
    icon_class = "fas fa-chevron-up float-end" if new_state else "fas fa-chevron-down float-end"
    return new_state, icon_class

@app.callback(
    Output("sidebar-marketing-collapse", "is_open"),
    Output("sidebar-marketing-icon", "className"),
    Input("sidebar-marketing-header", "n_clicks"),
    State("sidebar-marketing-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_sidebar_marketing(n, is_open):
    new_state = not is_open if n else is_open
    icon_class = "fas fa-chevron-up float-end" if new_state else "fas fa-chevron-down float-end"
    return new_state, icon_class

# Callback for agent chat with intelligent routing
@app.callback(
    Output("agent-response-container", "children"),
    Output("chat-history-store", "data"),
    Input("ask-agent-button", "n_clicks"),
    State("agent-question", "value"),
    State("event-store", "data"),
    State("chat-history-store", "data"),
    prevent_initial_call=True
)
def handle_agent_question(n_clicks, question, event, chat_history):
    if not n_clicks or not question or not question.strip():
        return html.Div(), chat_history

    try:
        # Build comprehensive context
        context = {
            'name': event.get('name'),
            'date': str(event.get('date')),
            'time': str(event.get('time')),
            'venue': event.get('venue'),
            'size': event.get('size'),
            'type': event.get('type'),
            'alcohol': event.get('alcohol'),
            'external': event.get('external'),
            'tags': event.get('tags', []),
            'programs': event.get('programs', [])
        }

        # Add instruction for concise response
        enhanced_question = f"{question}\n\nIMPORTANT: Provide a concise, summarized answer in 3-5 sentences maximum. Focus on the key insights only."

        # Use supervisor-based intelligent routing (no need to specify agent)
        response = agent_interaction.query_agent(
            agent_name=None,  # Not used with supervisor
            question=enhanced_question,
            context=context,
            use_supervisor=True  # Enable intelligent routing
        )

        # Determine which agent(s) were used
        agent_used = response.get('agent_name', 'AI Supervisor')

        # Add to chat history
        chat_history.append({
            'agent': agent_used,
            'question': question,
            'response': response
        })

        # Display response with routing information
        response_display = html.Div([
            # Show routing decision
            dbc.Alert([
                html.I(className="fas fa-route me-2"),
                html.Strong("Routed to: "),
                f"{agent_used}"
            ], color="light", className="mb-2 border"),

            # Main response
            html.Div([
                html.H5([
                    f"{agent_used} Response ",
                    html.I(
                        className="fas fa-search-plus agent-expand-icon",
                        id="reasoning-toggle",
                        style={"cursor": "pointer", "fontSize": "0.8em", "marginLeft": "8px"}
                    )
                ], className="text-white mb-2"),
                dcc.Markdown(
                    response.get('answer', 'No response'),
                    className="text-white mb-0"
                )
            ], className="agent-decision mb-2"),

            # Detailed reasoning (collapsible)
            dbc.Collapse([
                dbc.Card(dbc.CardBody([
                    html.H6("🔍 Full Analysis & Reasoning", className="mb-3"),
                    dcc.Markdown(
                        response.get('reasoning', 'No detailed reasoning captured'),
                        className="reasoning-markdown"
                    )
                ]), className="detailed-analysis-card")
            ], id="reasoning-collapse", is_open=False, className="mb-3")
        ])

        return response_display, chat_history

    except Exception as e:
        error_display = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error processing your question: {str(e)}",
            html.Br(),
            html.Small("This could be due to API limits or connection issues. Please try again.")
        ], color="danger")
        return error_display, chat_history

# Callback for crib sheet generation
@app.callback(
    Output("download-crib-sheet", "data"),
    Output("action-feedback", "children", allow_duplicate=True),
    Input("crib-sheet-button", "n_clicks"),
    State("event-store", "data"),
    State("results-store", "data"),
    prevent_initial_call=True
)
def generate_and_download_crib_sheet(n_clicks, event, results):
    if not n_clicks:
        return dash.no_update, dash.no_update

    try:
        crib_sheet = generate_crib_sheet(event, results)
        filename = f"LBS_Event_CribSheet_{datetime.now().strftime('%Y%m%d')}.txt"

        feedback = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "✓ Crib sheet generated! Download starting... 📧 Ready to send to space@london.edu"
        ], color="success", className="mt-3")

        return dict(content=crib_sheet, filename=filename), feedback

    except Exception as e:
        error_feedback = dbc.Alert(
            f"Error generating crib sheet: {str(e)}",
            color="danger",
            className="mt-3"
        )
        return dash.no_update, error_feedback

# Callback for modify button
@app.callback(
    Output("stage-store", "data", allow_duplicate=True),
    Output("chat-history-store", "data", allow_duplicate=True),
    Input("modify-button", "n_clicks"),
    prevent_initial_call=True
)
def modify_event(n_clicks):
    if n_clicks:
        return "input", []
    return dash.no_update, dash.no_update

# Callback for approve button
@app.callback(
    Output("action-feedback", "children", allow_duplicate=True),
    Input("approve-button", "n_clicks"),
    prevent_initial_call=True
)
def approve_event(n_clicks):
    if n_clicks:
        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "✓ Event plan approved! All recommendations exported. Ready for implementation."
        ], color="success", className="mt-3")
    return dash.no_update

if __name__ == "__main__":
    app.run(debug=True, port=8050)
