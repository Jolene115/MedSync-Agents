from agents.hospital_agents import HospitalAgents
try:
    agents = HospitalAgents()
    print("Attempting to create Triage Nurse...")
    nurse = agents.triage_nurse()
    print("Success! Nurse Agent created with CrewAI native tools.")
    
    print("Tools loaded:", [t.name for t in nurse.tools])
except Exception as e:
    print(f"Failed: {e}")
