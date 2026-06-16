# LBS Event Horizon

LBS Event Horizon is an agent-assisted event operations prototype for organisers. It combines event planning inputs, synthetic operational data, and specialist agents to produce planning support, risk checks, marketing suggestions, logistics guidance, and event crib sheets.

The project is useful as a field/deployment-style case study: it starts with a messy real workflow, breaks it into agent responsibilities, and turns the result into a working Python application that can be demoed with realistic event scenarios.

## What it demonstrates

- Translating an event organiser workflow into a multi-agent system
- Coordinating planning, marketing, logistics, compliance, and prediction agents
- Generating operational outputs such as event crib sheets and context records
- Using synthetic data to test product behavior without exposing real attendee data
- Building a Python prototype around practical stakeholder needs

## Project structure

```text
LBS_EventHorizon/
├── app.py                         # Main app entry point
├── app_dash.py                    # Dashboard/app variant
├── agents/                        # Specialist event-planning agents
├── tools/                         # Booking and database tools
├── utils/                         # Output and crib sheet generation
├── mock_data/                     # Synthetic event data
├── outputs/                       # Generated example outputs
└── SECURITY.md                    # API key and environment guidance
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

To run the Dash variant:

```bash
python app_dash.py
```

## Security note

API keys should be stored in a local `.env` file and never committed. See `SECURITY.md` for setup guidance.

## Data note

The included personas, venue constraints, past events, and generated outputs are synthetic examples for prototyping and demonstration.
