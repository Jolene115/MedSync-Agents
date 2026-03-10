from crewai import Crew, Task, Process
from agents.hospital_agents import HospitalAgents
from tools.medical_tools import vitals_tool, history_tool, escalation_tool

class HospitalSystem:
    def __init__(self):
        self.agents = HospitalAgents()

    def run(self, patient_id):
        # 1. Define Agents
        nurse = self.agents.triage_nurse()
        specialist = self.agents.diagnostic_specialist()
        coordinator = self.agents.ward_coordinator()

        # 2. Define Tasks
        # Task 1: Monitoring
        monitor_task = Task(
            description=f'Monitor the vitals for patient {patient_id}. Check if any value is outside the normal range. If everything is normal, report "All Clear". If there is an anomaly, clearly state what it is.',
            expected_output='A report on the current vitals and any flagged anomalies.',
            agent=nurse,
        tools=[vitals_tool]
    )

        # Task 2: Diagnosis
        diagnosis_task = Task(
            description=f'Review the vitals report from the Triage Nurse. Cross-reference with the patient history for {patient_id}. Determine if this is a critical emergency, a chronic issue, or a false alarm. Provide a medical reasoning.',
            expected_output='A diagnostic assessment with severity level (Low, Medium, High) and reasoning.',
            agent=specialist,
            context=[monitor_task],
            tools=[history_tool]
        )

        # Task 3: Coordination
        coordination_task = Task(
            description='Based on the Diagnostic Specialist assessment, determine the necessary resources. If High Severity, escalate to a doctor immediately. If Medium, schedule a checkup. If Low, just log it. Use the Escalate Aleart tool to action this.',
            expected_output='Final action plan and resource allocation decision.',
            agent=coordinator,
            context=[diagnosis_task],
            tools=[escalation_tool]
        )

        # 3. Create Crew
        hospital_crew = Crew(
            agents=[nurse, specialist, coordinator],
            tasks=[monitor_task, diagnosis_task, coordination_task],
            process=Process.sequential,
            verbose=True
        )

        result = hospital_crew.kickoff()
        return result
