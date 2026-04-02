from crewai import Crew, Task, Process
from agents.hospital_agents import HospitalAgents
from tools.medical_tools import vitals_tool, history_tool, escalation_tool, medication_tool

class HospitalSystem:
    def __init__(self):
        self.agents = HospitalAgents()

    def run_initial_phase(self, patient_id, diagnosis="Unknown", step_callback=None):
        # 1. Define Agents
        nurse = self.agents.triage_nurse()
        specialist = self.agents.diagnostic_specialist()
        pharmacist = self.agents.clinical_pharmacist()

        # 2. Define Tasks
        format_rules = "Format Rules: Use clear Markdown headers (###) for each section. Use bullet points for vital readings. NEVER use escaped characters like \\n in your final answer; provide raw, readable text that a human doctor can immediately act upon.\n\nCRITICAL: You MUST end your response with exactly these two sections:\n### KEY FINDING:\n(One sentence summarizing the single most important clinical finding)\n### RECOMMENDATION:\n(One actionable sentence for the next clinician in the chain)"

        # Task 1: Monitoring
        monitor_task = Task(
            description=f'As the Triage Nurse, begin by identifying yourself and stating your task: monitoring vitals for Subject {patient_id}. Analyze these vitals and flag any anomalies for the team. Do not assume a diagnosis.\n\n{format_rules}',
            expected_output='A report on the current vitals, identified trends, and any flagged anomalies based on a single tool reading. MUST end with ### KEY FINDING: and ### RECOMMENDATION: sections.',
            agent=nurse,
            tools=[vitals_tool]
        )

        # Task 2: Diagnosis
        diagnosis_task = Task(
            description=f'As the Diagnostic Specialist, you must acknowledge the work done by the Triage Nurse. Read the diagnosis from ADMISSIONS.csv. Compare it to the Nurse\'s flags. Provide a Differential Diagnosis for this {diagnosis} case. Your output must be clear for the Pharmacist.\n\n{format_rules}',
            expected_output='A definitive diagnostic assessment, a differential diagnosis ruling out other conditions, and a severity level (Low, Medium, High). MUST end with ### KEY FINDING: and ### RECOMMENDATION: sections.',
            agent=specialist,
            context=[monitor_task],
            tools=[history_tool]
        )

        # Task 3: Pharmacy Review
        pharmacy_task = Task(
            description=f'As the Clinical Pharmacist, you must acknowledge the work done by the Diagnostic Specialist. The Pharmacist\'s output is a MANDATORY prerequisite for the Ward Coordinator. Review the Specialist\'s diagnosis. Recommend a medication plan based on {diagnosis}. Crucial: Perform a safety check against the patient\'s current vitals and history.\n\n{format_rules}',
            expected_output='A treatment plan outlining the prescribed medication, validated side effects context, dosage, and rationale considering the patient history. MUST end with ### KEY FINDING: and ### RECOMMENDATION: sections.',
            agent=pharmacist,
            context=[diagnosis_task],
            tools=[medication_tool, history_tool]
        )

        # 3. Create Crew (Phase 1)
        initial_crew = Crew(
            agents=[nurse, specialist, pharmacist],
            tasks=[monitor_task, diagnosis_task, pharmacy_task],
            process=Process.sequential,
            step_callback=step_callback,
            verbose=True
        )

        result = initial_crew.kickoff()
        return result

    def run_final_phase(self, patient_id, diagnosis="Unknown", human_input="", step_callback=None):
        coordinator = self.agents.ward_coordinator()
        format_rules = "Format Rules: Use clear Markdown headers (###) for each section. Use bullet points for vital readings. NEVER use escaped characters like \\n in your final answer; provide raw, readable text that a human doctor can immediately act upon."

        # Task 4: Coordination
        coordination_task = Task(
            description=f'Task Contract: You are the Ward Coordinator. Your primary directive is to finalize the clinical coordination report for Patient {patient_id}.\n\nInstructions for Human-in-the-Loop Integration:\n1. You will be provided with the "Initial AI Plan" and the "Human Consultant\'s Directives" ({human_input}).\n2. You MUST prioritize the Human Consultant\'s directives over any previous agent outputs. If the human has modified a dosage, severity score, or allocation, you must adopt that change as the absolute truth.\n3. Your final report MUST start with the following header: \'✅ This report has been reviewed and modified by the Human Consultant.\'\n4. In your summary, explicitly state: \'Per human override, the [Medication/Severity/Allocation] was updated to [New Value].\'\n\n{format_rules}',
            expected_output='Final action plan and resource/Level of Care allocation decision, including prescribed medication and a distinct Severity Score: X/10.',
            agent=coordinator,
            tools=[escalation_tool]
        )

        # Create Crew (Phase 2)
        final_crew = Crew(
            agents=[coordinator],
            tasks=[coordination_task],
            process=Process.sequential,
            step_callback=step_callback,
            verbose=True
        )

        result = final_crew.kickoff()
        return result
