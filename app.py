import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from data.mimic_loader import MimicLoader

# Load environment variables (API Key)
load_dotenv()

# Initialize MimicLoader
loader = MimicLoader()

# Page configuration
st.set_page_config(
    page_title="MedSync Clinical Command Centre",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════
# CUSTOM CSS — Clinical Navy/White Theme
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Theme */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Status Header Bar */
    .status-header {
        background: linear-gradient(135deg, #0a1628 0%, #1a2744 100%);
        color: white;
        padding: 18px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(10, 22, 40, 0.3);
    }
    .status-header .patient-info {
        font-size: 15px;
        font-weight: 400;
        opacity: 0.9;
        letter-spacing: 0.3px;
    }
    .status-header .patient-name {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 4px;
        letter-spacing: -0.3px;
    }
    .status-header .phase-badge {
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .phase-idle { background: #374151; color: #9ca3af; }
    .phase-running { background: #1e40af; color: #93c5fd; animation: pulse-blue 2s infinite; }
    .phase-waiting { background: #92400e; color: #fcd34d; animation: pulse-amber 2s infinite; }
    .phase-complete { background: #065f46; color: #6ee7b7; }

    @keyframes pulse-blue {
        0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
        50% { box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }
    }
    @keyframes pulse-amber {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.5); }
        50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
    }

    /* Pipeline Progress Steps */
    .pipeline-container {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 16px 0 24px 0;
        flex-wrap: wrap;
    }
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 18px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 500;
        border: 1.5px solid #e5e7eb;
        background: white;
        color: #6b7280;
        transition: all 0.3s ease;
    }
    .pipeline-step.done {
        background: #ecfdf5;
        border-color: #6ee7b7;
        color: #065f46;
    }
    .pipeline-step.active {
        background: #eff6ff;
        border-color: #3b82f6;
        color: #1e40af;
        animation: pulse-blue 2s infinite;
    }
    .pipeline-step.pending {
        opacity: 0.5;
    }
    .pipeline-arrow {
        color: #d1d5db;
        font-size: 18px;
        display: flex;
        align-items: center;
    }

    /* Vital Cards */
    .vital-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #e5e7eb;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    .vital-card.normal {
        border-left-color: #10b981;
    }
    .vital-card.warning {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    .vital-card.critical {
        border-left-color: #ef4444;
        background: #fef2f2;
        animation: pulse-critical 2s infinite;
    }
    .vital-card.primary {
        border-width: 4px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .vital-card .vital-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6b7280;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .vital-card .vital-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        line-height: 1.2;
    }
    .vital-card.primary .vital-value {
        font-size: 36px;
    }
    .vital-card .vital-delta {
        font-size: 13px;
        font-weight: 500;
        margin-top: 4px;
    }
    .vital-delta.up { color: #ef4444; }
    .vital-delta.down { color: #ef4444; }
    .vital-delta.stable { color: #10b981; }

    @keyframes pulse-critical {
        0%, 100% { box-shadow: 0 1px 4px rgba(239, 68, 68, 0.15); }
        50% { box-shadow: 0 2px 16px rgba(239, 68, 68, 0.3); }
    }

    /* Decision Cards */
    .decision-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .decision-card .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .decision-card .card-icon {
        font-size: 24px;
    }
    .decision-card .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #1f2937;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .decision-card .card-status {
        margin-left: auto;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
    }
    .card-status.done { background: #ecfdf5; color: #065f46; }
    .card-status.active { background: #eff6ff; color: #1e40af; }

    .decision-card .key-finding {
        background: #f0f9ff;
        border-left: 3px solid #3b82f6;
        padding: 10px 14px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        color: #1e3a5f;
        font-weight: 500;
    }
    .decision-card .recommendation {
        background: #f0fdf4;
        border-left: 3px solid #10b981;
        padding: 10px 14px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        color: #14532d;
        font-weight: 500;
    }

    /* HITL Gate */
    .hitl-gate {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
    }
    .hitl-title {
        font-size: 18px;
        font-weight: 700;
        color: #92400e;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .hitl-subtitle {
        font-size: 13px;
        color: #78350f;
        margin-bottom: 16px;
    }

    /* Patient Info Card */
    .patient-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .patient-card .info-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f3f4f6;
        font-size: 13px;
    }
    .patient-card .info-row:last-child {
        border-bottom: none;
    }
    .patient-card .info-label {
        color: #6b7280;
        font-weight: 500;
    }
    .patient-card .info-value {
        color: #111827;
        font-weight: 600;
    }

    /* Regulatory Footer */
    .reg-footer {
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        padding: 16px 24px;
        border-radius: 0 0 12px 12px;
        margin-top: 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }
    .reg-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: #eef2ff;
        color: #4338ca;
        border: 1px solid #c7d2fe;
    }
    .reg-disclaimer {
        font-size: 11px;
        color: #9ca3af;
        font-style: italic;
    }

    /* Section Headers */
    .section-header {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #4b5563;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Hide default Streamlit padding for cleaner layout */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# CLINICAL THRESHOLDS — Standard Medical Ranges
# ═══════════════════════════════════════════════════════════════════════
VITAL_THRESHOLDS = {
    'Heart Rate (bpm)': {'low': 50, 'high': 110, 'normal_low': 60, 'normal_high': 90, 'unit': 'bpm'},
    'Sys BP (mmHg)': {'low': 90, 'high': 160, 'normal_low': 100, 'normal_high': 130, 'unit': 'mmHg'},
    'SpO2 (%)': {'low': 92, 'high': None, 'normal_low': 95, 'normal_high': 100, 'unit': '%'},
    'Temp (°F)': {'low': 95, 'high': 100.4, 'normal_low': 97.5, 'normal_high': 99.0, 'unit': '°F'},
    'Resp Rate (insp/min)': {'low': 10, 'high': 24, 'normal_low': 12, 'normal_high': 20, 'unit': '/min'},
}

# Diagnosis-to-Primary-Vitals mapping
DIAGNOSIS_PRIMARY_VITALS = {
    'pneumonia': ['SpO2 (%)', 'Resp Rate (insp/min)'],
    'respiratory': ['SpO2 (%)', 'Resp Rate (insp/min)'],
    'asthma': ['SpO2 (%)', 'Resp Rate (insp/min)'],
    'copd': ['SpO2 (%)', 'Resp Rate (insp/min)'],
    'breath': ['SpO2 (%)', 'Resp Rate (insp/min)'],
    'stemi': ['Heart Rate (bpm)', 'Sys BP (mmHg)'],
    'heart': ['Heart Rate (bpm)', 'Sys BP (mmHg)'],
    'cardiac': ['Heart Rate (bpm)', 'Sys BP (mmHg)'],
    'mi': ['Heart Rate (bpm)', 'Sys BP (mmHg)'],
    'failure': ['Heart Rate (bpm)', 'Sys BP (mmHg)'],
    'sepsis': ['Temp (°F)', 'Heart Rate (bpm)'],
    'infection': ['Temp (°F)', 'Heart Rate (bpm)'],
    'fever': ['Temp (°F)', 'Heart Rate (bpm)'],
}


def get_vital_status(metric_name, value):
    """Returns 'normal', 'warning', or 'critical' based on clinical thresholds."""
    thresholds = VITAL_THRESHOLDS.get(metric_name)
    if not thresholds or pd.isna(value):
        return 'normal'
    if thresholds['low'] and value < thresholds['low']:
        return 'critical'
    if thresholds['high'] and value > thresholds['high']:
        return 'critical'
    if value < thresholds['normal_low'] or (thresholds['normal_high'] and value > thresholds['normal_high']):
        return 'warning'
    return 'normal'


def get_primary_vitals(diagnosis):
    """Returns list of primary vital names for the given diagnosis."""
    dx_lower = diagnosis.lower()
    for keyword, vitals in DIAGNOSIS_PRIMARY_VITALS.items():
        if keyword in dx_lower:
            return vitals
    return ['Heart Rate (bpm)', 'Sys BP (mmHg)']  # default


def extract_key_finding(output_text):
    """Extracts ### KEY FINDING: content from structured agent output."""
    match = re.search(r'###\s*KEY\s*FINDING[:\s]*\n?(.*?)(?=###|$)', output_text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: first 2 sentences
    sentences = re.split(r'[.!?]+', output_text.strip())
    return '. '.join(s.strip() for s in sentences[:2] if s.strip()) + '.'


def extract_recommendation(output_text):
    """Extracts ### RECOMMENDATION: content from structured agent output."""
    match = re.search(r'###\s*RECOMMENDATION[:\s]*\n?(.*?)(?=###|$)', output_text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def get_status_emoji(vital_status):
    """Returns status emoji for vital status."""
    return {'normal': '🟢', 'warning': '🟡', 'critical': '🔴'}.get(vital_status, '⚪')


# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR — Controls & Configuration
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏥 MedSync Control")
    st.markdown("---")

    # Patient Selection
    patient_id = st.text_input("Patient ID:", value="40124", help="Enter a valid MIMIC-III subject ID")

    # Quick Demo Cases
    st.markdown("**Quick Demo Cases:**")
    demo_cols = st.columns(2)
    with demo_cols[0]:
        if st.button("🫁 Pneumonia", use_container_width=True, help="Patient 40124"):
            st.session_state.quick_patient = "40124"
            st.rerun()
        if st.button("❤️ STEMI", use_container_width=True, help="Patient 40503"):
            st.session_state.quick_patient = "40503"
            st.rerun()
    with demo_cols[1]:
        if st.button("🦠 Sepsis", use_container_width=True, help="Patient 10006"):
            st.session_state.quick_patient = "10006"
            st.rerun()
        if st.button("🫁 Embolism", use_container_width=True, help="Patient 43881"):
            st.session_state.quick_patient = "43881"
            st.rerun()

    # Handle quick patient selection
    if "quick_patient" in st.session_state:
        patient_id = st.session_state.quick_patient
        del st.session_state.quick_patient

    st.markdown("---")

    if st.button("🚀 Start Clinical Analysis", use_container_width=True, type="primary"):
        st.session_state.sim_state = "RUNNING_PHASE_1"
        st.session_state.clinical_logs = []
        st.session_state.decision_cards = []
        st.session_state.pharmacist_plan = ""
        st.session_state.final_result = ""
        st.session_state.completed_agents = []

    st.markdown("---")

    # Developer/Audit Mode Toggle
    dev_mode = st.toggle("🔧 Developer / Audit Mode", value=False,
                         help="Show raw AI reasoning and tool execution logs")

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; opacity:0.5; font-size:11px;'>"
        "MedSync-Agents v2.0<br/>Clinical Command Centre"
        "</div>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════
# STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════
if "sim_state" not in st.session_state:
    st.session_state.sim_state = "START"
if "clinical_logs" not in st.session_state:
    st.session_state.clinical_logs = []
if "decision_cards" not in st.session_state:
    st.session_state.decision_cards = []
if "pharmacist_plan" not in st.session_state:
    st.session_state.pharmacist_plan = ""
if "final_result" not in st.session_state:
    st.session_state.final_result = ""
if "completed_agents" not in st.session_state:
    st.session_state.completed_agents = []


# ═══════════════════════════════════════════════════════════════════════
# FETCH PATIENT DATA
# ═══════════════════════════════════════════════════════════════════════
history_str = loader.get_patient_history(patient_id)
df_vitals = loader.get_patient_data(patient_id)

raw_dx = "Unknown"
clean_dx = "Unknown"
history_dict = {}

if "Error" not in history_str and "No records" not in history_str:
    history_lines = history_str.strip().split('\n')
    history_dict = {line.split(': ')[0]: line.strip(line.split(': ')[0] + ': ') for line in history_lines if ': ' in line}
    raw_dx = history_dict.get('Admission Diagnosis', 'N/A')
    clean_dx = raw_dx.strip().replace("PNEUMONI", "Pneumonia").title()


# ═══════════════════════════════════════════════════════════════════════
# STATUS HEADER BAR
# ═══════════════════════════════════════════════════════════════════════
phase_labels = {
    "START": ("Awaiting Input", "phase-idle"),
    "RUNNING_PHASE_1": ("Phase 1 — AI Analysis Running", "phase-running"),
    "PHASE_1_COMPLETE": ("Awaiting Clinician Approval", "phase-waiting"),
    "RUNNING_PHASE_2": ("Phase 2 — Coordination Running", "phase-running"),
    "FINALIZED": ("Analysis Complete", "phase-complete"),
}
phase_text, phase_class = phase_labels.get(st.session_state.sim_state, ("Unknown", "phase-idle"))

admit_time_display = history_dict.get('Admission Time', 'N/A')
gender_display = history_dict.get('Gender', 'N/A')

st.markdown(f"""
<div class="status-header">
    <div>
        <div class="patient-name">Patient {patient_id}</div>
        <div class="patient-info">
            Dx: <strong>{clean_dx}</strong> &nbsp;·&nbsp; 
            Gender: <strong>{gender_display}</strong> &nbsp;·&nbsp; 
            Admitted: <strong>{admit_time_display}</strong>
        </div>
    </div>
    <div class="phase-badge {phase_class}">{phase_text}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# AGENT PIPELINE PROGRESS
# ═══════════════════════════════════════════════════════════════════════
agent_pipeline = [
    ("🩺", "Triage", "Triage Nurse"),
    ("🧠", "Diagnosis", "Diagnostic Specialist"),
    ("💊", "Pharmacy", "Clinical Pharmacist"),
    ("📋", "Coordination", "Ward Coordinator"),
]

completed = st.session_state.completed_agents

def get_step_class(agent_role):
    if agent_role in completed:
        return "done"
    # Determine which agent is currently active based on state
    if st.session_state.sim_state == "RUNNING_PHASE_1":
        next_agents = ["Triage Nurse", "Diagnostic Specialist", "Clinical Pharmacist"]
        for a in next_agents:
            if a not in completed:
                return "active" if a == agent_role else "pending"
    elif st.session_state.sim_state == "RUNNING_PHASE_2":
        if agent_role == "Ward Coordinator":
            return "active"
    return "pending"

pipeline_html = '<div class="pipeline-container">'
for i, (icon, label, role) in enumerate(agent_pipeline):
    step_class = get_step_class(role)
    status_icon = "✅" if step_class == "done" else ("🔄" if step_class == "active" else "⏳")
    pipeline_html += f'<div class="pipeline-step {step_class}">{icon} {label} {status_icon}</div>'
    if i < len(agent_pipeline) - 1:
        pipeline_html += '<div class="pipeline-arrow">→</div>'
pipeline_html += '</div>'

st.markdown(pipeline_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# AGENT STEP CALLBACK — Structured Extraction
# ═══════════════════════════════════════════════════════════════════════
def agent_step_callback(step_output):
    agent_role = "Medical Agent"

    # Role Resolution
    thought_text = getattr(step_output, 'thought', getattr(step_output, 'log', '')).lower()
    output_text_lower = getattr(step_output, 'output', '').lower()
    combined_text = thought_text + " " + output_text_lower

    if hasattr(step_output, 'agent') and hasattr(step_output.agent, 'role'):
        agent_role = step_output.agent.role
    elif any(kw in combined_text for kw in ["triage nurse", "monitor_vitals", "vitals report", "read_patient_vitals"]):
        agent_role = "Triage Nurse"
    elif any(kw in combined_text for kw in ["diagnostic specialist", "differential diagnosis", "diagnostic assessment", "read_patient_history"]):
        agent_role = "Diagnostic Specialist"
    elif any(kw in combined_text for kw in ["pharmacist", "check medication", "medication plan", "check_general_medications"]):
        agent_role = "Clinical Pharmacist"
    elif any(kw in combined_text for kw in ["ward coordinator", "severity score", "final action plan", "level of care"]):
        agent_role = "Ward Coordinator"

    icons = {"Triage Nurse": "🩺", "Diagnostic Specialist": "🧠", "Clinical Pharmacist": "💊", "Ward Coordinator": "📋"}
    icon = icons.get(agent_role, "🏥")
    stage_labels = {
        "Triage Nurse": "Stage 1: Triage Assessment",
        "Diagnostic Specialist": "Stage 2: Diagnostic Review",
        "Clinical Pharmacist": "Stage 3: Pharmacy Safety Check",
        "Ward Coordinator": "Stage 4: Final Coordination"
    }
    stage_text = stage_labels.get(agent_role, f"{agent_role} Task")

    thought_content = getattr(step_output, 'thought', getattr(step_output, 'log', ''))

    # Action log for developer mode
    action_log = ""
    if hasattr(step_output, 'tool') and getattr(step_output, 'tool'):
        tool_name = getattr(step_output, 'tool')
        tool_input = getattr(step_output, 'tool_input', '')
        action_log = f"Tool: {tool_name} | Input: {tool_input}"

    output_text = getattr(step_output, 'output', '')
    if not output_text:
        if action_log:
            output_text = f"Executing tool: {getattr(step_output, 'tool')}"
        else:
            output_text = str(step_output)

    clean_output = str(output_text).replace('\\n', '\n').strip()

    # Extract structured findings
    key_finding = extract_key_finding(clean_output)
    recommendation = extract_recommendation(clean_output)

    # Track completed agents
    if agent_role not in st.session_state.completed_agents:
        st.session_state.completed_agents.append(agent_role)

    log_entry = {
        "role": agent_role,
        "icon": icon,
        "stage_text": stage_text,
        "thought": thought_content,
        "action": action_log,
        "output": clean_output,
        "key_finding": key_finding,
        "recommendation": recommendation,
    }
    st.session_state.clinical_logs.append(log_entry)

    # Create decision card data
    card = {
        "role": agent_role,
        "icon": icon,
        "stage_text": stage_text,
        "key_finding": key_finding,
        "recommendation": recommendation,
        "full_output": clean_output,
        "thought": thought_content,
        "action": action_log,
    }
    # Only add one card per role (last output wins)
    st.session_state.decision_cards = [c for c in st.session_state.decision_cards if c["role"] != agent_role]
    st.session_state.decision_cards.append(card)


# ═══════════════════════════════════════════════════════════════════════
# MAIN LAYOUT — Two Column Clinical Display
# ═══════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([2, 3])

# ─────────────────────────────────────────────────
# LEFT PANEL — Vitals & Patient Context
# ─────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="section-header">📊 Vitals Overview</div>', unsafe_allow_html=True)

    if df_vitals is not None:
        admit_time = history_dict.get('Admission Time') if 'history_dict' in locals() else None
        future_time = datetime(2200, 1, 1)
        history_df = loader.get_vitals_history(df_vitals, future_time, lookback_hours=24, admit_time=admit_time)

        if not history_df.empty:
            x_col = history_df.attrs.get('x_axis_col', 'charttime')
            primary_vitals = get_primary_vitals(clean_dx)

            # Get all available vital metrics
            metrics = [c for c in history_df.columns if c != x_col]

            # Sort: primary vitals first
            metrics_sorted = sorted(metrics, key=lambda m: (0 if m in primary_vitals else 1, m))

            for metric in metrics_sorted:
                plot_df = history_df[[x_col, metric]].dropna()
                if plot_df.empty:
                    continue

                current_val = plot_df.iloc[-1][metric]
                is_primary = metric in primary_vitals
                status = get_vital_status(metric, current_val)
                status_emoji = get_status_emoji(status)

                # Calculate trend delta
                delta_html = ""
                if len(plot_df) >= 2:
                    prev_val = plot_df.iloc[-2][metric]
                    delta = current_val - prev_val
                    if abs(delta) > 0.5:
                        arrow = "↑" if delta > 0 else "↓"
                        # For BP and SpO2, down is bad; for HR and Temp, up is bad
                        is_bad_direction = False
                        if metric in ['Sys BP (mmHg)', 'SpO2 (%)'] and delta < 0:
                            is_bad_direction = True
                        elif metric in ['Heart Rate (bpm)', 'Temp (°F)', 'Resp Rate (insp/min)'] and delta > 0:
                            is_bad_direction = True
                        delta_class = "up" if is_bad_direction else "stable"
                        if not is_bad_direction and abs(delta) < 5:
                            delta_class = "stable"
                        delta_html = f'<div class="vital-delta {delta_class}">{arrow} {abs(delta):.1f} from previous</div>'
                    else:
                        delta_html = '<div class="vital-delta stable">→ Stable</div>'

                card_class = f"vital-card {status}" + (" primary" if is_primary else "")
                st.markdown(f"""
                <div class="{card_class}">
                    <div class="vital-label">{status_emoji} {metric} {'★ PRIMARY' if is_primary else ''}</div>
                    <div class="vital-value">{current_val:.1f}</div>
                    {delta_html}
                </div>
                """, unsafe_allow_html=True)

                # Mini sparkline chart
                fig = px.line(plot_df, x=x_col, y=metric)
                color = '#ef4444' if status == 'critical' else ('#f59e0b' if status == 'warning' else '#10b981')
                fig.update_traces(line=dict(color=color, width=2))
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    height=80 if not is_primary else 100,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showticklabels=False, showgrid=False),
                    yaxis=dict(showticklabels=False, showgrid=False),
                )
                st.plotly_chart(fig, use_container_width=True, key=f"spark_{metric}")
        else:
            st.info("No continuous vitals history found for this patient.")
    else:
        st.error("Patient vitals data not found.")

    # Patient Info Card
    st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
    if "Error" not in history_str and "No records" not in history_str:
        st.markdown(f"""
        <div class="patient-card">
            <div class="info-row"><span class="info-label">Patient ID</span><span class="info-value">{patient_id}</span></div>
            <div class="info-row"><span class="info-label">Gender</span><span class="info-value">{history_dict.get('Gender', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">Date of Birth</span><span class="info-value">{history_dict.get('Date of Birth', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">Diagnosis</span><span class="info-value">{clean_dx}</span></div>
            <div class="info-row"><span class="info-label">Admitted</span><span class="info-value">{history_dict.get('Admission Time', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">Insurance</span><span class="info-value">{history_dict.get('Insurance', 'N/A')}</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Patient not found in database.")


# ─────────────────────────────────────────────────
# RIGHT PANEL — Clinical Decisions & Actions
# ─────────────────────────────────────────────────
with col_right:
    st.markdown('<div class="section-header">🎯 Clinical Decision Feed</div>', unsafe_allow_html=True)

    # ── Render Decision Cards ──
    if st.session_state.decision_cards:
        for card in st.session_state.decision_cards:
            st.markdown(f"""
            <div class="decision-card">
                <div class="card-header">
                    <span class="card-icon">{card['icon']}</span>
                    <span class="card-title">{card['stage_text']}</span>
                    <span class="card-status done">Complete</span>
                </div>
                <div class="key-finding">
                    <strong>Key Finding:</strong> {card['key_finding']}
                </div>
                {'<div class="recommendation"><strong>Recommendation:</strong> ' + card["recommendation"] + '</div>' if card["recommendation"] else ''}
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🔍 View {card['role']}'s Full AI Reasoning"):
                st.markdown(card['full_output'])
    elif st.session_state.sim_state == "START":
        st.info("👈 Select a patient and click **Start Clinical Analysis** to begin the multi-agent coordination.")

    # ── Run Phase 1 ──
    if st.session_state.sim_state == "RUNNING_PHASE_1":
        with st.spinner("🔄 Phase 1: AI Medical Team is analyzing patient data..."):
            from core.crew import HospitalSystem
            system = HospitalSystem()
            result = system.run_initial_phase(
                patient_id=patient_id,
                diagnosis=clean_dx,
                step_callback=agent_step_callback
            )
            st.session_state.pharmacist_plan = str(result)
            st.session_state.sim_state = "PHASE_1_COMPLETE"
            st.rerun()

    # ── HITL Approval Gate ──
    elif st.session_state.sim_state == "PHASE_1_COMPLETE":
        st.markdown("""
        <div class="hitl-gate">
            <div class="hitl-title">⚠️ Clinician Verification Required</div>
            <div class="hitl-subtitle">
                The AI medical team has completed initial analysis. A qualified clinician must review 
                and approve the medication plan before the Ward Coordinator can finalize resource allocation.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**📋 AI-Generated Medication Plan:**")
        reviewed_plan = st.text_area(
            "Review, modify, or approve the plan below:",
            value=st.session_state.pharmacist_plan,
            height=300,
            label_visibility="collapsed"
        )

        hitl_cols = st.columns([1, 1])
        with hitl_cols[0]:
            if st.button("✅ Approve & Escalate", type="primary", use_container_width=True):
                st.session_state.pharmacist_plan = reviewed_plan
                st.session_state.sim_state = "RUNNING_PHASE_2"
                st.rerun()
        with hitl_cols[1]:
            if st.button("✏️ Modify & Escalate", use_container_width=True):
                st.session_state.pharmacist_plan = reviewed_plan
                st.session_state.sim_state = "RUNNING_PHASE_2"
                st.rerun()

    # ── Run Phase 2 ──
    elif st.session_state.sim_state == "RUNNING_PHASE_2":
        with st.spinner("🔄 Phase 2: Ward Coordinator is finalizing resource allocation..."):
            from core.crew import HospitalSystem
            system = HospitalSystem()
            final_result = system.run_final_phase(
                patient_id=patient_id,
                diagnosis=clean_dx,
                human_input=st.session_state.pharmacist_plan,
                step_callback=agent_step_callback
            )
            st.session_state.final_result = str(final_result)
            st.session_state.sim_state = "FINALIZED"
            st.rerun()

    # ── Final Results: Severity & Orders ──
    elif st.session_state.sim_state == "FINALIZED" and st.session_state.final_result:
        final_result_str = st.session_state.final_result

        st.markdown("---")
        st.markdown('<div class="section-header">📊 Final Clinical Orders</div>', unsafe_allow_html=True)

        # Extract severity
        severity_match = re.search(r'(?:Severity Score|Severity)[\*:\s]*(\d+)', final_result_str, re.IGNORECASE)
        severity_score = int(severity_match.group(1)) if severity_match else 5

        sev_col1, sev_col2 = st.columns([1, 2])

        with sev_col1:
            # Severity Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=severity_score,
                title={'text': "Criticality Index", 'font': {'size': 20, 'family': 'Inter'}},
                gauge={
                    'axis': {'range': [None, 10], 'tickwidth': 1},
                    'bar': {'color': "#1e40af"},
                    'steps': [
                        {'range': [0, 3], 'color': "#ecfdf5"},
                        {'range': [3, 7], 'color': "#fffbeb"},
                        {'range': [7, 10], 'color': "#fef2f2"}
                    ],
                    'threshold': {
                        'line': {'color': "#111827", 'width': 4},
                        'thickness': 0.75,
                        'value': severity_score
                    }
                }
            ))
            fig_gauge.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': "#1f2937", 'family': "Inter"},
                height=220
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.metric(label="Severity Score", value=f"{severity_score} / 10")

        with sev_col2:
            clean_final = re.sub(r'\*?Severity.*?\d+(?:/10)?\*?\n?', '', final_result_str, flags=re.IGNORECASE).strip()
            is_stemi = "stemi" in clean_dx.lower()
            if severity_score >= 7 or is_stemi:
                st.error(clean_final)
            elif severity_score >= 4:
                st.warning(clean_final)
            else:
                st.success(clean_final)

        st.download_button(
            label="📥 Download Clinical Report",
            data=final_result_str,
            file_name=f"patient_{patient_id}_clinical_report.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )


# ═══════════════════════════════════════════════════════════════════════
# DEVELOPER / AUDIT MODE — Raw Agent Logs
# ═══════════════════════════════════════════════════════════════════════
if dev_mode and st.session_state.clinical_logs:
    st.markdown("---")
    st.markdown('<div class="section-header">🔧 Developer / Audit Trail</div>', unsafe_allow_html=True)
    st.caption("This view shows raw AI agent reasoning, tool calls, and execution logs for technical review.")

    for i, log in enumerate(st.session_state.clinical_logs):
        with st.expander(f"{log['icon']} {log['stage_text']} — {log['role']}", expanded=False):
            if log.get("action"):
                st.code(log["action"], language="text")
            if log.get("thought") and len(str(log["thought"]).strip()) > 20:
                st.markdown("**🧠 Internal Reasoning:**")
                st.text(str(log["thought"]).replace('\\n', '\n').strip())
            st.markdown("**📄 Full Output:**")
            st.markdown(log["output"])


# ═══════════════════════════════════════════════════════════════════════
# REGULATORY & STANDARDS FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div class="reg-footer">
    <div>
        <span class="reg-badge">🔥 FHIR R4 Aware</span>
        <span class="reg-badge">🔒 HIPAA Aware</span>
        <span class="reg-badge">🤖 ISO 42001 Aware</span>
    </div>
    <div class="reg-disclaimer">
        Designed with awareness of healthcare data interoperability (FHIR), privacy (HIPAA), and AI governance (ISO 42001) standards. 
        This is a research prototype — not a certified medical device.
    </div>
</div>
""", unsafe_allow_html=True)
