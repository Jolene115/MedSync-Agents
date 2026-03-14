import pandas as pd
import os

# 1. Configuration
RAW_FILE = 'data/raw/CHARTEVENTS.csv'
PROCESSED_FOLDER = 'data/processed/'

def extract_patient_data(patient_id):
    """Dynamically extracts vitals for a specific patient ID from the raw dataset."""
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    try:
        target_id = int(patient_id)
    except ValueError:
        print(f"Error: Invalid patient ID '{patient_id}'")
        return False
        
    output_file = os.path.join(PROCESSED_FOLDER, f'patient_{target_id}_vitals.csv')
    
    # Safety: Remove existing file to avoid appending duplicates
    if os.path.exists(output_file):
        os.remove(output_file)

    print(f"Starting dynamic extraction for Patient {target_id}...")

    # 3. Read in chunks (Crucial for large files)
    try:
        chunks = pd.read_csv(RAW_FILE, chunksize=200000, low_memory=False)
        
        found_any = False
        for chunk in chunks:
            # Filter for the patient
            patient_data = chunk[chunk['subject_id'] == target_id]
            
            # Write to the working file
            if not patient_data.empty:
                if not found_any: # First time writing
                     patient_data.to_csv(output_file, mode='w', index=False)
                else: # Rest of the time appending
                     patient_data.to_csv(output_file, mode='a', index=False, header=False)
                
                found_any = True
                print(f"  Found {len(patient_data)} rows...")

        if found_any:
            print(f"Done! Data for {target_id} is ready at: {output_file}")
            return True
        else:
            print(f"Warning: No data found in CHARTEVENTS for patient {target_id}")
            return False

    except FileNotFoundError:
        print(f"Error: Could not find {RAW_FILE}. Please move CHARTEVENTS.csv there!")
        return False

# For direct script execution
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_patient_data(sys.argv[1])
    else:
        print("Please provide a patient ID. Example: python data/process_mimic.py 40124")