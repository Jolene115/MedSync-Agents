import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from data.mimic_loader import MimicLoader

# Load environment variables (API Key) to FIX Importerror
load_dotenv()

# Initialize MimicLoader
loader = MimicLoader()

# Page configuration
st.set_page_config(
    page_title="MedSync-Agents Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar - Controls
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=100) # Placeholder hospital logo
    st.title("MedSync Control")
    st.markdown("---")
    
    # Patient Selection
    patient_id = st.text_input("Enter Patient ID:", value="40124")
    st.markdown("---")
    if st.button("🚀 Start Simulation", use_container_width=True, type="primary"):
        st.session_state.sim_state = "RUNNING_PHASE_1"
        st.session_state.clinical_logs = []
        st.session_state.pharmacist_plan = ""
        st.session_state.final_result = ""

st.title("🏥 Clinical AI Coordination Dashboard")
st.markdown("Watch the multi-agent system analyze and escalate real-time patient data.")
st.markdown("---")

# State Machine Initialization
if "sim_state" not in st.session_state:
    st.session_state.sim_state = "START"
if "clinical_logs" not in st.session_state:
    st.session_state.clinical_logs = []
if "pharmacist_plan" not in st.session_state:
    st.session_state.pharmacist_plan = ""
if "final_result" not in st.session_state:
    st.session_state.final_result = ""

# Fetch Data (Unconditional so context renders regardless of state)
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

# NEW THREE COLUMN LAYOUT
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("📋 Patient Context")
    if "Error" not in history_str and "No records" not in history_str:
        st.info(f"**Age/DOB:** {history_dict.get('Date of Birth', 'N/A')}")
        st.info(f"**Gender:** {history_dict.get('Gender', 'N/A')}")
        st.error(f"**Admit Dx:** {clean_dx}")
        st.warning(f"**Admit Time:** {history_dict.get('Admission Time', 'N/A')}")
    else:
        st.error("Patient not found in database.")
        
    st.markdown("### 📊 Vitals Trend")
    if df_vitals is not None:
        admit_time = history_dict.get('Admission Time') if 'history_dict' in locals() else None
        future_time = datetime(2200, 1, 1)
        history_df = loader.get_vitals_history(df_vitals, future_time, lookback_hours=24, admit_time=admit_time)
        
        if not history_df.empty:
            x_col = history_df.attrs.get('x_axis_col', 'charttime')
            dx_lower = clean_dx.lower()
            target_metrics = []
            
            if any(word in dx_lower for word in ['pneumonia', 'respiratory', 'asthma', 'copd', 'breath']):
                target_metrics = ['Resp Rate (insp/min)', 'SpO2 (%)']
            elif any(word in dx_lower for word in ['heart', 'stemi', 'cardiac', 'failure', 'shock']):
                target_metrics = ['Heart Rate (bpm)', 'Sys BP (mmHg)']
            elif any(word in dx_lower for word in ['sepsis', 'infection', 'fever']):
                target_metrics = ['Temp (°F)', 'Heart Rate (bpm)']
            else:
                target_metrics = ['Heart Rate (bpm)', 'Sys BP (mmHg)']
            
            metrics = [c for c in history_df.columns if c != x_col and any(m in c for m in target_metrics)]
            if not metrics:
                metrics = [c for c in history_df.columns if c != x_col]
            
            for metric in metrics:
                plot_df = history_df[[x_col, metric]].dropna()
                if not plot_df.empty:
                    fig = px.line(plot_df, x=x_col, y=metric, title=metric)
                    fig.update_layout(
                        xaxis_title="Hours Since Admit" if x_col != 'charttime' else "", 
                        yaxis_title="", height=140, margin=dict(l=0, r=0, t=30, b=0),
                        showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
                    )
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showline=False, showgrid=True, gridcolor='lightgray')
                    current_val = plot_df.iloc[-1][metric]
                    st.metric(label=metric, value=f"{current_val:.1f}")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No continuous vitals history found.")

