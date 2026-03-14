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
        "Reads the most recent vital signs records for a given patient_id. "
        "Returns the last 10 readings regardless of the exact time, ensuring data is found."
    )

    def _run(self, patient_id: str) -> str:
        # Load data
        df = loader.get_patient_data(patient_id)
        if df is None or df.empty:
            return "Error: No data found for this patient."
            
        # The Fix: Filter for relevant vital IDs and grab the most recent readings, ignoring the clock!
        vital_ids = [220045, 211, 220179, 220050, 51, 220277, 646, 223761, 678, 220210, 618]
        filtered_df = df[df['itemid'].isin(vital_ids)]
        
        if filtered_df.empty:
            filtered_df = df  # fallback if none of the specific IDs are found
            
        trend_data = filtered_df.sort_values('charttime').tail(15)
        
        results = []
        for _, row in trend_data.iterrows():
            item_id = row['itemid']
            label = loader.item_dict.get(item_id, f"Unknown({item_id})")
            val = row['valuenum']
            uom = row.get('valueuom', '')
            time_str = str(row['charttime'])
            results.append(f"[{time_str}] {label} (ID: {item_id}): {val} {uom}")
            
        vit_data = "\n".join(results)
        
        return (
            f"Vitals scanning completed for patient {patient_id}.\n"
            f"Here are the most recent 10 records found:\n{vit_data}\n\n"
            f"Note to Agent: Please analyze these records for anomalies like missing expected vitals or abnormal values."
        )

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

class MedicationCheckTool(BaseTool):
    name: str = "Check Medication"
    description: str = (
        "Looks up standard treatment protocols based on a given diagnosis. "
        "Returns recommended medications, standard dosages, and prominent contraindications."
    )

    def _run(self, diagnosis: str) -> str:
        diagnosis = diagnosis.lower()
        if "pneumonia" in diagnosis:
            return (
                "Standard Treatment for Pneumonia (Community Acquired/Hospital Acquired):\n"
                "- Primary Option: Ceftriaxone 1g IV daily + Azithromycin 500mg IV daily.\n"
                "- Alternative (if Penicillin/Cephalosporin allergy): Levofloxacin 750mg IV daily.\n"
                "- Contraindications: Avoid Levofloxacin in patients with prolonged QTc intervals."
            )
        elif "sepsis" in diagnosis:
            return (
                "Standard Treatment for Sepsis (Unknown Origin):\n"
                "- Primary Option: Vancomycin (dose based on pharmacy consult) + Cefepime 2g IV every 8h.\n"
                "- Contraindications: Adjust Cefepime dose for renal impairment."
            )
        elif "stemi" in diagnosis or "myocardial infarction" in diagnosis or "heart attack" in diagnosis:
            return (
                "Standard Treatment for STEMI (ST-Elevation Myocardial Infarction):\n"
                "- Primary Option: Aspirin 325mg chewed, Clopidogrel 300-600mg, Heparin infusion, Nitroglycerin."
                "- Contraindications: Avoid Nitroglycerin if patient is hypotensive (low Blood Pressure) or severely bradycardic."
            )
        else:
            return f"No standard protocol found in database for '{diagnosis}'. Recommend general supportive care and consult infectious disease if infection suspected."

# Export instances for agents to use
vitals_tool = VitalsMonitorTool()
history_tool = PatientHistoryTool()
escalation_tool = EscalationTool()
medication_tool = MedicationCheckTool()
