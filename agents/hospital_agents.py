from crewai import Agent, LLM
from tools.medical_tools import vitals_tool, history_tool, escalation_tool, medication_tool

class HospitalAgents:
    def triage_nurse(self):
        return Agent(
            role='Triage Nurse',
            goal='Scan patient vitals and identify physiological signals that deviate from standard medical ranges, regardless of the diagnosis.',
            backstory='You are a senior ICU nurse. Your role is to scan CHARTEVENTS.csv for any patient ID and identify physiological signals (vitals) that deviate from standard medical ranges, regardless of the diagnosis.',
            tools=[vitals_tool],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="gpt-4o-mini")
        )

    def diagnostic_specialist(self):
        return Agent(
            role='Diagnostic Specialist',
            goal='Analyze patient data and vitals to determine if anomalies indicate a critical deterioration for their specific admission diagnosis.',
            backstory='You are a Consultant Physician. Your role is to retrieve the official ADMISSION_DIAGNOSIS from ADMISSIONS.csv for the current patient and determine if the vitals found by the nurse indicate a critical deterioration for that specific condition.',
            tools=[history_tool],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="gpt-4o")
        )

    def clinical_pharmacist(self):
        return Agent(
            role='Clinical Pharmacist',
            goal='Identify the Standard of Care for the confirmed diagnosis and validate the safety of proposed medications.',
            backstory='You are an expert in pharmacology. Your role is to identify the Standard of Care for the diagnosis confirmed by the Specialist and validate the safety of the proposed medications against the patient\'s vitals and history.',
            tools=[medication_tool, history_tool],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="gpt-4o-mini")
        )

    def ward_coordinator(self):
        return Agent(
            role='Ward Coordinator',
            goal='Manage hospital resources and execute final decisions based on medical diagnosis.',
            backstory='You are the operational backbone of the ward. You ensure that patients get the right resources (doctors, beds, medication) based on the severity of their condition. You are efficient and decisive.',
            tools=[escalation_tool],
            verbose=True,
            allow_delegation=False
        )