with col2:
    st.subheader("🤖 Live Coordination Feed")
    chat_container = st.container(height=650)
    
    def render_log_entry(log, container):
        with container:
            with st.chat_message("assistant", avatar=log["icon"]):
                st.subheader(f"{log['icon']} {log['stage_text']} Complete")
                
                # Only render reasoning expander if content exceeds clinical value threshold
                has_thought = log["thought"] and len(log["thought"].strip()) > 20
                has_action = bool(log["action"])
                
                if has_thought:
                    with st.expander(f"View {log['role']}'s Clinical Reasoning"):
                        st.write(log["thought"].replace('\\n', '\n').strip())
                elif has_action:
                    with st.expander(f"View {log['role']}'s Action Log"):
                        st.code(log["action"])
                        
                st.info(log["output"])

    def agent_step_callback(step_output):
        agent_role = "Medical Agent"
        
        # Enhanced Bulletproof Role Resolution Heuristic
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
        stage_labels = {"Triage Nurse": "Stage 1: Triage Assessment", "Diagnostic Specialist": "Stage 2: Diagnostic Review", "Clinical Pharmacist": "Stage 3: Pharmacy Review", "Ward Coordinator": "Stage 4: Final Coordination"}
        stage_text = stage_labels.get(agent_role, f"{agent_role} Task")

        thought_content = getattr(step_output, 'thought', getattr(step_output, 'log', ''))
        
        # Professional Custom Action Log
        action_log = ""
        if hasattr(step_output, 'tool') and getattr(step_output, 'tool'):
            tool_name = getattr(step_output, 'tool')
            tool_input = getattr(step_output, 'tool_input', '')
            action_log = f"Action: {icon} {agent_role} is executing '{tool_name}' with input: {tool_input}"

        output_text = getattr(step_output, 'output', '')
        if not output_text:
            if action_log:
                output_text = f"Action Result for '{getattr(step_output, 'tool')}'"
            else:
                output_text = str(step_output)
                
        clean_output = str(output_text).replace('\\n', '\n').strip()

        log_entry = {
            "role": agent_role,
            "icon": icon,
            "stage_text": stage_text,
            "thought": thought_content,
            "action": action_log,
            "output": clean_output
        }
        st.session_state.clinical_logs.append(log_entry)
        render_log_entry(log_entry, chat_container)

    # 1. Render historical logs first
    for log in st.session_state.clinical_logs:
        render_log_entry(log, chat_container)

    # 2. Handle Phase Execution
    if st.session_state.sim_state == "RUNNING_PHASE_1":
        with st.spinner("Stage 1-3: Medical AI team is analyzing data..."):
            from core.crew import HospitalSystem
            system = HospitalSystem()
            result = system.run_initial_phase(patient_id=patient_id, diagnosis=clean_dx, step_callback=agent_step_callback)
            st.session_state.pharmacist_plan = str(result)
            st.session_state.sim_state = "PHASE_1_COMPLETE"
            st.rerun()

    elif st.session_state.sim_state == "PHASE_1_COMPLETE":
        with chat_container:
            st.warning("🚨 System Paused: Pending Clinical Approval")
            override_text = st.text_area("Review and Edit the Pharmacist's Medication Plan before Ward Coordinator Escalation:", value=st.session_state.pharmacist_plan, height=300)
            if st.button("✅ Verify and Escalate", type="primary"):
                st.session_state.pharmacist_plan = override_text
                st.session_state.sim_state = "RUNNING_PHASE_2"
                st.rerun()

    elif st.session_state.sim_state == "RUNNING_PHASE_2":
        with st.spinner("Stage 4: Ward Coordinator finalizing escalation..."):
            from core.crew import HospitalSystem
            system = HospitalSystem()
            final_result = system.run_final_phase(patient_id=patient_id, diagnosis=clean_dx, human_input=st.session_state.pharmacist_plan, step_callback=agent_step_callback)
            st.session_state.final_result = str(final_result)
            st.session_state.sim_state = "FINALIZED"
            st.rerun()

    elif st.session_state.sim_state == "FINALIZED":
        with chat_container:
            with st.chat_message("assistant", avatar="🏁"):
                st.success("Simulation Complete")

with col3:
    st.subheader("🚨 Final Orders")
    if st.session_state.sim_state == "FINALIZED" and st.session_state.final_result:
        final_result_str = st.session_state.final_result
        severity_match = re.search(r'(?:Severity Score|Severity)[\*:\s]*(\d+)', final_result_str, re.IGNORECASE)
        severity_score = int(severity_match.group(1)) if severity_match else 5
        
        st.metric(label="Calculated Severity", value=f"{severity_score} / 10")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = severity_score,
            title = {'text': "Criticality Index", 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [None, 10], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'steps' : [
                    {'range': [0, 3], 'color': "green"},
                    {'range': [3, 7], 'color': "yellow"},
                    {'range': [7, 10], 'color': "red"}],
                'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': severity_score}
            }
        ))
        
        fig_gauge.update_layout(
            title_y=0.9,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "darkblue", 'family': "Arial"},
            height=220
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
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
            file_name=f"patient_{patient_id}_report.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )
