import os
from core.crew import HospitalSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("## Welcome to the MedSync Agents: Hospital Multi-Agent Coordination Platform")
    print("-------------------------------------------------------------")
    
    # Default to 40124 (Our processed patient)
    patient_id = input("Enter Patient ID (Default: 40124): ") or "40124"
    
    print(f"\n[INFO] Starting Simulation for Patient: {patient_id}...\n")
    
    hospital_system = HospitalSystem()
    initial_result = hospital_system.run_initial_phase(patient_id=patient_id)
    
    print("\n[HITL] Pharmacist's Proposed Plan:")
    print(initial_result)
    override = input("\nEdit the plan or press Enter to approve as-is: ") or str(initial_result)
    
    result = hospital_system.run_final_phase(patient_id=patient_id, human_input=override)
    
    print("\n\n########################")
    print("## FINAL COORDINATION RESULT ##")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    main()
