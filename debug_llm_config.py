from agents.hospital_agents import HospitalAgents
import os

# Mock API key for testing instantiation (not execution)
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-instantiation-only"

try:
    agents = HospitalAgents()
    print("Attempting to create Triage Nurse (expecting gpt-4o-mini)...")
    nurse = agents.triage_nurse()
    print(f"Success! Nurse LLM Model: {nurse.llm.model}")
    
    print("Attempting to create Diagnostic Specialist (expecting gpt-4o)...")
    specialist = agents.diagnostic_specialist()
    print(f"Success! Specialist LLM Model: {specialist.llm.model}")

except Exception as e:
    print(f"Failed: {e}")
