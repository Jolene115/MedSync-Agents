from crewai.tools import BaseTool
from pydantic import Field
from data.mimic_loader import MimicLoader
from datetime import datetime, timedelta

# Initialize data loader
loader = MimicLoader()

# Shared escalation log — read by the Streamlit UI to render escalation decisions
escalation_log = []


class VitalsMonitorTool(BaseTool):
    name: str = "Monitor Vitals"
    description: str = (
        "Reads the most recent vital signs records for a given patient_id. "
        "Returns the last 10 readings regardless of the exact time, ensuring data is found."
    )

    def _run(self, patient_id: str) -> str:
        df = loader.get_patient_data(patient_id)
        if df is None or df.empty:
            return "Error: No data found for this patient."

        # Demo mode: retrieve latest available readings from the MIMIC-III static dataset.
        # In production, this would be replaced by an HL7 FHIR R4 real-time observation feed.
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
        entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "recommendation": recommendation,
            "reason": reason
        }
        escalation_log.append(entry)
        return (
            f"ESCALATION LOGGED: Severity={severity}, "
            f"Action={recommendation}, Reason={reason}"
        )


class MedicationCheckTool(BaseTool):
    name: str = "Check Medication"
    description: str = (
        "Looks up standard treatment protocols based on a given diagnosis. "
        "Returns recommended medications, standard dosages, and prominent contraindications."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # Protocol Database — covers all 4 featured landing page cases + common
    # conditions. Structured to mirror hospital formulary reference patterns.
    # ═══════════════════════════════════════════════════════════════════════
    PROTOCOL_DB: dict = {
        # ── Cardiac ──
        "stemi": {
            "match": ["stemi", "myocardial infarction", "heart attack", "mi ", "nstemi"],
            "protocol": (
                "Standard Treatment for STEMI (ST-Elevation Myocardial Infarction):\n"
                "- Dual Antiplatelet: Aspirin 325mg chewed STAT + Clopidogrel 300-600mg loading dose.\n"
                "- Anticoagulation: Heparin IV bolus 60 U/kg (max 4000 U), then 12 U/kg/hr infusion.\n"
                "- Vasodilator: Nitroglycerin 0.4mg SL, may repeat x3 at 5-min intervals.\n"
                "- Beta-Blocker: Metoprolol 25mg PO if hemodynamically stable.\n"
                "- Contraindications: Avoid Nitroglycerin if SBP < 90 mmHg, HR < 50 bpm, or "
                "suspected right ventricular infarction. Avoid Beta-Blockers in cardiogenic shock.\n"
                "- Monitoring: Serial troponin q6h, continuous telemetry, 12-lead ECG q15min."
            ),
        },
        "heart_failure": {
            "match": ["heart failure", "chf", "congestive", "cardiomyopathy"],
            "protocol": (
                "Standard Treatment for Heart Failure (Acute Decompensated):\n"
                "- Diuretic: Furosemide 40-80mg IV bolus, titrate to urine output.\n"
                "- ACE Inhibitor: Enalapril 2.5-5mg PO BID (if tolerated, SBP > 90).\n"
                "- Beta-Blocker: Carvedilol 3.125mg PO BID (initiate when euvolemic).\n"
                "- Vasodilator: Nitroglycerin IV if SBP > 110 mmHg with pulmonary edema.\n"
                "- Contraindications: Avoid ACE-I if hyperkalemia (K+ > 5.5) or bilateral renal "
                "artery stenosis. Hold Beta-Blocker in acute decompensation with hypotension.\n"
                "- Monitoring: Daily weights, strict I&O, BMP q12h for renal function and potassium."
            ),
        },
        "afib": {
            "match": ["atrial fibrillation", "afib", "a-fib", "a fib"],
            "protocol": (
                "Standard Treatment for Atrial Fibrillation:\n"
                "- Rate Control: Metoprolol 5mg IV q5min x3, then 25-50mg PO BID. "
                "Alternative: Diltiazem 0.25mg/kg IV bolus, then 5-15mg/hr infusion.\n"
                "- Rhythm Control (if indicated): Amiodarone 150mg IV over 10 min, then 1mg/min x6h.\n"
                "- Anticoagulation: Apixaban 5mg PO BID (preferred) or Warfarin with INR target 2-3.\n"
                "- Contraindications: Avoid Amiodarone if thyroid disease or hepatic impairment. "
                "Reduce Apixaban to 2.5mg if CrCl < 25 mL/min, age ≥ 80, or weight ≤ 60kg.\n"
                "- Monitoring: Thyroid and liver function q3-6 months on Amiodarone."
            ),
        },

        # ── Respiratory ──
        "pneumonia": {
            "match": ["pneumonia", "cap ", "community acquired", "hospital acquired", "hap "],
            "protocol": (
                "Standard Treatment for Pneumonia (Community Acquired / Hospital Acquired):\n"
                "- Primary Option: Ceftriaxone 1g IV daily + Azithromycin 500mg IV daily.\n"
                "- Alternative (PCN/Cephalosporin allergy): Levofloxacin 750mg IV daily.\n"
                "- Severe/ICU: Add Vancomycin if MRSA risk factors present.\n"
                "- Contraindications: Avoid Levofloxacin in patients with prolonged QTc interval "
                "(> 500ms) or concurrent QTc-prolonging agents. Monitor for C. difficile.\n"
                "- Monitoring: Repeat chest imaging at 48-72h if no clinical improvement."
            ),
        },
        "pulmonary_embolism": {
            "match": ["pulmonary embolism", "embolism", "pe ", "vte", "dvt", "deep vein"],
            "protocol": (
                "Standard Treatment for Pulmonary Embolism / VTE:\n"
                "- Anticoagulation (Initial): Heparin IV bolus 80 U/kg, then 18 U/kg/hr. "
                "Target aPTT 60-80 seconds.\n"
                "- Alternative: Enoxaparin (LMWH) 1mg/kg SC q12h if hemodynamically stable.\n"
                "- Oral Transition: Rivaroxaban 15mg PO BID x21 days, then 20mg daily. "
                "Or Warfarin bridging with INR target 2-3.\n"
                "- Massive PE: Consider tPA (Alteplase 100mg IV over 2h) if hemodynamic instability.\n"
                "- Contraindications: Anticoagulation contraindicated if active hemorrhage, "
                "recent surgery (< 14 days), or history of heparin-induced thrombocytopenia (HIT). "
                "Reduce LMWH dose if CrCl < 30 mL/min.\n"
                "- Monitoring: aPTT q6h for heparin, anti-Xa levels for LMWH, INR for warfarin."
            ),
        },

        # ── Infectious ──
        "sepsis": {
            "match": ["sepsis", "septic", "sirs", "bacteremia", "systemic infection"],
            "protocol": (
                "Standard Treatment for Sepsis (Surviving Sepsis Campaign Guidelines):\n"
                "- Hour-1 Bundle: Obtain blood cultures x2, then start empiric antibiotics immediately.\n"
                "- Primary Option: Vancomycin 25-30mg/kg IV loading dose + Cefepime 2g IV q8h. "
                "Add Metronidazole 500mg IV q8h if intra-abdominal source suspected.\n"
                "- Fluid Resuscitation: Lactated Ringer's 30 mL/kg IV bolus within first 3 hours.\n"
                "- Vasopressor: Norepinephrine 0.1-0.5 mcg/kg/min if MAP < 65 after fluids.\n"
                "- Contraindications: Adjust Cefepime dose for renal impairment (CrCl < 60: q12h; "
                "CrCl < 30: q24h). Monitor Vancomycin trough (target 15-20 mcg/mL).\n"
                "- Monitoring: Lactate clearance q2-4h, procalcitonin trend, daily renal panel."
            ),
        },

        # ── GI ──
        "gi_bleed": {
            "match": ["gi bleed", "gastrointestinal bleed", "upper gi", "lower gi", "melena", "hematemesis"],
            "protocol": (
                "Standard Treatment for GI Hemorrhage:\n"
                "- Resuscitation: 2 large-bore IVs, crossmatch 4 units pRBC, volume resuscitation.\n"
                "- PPI: Pantoprazole 80mg IV bolus, then 8mg/hr continuous infusion.\n"
                "- Octreotide: 50mcg IV bolus then 50mcg/hr if variceal bleed suspected.\n"
                "- Contraindications: HOLD all anticoagulants and antiplatelet agents. "
                "Avoid NSAIDs. Avoid NG tube if variceal bleed suspected.\n"
                "- Monitoring: Serial hemoglobin q6h, hemodynamic monitoring, urgent GI consult for EGD."
            ),
        },

        # ── Neurological ──
        "stroke": {
            "match": ["stroke", "cva", "cerebrovascular", "tia", "ischemic stroke"],
            "protocol": (
                "Standard Treatment for Acute Ischemic Stroke:\n"
                "- Thrombolysis: Alteplase (tPA) 0.9mg/kg IV (max 90mg) if within 4.5h of onset. "
                "10% bolus, remainder over 60 minutes.\n"
                "- Antihypertensive: Labetalol 10-20mg IV if SBP > 185 pre-tPA.\n"
                "- Antiplatelet: Aspirin 325mg PO at 24h post-tPA (or immediately if tPA not given).\n"
                "- Contraindications: tPA contraindicated if INR > 1.7, platelets < 100k, "
                "recent major surgery, or active internal bleeding.\n"
                "- Monitoring: NIH Stroke Scale q1h x24h, BP q15min during tPA infusion."
            ),
        },
    }

    def _run(self, diagnosis: str) -> str:
        diagnosis_lower = diagnosis.lower()
        for _key, entry in self.PROTOCOL_DB.items():
            if any(term in diagnosis_lower for term in entry["match"]):
                return entry["protocol"]

        return (
            f"No specific protocol found in formulary for '{diagnosis}'. "
            f"Recommend empiric supportive care and specialist consultation. "
            f"Consider broad-spectrum coverage if infectious etiology suspected."
        )


# Export instances for agents to use
vitals_tool = VitalsMonitorTool()
history_tool = PatientHistoryTool()
escalation_tool = EscalationTool()
medication_tool = MedicationCheckTool()
