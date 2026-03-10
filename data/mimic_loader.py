
import pandas as pd
import os
from datetime import datetime, timedelta

class MimicLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.processed_dir = os.path.join(data_dir, "processed")
        self.item_dict = self._load_item_dict()
        
    def _load_item_dict(self):
        """Loads D_ITEMS.csv to map Item IDs to Labels (e.g., 220045 -> Heart Rate)."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, "D_ITEMS.csv"))
            # Create a dictionary for quick lookup: {220045: "Heart Rate", ...}
            # lower case columns based on file verification
            return dict(zip(df.itemid, df.label))
        except FileNotFoundError:
            return {}

    def get_patient_data(self, patient_id):
        """Reads the processed vitals file for a specific patient."""
        file_path = os.path.join(self.processed_dir, f"patient_{patient_id}_vitals.csv")
        try:
            # Parse dates and sort by time
            df = pd.read_csv(file_path)
            # Ensure columns are lower case just in case
            df.columns = df.columns.str.lower()
            df['charttime'] = pd.to_datetime(df['charttime'])
            df.sort_values('charttime', inplace=True)
            return df
        except FileNotFoundError:
            return None

    def get_vitals_at_time(self, patient_df, current_sim_time):
        """
        Returns the most recent vital signs at or before the current simulation time.
        This simulates 'real-time' monitoring by not looking into the future.
        """
        if patient_df is None or patient_df.empty:
            return {}

        # Filter for rows up to current time
        past_data = patient_df[patient_df['charttime'] <= current_sim_time]
        
        if past_data.empty:
            return {}

        # Get the very last recorded row (most recent state)
        latest_row = past_data.iloc[-1]
        
        # Translate IDs to Names using D_ITEMS
        vitals = {
            "timestamp": latest_row['charttime'],
            "values": {}
        }
        
        # In MIMIC, rows are often single measurements (Long Format). 
        # But our processed file might be pivoting them or keeping them long.
        # If process_mimic.py keeps them long (one row = one measurement), 
        # we might need to look back a few rows to get a complete picture (HR + BP + O2).
        # For simplicity, let's assume we take the last 5 minutes of data to form a 'current state'.
        
        window_start = current_sim_time - timedelta(minutes=15)
        recent_window = past_data[past_data['charttime'] >= window_start]
        
        for _, row in recent_window.iterrows():
            item_id = row['itemid'] # Assuming column is lowercase from processed
            value = row['valuenum']
            label = self.item_dict.get(item_id, f"Unknown({item_id})")
            
            # Clean up labels slightly
            if "Heart Rate" in label: key = "heart_rate"
            elif "Blood Pressure" in label: key = "bp" # Simplified
            elif "O2 saturation" in label: key = "spo2"
            elif "Temperature" in label: key = "temperature"
            else: key = label

            vitals["values"][key] = value
            
        return vitals

    def get_patient_history(self, patient_id):
        """
        Retrieves static patient info (Age, Gender, Diagnosis) by joining 
        ADMISSIONS.csv and PATIENTS.csv.
        """
        try:
            # Load Admissions
            adm_df = pd.read_csv(os.path.join(self.data_dir, "ADMISSIONS.csv"))
            pat_df = pd.read_csv(os.path.join(self.data_dir, "PATIENTS.csv"))
            
            # Filter for Patient
            # Note: In MIMIC, SUBJECT_ID is int. Our input might be string "40124"
            pid = int(patient_id)
            
            adm_record = adm_df[adm_df['subject_id'] == pid]
            pat_record = pat_df[pat_df['subject_id'] == pid]
            
            if adm_record.empty or pat_record.empty:
                return f"No records found for Patient {patient_id}"
                
            # Get latest admission if multiple
            latest_adm = adm_record.iloc[-1]
            patient_info = pat_record.iloc[0]
            
            # Calculate Age (Approximate)
            # MIMIC shifts dates, so age is usually derived from DOB and Admit Time
            # Here we just return the raw DOB for simplicity or calc if year is reasonable
            dob = patient_info.get('dob', 'Unknown')
            gender = patient_info.get('gender', 'Unknown')
            diagnosis = latest_adm.get('diagnosis', 'Unknown')
            
            history_text = (
                f"Patient ID: {patient_id}\n"
                f"Gender: {gender}\n"
                f"Date of Birth: {dob}\n"
                f"Admission Diagnosis: {diagnosis}\n"
                f"Insurance: {latest_adm.get('insurance', 'Unknown')}\n"
                f"Religion: {latest_adm.get('religion', 'Unknown')}\n"
            )
            return history_text
            
        except Exception as e:
            return f"Error retrieving history: {str(e)}"
