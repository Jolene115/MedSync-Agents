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

## 📄 Data Source

This project uses the **MIMIC-III Clinical Database** (v1.4), a freely available dataset of de-identified health records from Beth Israel Deaconess Medical Center. All patient IDs are synthetic and contain no real personal health information.

> Johnson, A., Pollard, T., & Mark, R. (2016). MIMIC-III Clinical Database. PhysioNet. https://doi.org/10.13026/C2XW26

---

## 📝 License

This project is for academic and research purposes.
