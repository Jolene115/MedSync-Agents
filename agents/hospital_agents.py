from crewai import Agent, LLM
from tools.medical_tools import vitals_tool, history_tool, escalation_tool

class HospitalAgents:
    def triage_nurse(self):
        return Agent(
            role='Triage Nurse',
            goal='Monitor patient vitals and flag any signs of instability immediately.',
            backstory='You are an expert ICU nurse specializing in pneumonia cases. You have a sharp eye for detail. you strictly follow medical protocols and prioritize patient safety above all else. You do not diagnose, you only observe and report.',
            tools=[vitals_tool],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="gpt-4o-mini")
        )

    def diagnostic_specialist(self):
        return Agent(
            role='Diagnostic Specialist',
            goal='Analyze flagged patient data to determine the root cause and severity.',
            backstory='You are a senior specialist with 20 years of ICU experience. You look at the holistic picture, checking patient history and current vitals to rule out chronic conditions vs acute emergencies.',
            tools=[history_tool],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="gpt-4o")
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
