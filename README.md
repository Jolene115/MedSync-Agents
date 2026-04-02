# 🏥 MedSync-Agents

### Multi-Agent Clinical Coordination with Human-in-the-Loop Safety

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medsync-agents.streamlit.app)
&nbsp;&nbsp;![Python](https://img.shields.io/badge/Python-3.11-blue)
&nbsp;&nbsp;![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-orange)
&nbsp;&nbsp;![MIMIC-III](https://img.shields.io/badge/Data-MIMIC--III-green)

> 👉 **[Try the Live Demo →](https://medsync-agents.streamlit.app)**

---

## 🔍 The Problem

Clinical AI systems face a fundamental trust barrier: **the Black Box problem**. When an AI recommends a medication or escalation decision, clinicians cannot see *why* — making it unsafe for real-world adoption.

MedSync-Agents solves this by combining **multi-agent specialization** (each agent has a clearly defined clinical role) with a **Human-in-the-Loop safety checkpoint** that pauses AI execution for human review before any final decision is made.

Built on **99 de-identified patients** from the [MIMIC-III Clinical Database](https://physionet.org/content/mimiciii/1.4/) (Beth Israel Deaconess Medical Center).

---

## 🧠 How It Works — Segmented Crew Architecture

The system uses a **two-phase execution model** that physically separates AI analysis from final decision-making:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: AI Analysis                         │
│                                                                 │
│   🩺 Triage Nurse ──→ 🧠 Diagnostic Specialist ──→ 💊 Pharmacist │
│   (Reads Vitals)      (Differential Diagnosis)   (Drug Safety)  │
│                                                                 │
├─────────────────────── 🚨 SYSTEM PAUSES ────────────────────────┤
│                                                                 │
│              HUMAN-IN-THE-LOOP CHECKPOINT                       │
│    ┌──────────────────────────────────────────┐                 │
│    │  Clinician reviews AI medication plan    │                 │
│    │  ✏️  Edit dosages                         │                 │
│    │  ❌  Remove contraindicated drugs         │                 │
│    │  ⚠️  Override severity assessment         │                 │
│    └──────────────────────────────────────────┘                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    PHASE 2: Executive Decision                  │
│                                                                 │
│                    📋 Ward Coordinator                           │
│         (Incorporates human overrides into final report)        │
│         (ICU vs. General Ward allocation + Severity Score)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why Two Phases?

This is the **Segmented Crew Handoff** — a deliberate architectural choice:

- **Phase 1** runs as a single CrewAI sequential crew (3 agents)
- The system **physically stops execution** — not a prompt pause, but an actual code-level break
- The human edits are injected as the **"Gold Standard"** into Phase 2
- **Phase 2** runs a separate CrewAI crew where the Ward Coordinator is contractually bound to respect human overrides

This means the AI **cannot bypass human judgment** — it is architecturally impossible, not just prompt-enforced.

---

## 📊 Dashboard

| Feature | Description |
|---------|-------------|
| **Patient Context** | Auto-loads demographics, diagnosis, and admission timeline |
| **Vitals Trends** | Disease-adaptive charts (Resp Rate for Pneumonia, BP for STEMI, Temp for Sepsis) |
| **Live Coordination Feed** | Real-time agent reasoning with expandable "Clinical Thinking" panels |
| **Criticality Gauge** | Severity Score (0–10) with color-coded risk zones |
| **Clinical Override** | Editable text area for human medication/severity adjustments |
| **Downloadable Report** | Export the final coordination report as documentation |

---

## 🏗️ Architecture

```
app.py                       # Streamlit dashboard + HITL State Machine
├── core/
│   └── crew.py              # Bifurcated CrewAI engine
│                            #   └── run_initial_phase()  → Agents 1-3
│                            #   └── run_final_phase()    → Agent 4 + human input
├── agents/
│   └── hospital_agents.py   # Agent role definitions
├── tools/
│   └── medical_tools.py     # MIMIC-III data tools (vitals, history, meds)
├── data/
│   ├── mimic_loader.py      # Dynamic patient data loader
│   ├── ADMISSIONS.csv       # 99 de-identified admission records
│   ├── PATIENTS.csv         # Patient demographics
│   └── processed/           # Per-patient vitals (99 files)
└── pages/
    └── 1_IoE_Theory.py      # IoE architecture reference
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Orchestration** | [CrewAI](https://crewai.com) + [LangChain](https://langchain.com) |
| **LLM** | OpenAI GPT-4o-mini |
| **Frontend** | [Streamlit](https://streamlit.io) + Plotly |
| **Clinical Data** | [MIMIC-III](https://physionet.org/content/mimiciii/1.4/) (PhysioNet) |
| **Deployment** | Streamlit Community Cloud |

---

## 🧪 Patient Directory — 99 Testable Cases

Enter any Patient ID into the dashboard. Recommended demo cases:

| Patient ID | Diagnosis | What to Look For |
|---|---|---|
| **40124** | Shortness of Breath | Resp Rate + SpO2 trends |
| **40503** | STEMI (Heart Attack) | Heart Rate + BP, drug contraindications |
| **10006** | Sepsis | Temperature + HR, broad-spectrum antibiotics |
| **41976** | Pneumonia | Classic respiratory protocol |
| **43881** | Acute Pulmonary Embolism | Emergency escalation |

<details>
<summary>View all 99 Patient IDs</summary>

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

## 📄 Data Source

This project uses the **MIMIC-III Clinical Database** (v1.4), a freely available dataset of de-identified health records from Beth Israel Deaconess Medical Center. All patient IDs are synthetic and contain no real personal health information.

> Johnson, A., Pollard, T., & Mark, R. (2016). MIMIC-III Clinical Database. PhysioNet. https://doi.org/10.13026/C2XW26

---

## 📝 License

This project is for academic and research purposes.
