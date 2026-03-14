# 🏥 MedSync-Agents — Clinical AI Coordination Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medsync-agents.streamlit.app)

> A multi-agent clinical coordination platform powered by **CrewAI** and **OpenAI**, built on de-identified **MIMIC-III** patient data. Features a **Human-in-the-Loop (HITL)** override system for safe, transparent AI-assisted medical decision-making.

---

## 🚀 Live Demo

👉 **[medsync-agents.streamlit.app](https://medsync-agents.streamlit.app)**

---

## 🧠 What It Does

MedSync-Agents simulates a hospital coordination workflow using four specialized AI agents that collaborate sequentially:

| Stage | Agent | Role |
|-------|-------|------|
| 1 | 🩺 **Triage Nurse** | Monitors patient vitals from CHARTEVENTS and flags anomalies |
| 2 | 🧠 **Diagnostic Specialist** | Reads admission diagnosis and performs differential diagnosis |
| 3 | 💊 **Clinical Pharmacist** | Recommends medication with safety checks against vitals |
| 4 | 📋 **Ward Coordinator** | Finalizes resource allocation (ICU vs. General Ward) with severity scoring |

### Human-in-the-Loop Override

Between Stage 3 and Stage 4, the system **pauses** for human review. A clinician can:
- Review the AI's proposed medication plan
- Edit dosages, remove contraindicated drugs, or adjust severity
- The Ward Coordinator then incorporates these overrides into the final report

This implements a **Segmented Crew Handoff** architecture — a safer alternative to real-time AI decision-making in clinical settings.

---

## 📊 Dashboard Features

- **Patient Context Panel** — Auto-loads demographics and admission diagnosis
- **Vitals Trend Charts** — Disease-adaptive Plotly visualizations (e.g., Resp Rate for Pneumonia, BP for STEMI)
- **Live Coordination Feed** — Real-time agent activity with stage labels and clinical reasoning expanders
- **Criticality Gauge** — Severity Score visualization (0–10) with color-coded risk zones
- **Downloadable Report** — Export the final clinical coordination report as a text file

---

## 🏗️ Architecture

```
app.py                    # Streamlit dashboard with HITL State Machine
├── core/
│   ├── crew.py           # Bifurcated CrewAI engine (Phase 1 + Phase 2)
│   └── agents.py         # Agent role definitions
├── agents/
│   └── hospital_agents.py # Agent configurations
├── tools/
│   └── medical_tools.py  # CSV-based medical tools (vitals, history, meds)
├── data/
│   ├── mimic_loader.py   # Dynamic MIMIC-III data loader
│   ├── process_mimic.py  # Raw data processing script
│   ├── ADMISSIONS.csv    # De-identified admission records
│   ├── PATIENTS.csv      # De-identified patient demographics
│   └── processed/        # Pre-processed patient vitals CSVs
└── main.py               # CLI fallback with terminal HITL
```

---

## 🛠️ Tech Stack

- **AI Framework:** [CrewAI](https://crewai.com) + [LangChain](https://langchain.com)
- **LLM:** OpenAI GPT-4o-mini
- **Frontend:** [Streamlit](https://streamlit.io) with Plotly
- **Data:** [MIMIC-III](https://physionet.org/content/mimiciii/1.4/) (de-identified clinical dataset)

---

## ⚙️ Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Jolene115/MedSync-Agents.git
cd MedSync-Agents

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI API key
echo 'OPENAI_API_KEY=sk-your-key-here' > .env

# 4. Run the dashboard
streamlit run app.py
```

---

## 🧪 Patient Directory — Try These IDs!

All **99 patients** are testable. Enter any ID below into the dashboard. Here are some highlights by category:

### ⭐ Recommended Demo Cases

| Patient ID | Diagnosis | Why It's Interesting |
|---|---|---|
| **40124** | Shortness of Breath | Default patient — Resp Rate + SpO2 trends |
| **40503** | STEMI (Heart Attack) | Cardiac case — Heart Rate + BP trends |
| **10006** | Sepsis | Infection case — Temp + HR trends |
| **41976** | Pneumonia | Classic respiratory case |
| **43881** | Acute Pulmonary Embolism | Emergency presentation |

### Full Patient List

<details>
<summary>Click to expand all 99 Patient IDs</summary>

| ID | Diagnosis | ID | Diagnosis |
|---|---|---|---|
| 10006 | Sepsis | 40124 | Shortness of Breath |
| 10011 | Hepatitis B | 40177 | Acute Cholangitis |
| 10013 | Sepsis | 40204 | Fever; UTI |
| 10017 | Humeral Fracture | 40277 | Syncope; Intracranial Hemorrhage |
| 10019 | Alcoholic Hepatitis | 40286 | Left Hip OA |
| 10026 | Stroke/TIA | 40304 | Mediastinal Adenopathy |
| 10027 | Mitral Regurgitation; CAD/CABG | 40310 | Facial Numbness |
| 10029 | Syncope | 40456 | Pneumonia |
| 10032 | Right Humerus Fracture | 40503 | STEMI |
| 10033 | Renal Failure; Hyperkalemia | 40595 | Tracheal Esophageal Fistula |
| 10035 | Carotid Stenosis | 40601 | Sepsis |
| 10036 | Sepsis | 40612 | Cholecystitis |
| 10038 | Failure to Thrive | 40655 | Cellulitis |
| 10040 | Pulmonary Edema | 40687 | Abdominal Pain |
| 10042 | Unstable Angina | 41795 | Asthma/COPD |
| 10043 | Respiratory Distress | 41914 | Liver Transplant Complications |
| 10044 | Metastatic Melanoma | 41976 | Pneumonia |
| 10045 | Fever | 41983 | S/P Fall |
| 10046 | Brain Metastases | 42033 | Shortness of Breath |
| 10056 | Sepsis | 42066 | Tracheal Stenosis |
| 10059 | Variceal Bleed | 42075 | Inferior MI |
| 10061 | Chest Pain | 42135 | Failure to Thrive |
| 10064 | Subdural Hematoma | 42199 | Chest Pain |
| 10065 | Esophageal Cancer | 42231 | Renal Cancer |
| 10067 | Motorcycle Accident | 42275 | Shortness of Breath |
| 10069 | Seizure | 42281 | Upper GI Bleed |
| 10074 | GI Bleed | 42292 | Pneumonia/Hypoglycemia |
| 10076 | Lung Cancer | 42302 | Asthma/COPD Flare |
| 10083 | Hypotension | 42321 | Failure to Thrive |
| 10088 | Sepsis/Pneumonia | 42346 | Pneumonia |
| 10089 | Basal Ganglia Bleed | 42367 | Seizure; Status Epilepticus |
| 10090 | Overdose | 42412 | Hypoglycemia |
| 10093 | Critical Aortic Stenosis | 42430 | Cerebrovascular Accident |
| 10094 | Hypotension | 42458 | Pneumonia |
| 10098 | Motor Vehicle Accident | 43735 | Hypotension |
| 10101 | Tachypnea | 43746 | Metastatic Melanoma; Anemia |
| 10102 | Chronic Leukemia | 43748 | Hypotension; Renal Failure |
| 10104 | Hyponatremia; UTI | 43779 | Acute Subdural Hematoma |
| 10106 | Headache | 43798 | Esophageal Cancer |
| 10111 | Congestive Heart Failure | 43827 | MI; CHF |
| 10112 | VF Arrest | 43870 | Stroke/TIA |
| 10114 | Pulmonary Edema; MI | 43879 | Pleural Effusion |
| 10117 | Fever | 43881 | Acute Pulmonary Embolism |
| 10119 | Acute Cholecystitis | 43909 | Pneumonia |
| 10120 | Liver Failure | 43927 | CAD/CABG |
| 10124 | Left Hip Fracture | 44083 | Esophageal Cancer |
| 10126 | Liver Failure | 44154 | Altered Mental Status |
| 10127 | Motor Vehicle Accident | 44212 | ARDS; Acute Renal Failure |
| 10130 | Abscess | 44222 | Bradycardia |
| 10132 | Non-Small Cell Lung Cancer | 44228 | Cholangitis |

</details>

---

## 📄 Data Source

This project uses the **MIMIC-III Clinical Database** (v1.4), a freely available dataset of de-identified health records from Beth Israel Deaconess Medical Center. All patient IDs are synthetic and contain no real personal health information.

> Johnson, A., Pollard, T., & Mark, R. (2016). MIMIC-III Clinical Database. PhysioNet. https://doi.org/10.13026/C2XW26

---

## 📝 License

This project is for academic and research purposes.
