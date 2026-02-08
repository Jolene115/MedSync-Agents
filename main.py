import os
from core.crew import HospitalSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("## Welcome to the MedSync Agents: Hospital Multi-Agent Coordination Platform")
    print("-------------------------------------------------------------")
    
    patient_id = input("Enter Patient ID (P001, P002, P003): ") or "P001"
    
    print(f"\n[INFO] Starting Simulation for Patient: {patient_id}...\n")
    
    hospital_system = HospitalSystem()
    result = hospital_system.run(patient_id=patient_id)
    
    print("\n\n########################")
    print("## FINAL COORDINATION RESULT ##")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    main()
