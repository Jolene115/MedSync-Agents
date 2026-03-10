from crewai.tools import BaseTool
from pydantic import Field
from data.mimic_loader import MimicLoader
from datetime import datetime, timedelta

# Global Simulation State
# In a full app, this might be in a database or session state
loader = MimicLoader()
# Set a fixed start time for the demo based on the patient's data range (approx 2130 for 40124)
simulation_start_time = datetime(2130, 2, 4, 4, 0, 0)
current_simulation_time = simulation_start_time

class VitalsMonitorTool(BaseTool):
    name: str = "Monitor Vitals"
    description: str = (
        "Reads the latest vital signs for a given patient_id at the current simulation time. "
        "Returns a dictionary with heart_rate, bp, spo2, and temp. "
        "Each call advances the simulation time by 15 minutes."
    )

    def _run(self, patient_id: str) -> str:
        global current_simulation_time
        
        # Check if patient ID matches our processed data, if not default to demo patient
        if patient_id not in ["40124"]: 
             return f"Error: Patient {patient_id} not found in processed data. Try 40124."

        # Load data
        df = loader.get_patient_data(patient_id)
        if df is None:
            return "Error: No data found"
            
        # Get vitals at current time
        vitals = loader.get_vitals_at_time(df, current_simulation_time)
        
        # Advance time for next step (Simulation of time passing)
        current_simulation_time += timedelta(minutes=15)
        
        result = {
            "patient_id": patient_id,
            "current_time": str(current_simulation_time),
            "vitals": vitals.get("values", "No data at this timestamp")
        }
        return str(result)

class PatientHistoryTool(BaseTool):
    name: str = "Read Patient History"
    description: str = "Retrieves the medical history for a specific patient_id."

    def _run(self, patient_id: str) -> str:
        return str(loader.get_patient_history(patient_id))

class EscalationTool(BaseTool):
    name: str = "Escalate Alert"
    description: str = "Logs an escalation decision. Arguments: severity, recommendation, reason."

    def _run(self, severity: str, recommendation: str, reason: str) -> str:
        return f"ESCALATION LOGGED: Severity={severity}, Action={recommendation}, Reason={reason}"

# Export instances for agents to use
vitals_tool = VitalsMonitorTool()
history_tool = PatientHistoryTool()
escalation_tool = EscalationTool()
