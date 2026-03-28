# HEA — Hospital Emergency Allocation System
### Team LUMEN · HackCraft 3.0

A full-stack hospital resource management system with AI-powered demand forecasting,
real-time bed tracking, and automated alerts.

---

## What this project does

| Feature | What it means |
|---|---|
| Live bed dashboard | See every bed in every ward — available, occupied, or in maintenance |
| Patient admission | Admit a patient and auto-assign them a bed in one click |
| AI forecast | Predicts how many patients will arrive in the next 72 hours |
| Surge alerts | Automatically warns when occupancy is high or ICU beds are low |
| Resource tracking | Track ventilators, OT rooms, oxygen cylinders etc. |
| Audit log | Every action is logged — who did what and when |
| PDF reports | Download a formatted report of the current hospital status |

---

## Tech stack (beginner-friendly)

| Layer | Technology | Why |
|---|---|---|
| Backend | Python + Flask | Simple, beginner-friendly web framework |
| Database | SQLite | No installation needed, file-based |
| ML model | Scikit-learn (Random Forest) | Simple, accurate, works offline |
| Frontend | HTML + CSS + JavaScript | No framework needed, runs in any browser |
| PDF | ReportLab | Python PDF generation |

---

## Setup — Step by step (complete beginner guide)

### Step 1 — Install Python
If you don't have Python installed:
- Go to https://python.org/downloads
- Download Python 3.11 or newer
- During install, CHECK the box that says "Add Python to PATH"

To verify: open a terminal and type:
```
python --version
```
You should see something like: `Python 3.11.x`

---

### Step 2 — Download the project
If you have git:
```bash
git clone <your-repo-url>
cd hea-project
```

Or just download the ZIP and extract it.

---

### Step 3 — Install dependencies
Open a terminal in the `backend/` folder and run:

```bash
cd backend
pip install -r requirements.txt
```

This installs Flask, Scikit-learn, Pandas, and ReportLab.

If you get a permission error, use:
```bash
pip install -r requirements.txt --user
```

---

### Step 4 — Train the ML model (one time only)
Still inside the `backend/` folder:

```bash
python ml/train_model.py
```

You should see output like:
```
Model for 'admissions' — MAE: 3.2
Model for 'icu_admissions' — MAE: 1.1
Model for 'emergency_admissions' — MAE: 2.4
Models saved to .../hea_model.pkl
```

This creates a trained model file. You only need to do this once.

---

### Step 5 — Run the backend
Still inside the `backend/` folder:

```bash
python app.py
```

You should see:
```
Initialising HEA database...
HEA API running at http://localhost:5000
```

Leave this terminal open! The server needs to keep running.

---

### Step 6 — Open the frontend
Open a NEW terminal window (or just use your file explorer).

Go into the `frontend/` folder and open `index.html` in your browser.

The easiest way: double-click `frontend/index.html`

OR from terminal:
```bash
# On Windows:
start frontend/index.html

# On Mac:
open frontend/index.html

# On Linux:
xdg-open frontend/index.html
```

Login with: **admin / admin123**

---

## Folder structure explained

```
hea-project/
│
├── backend/
│   ├── app.py              ← Start here. This is the main server.
│   ├── db.py               ← Database setup and connection
│   ├── alerts.py           ← Logic that checks for shortages
│   ├── requirements.txt    ← List of Python packages needed
│   │
│   ├── models/
│   │   ├── bed.py          ← Functions for bed allocation
│   │   └── patient.py      ← Functions for admitting/discharging
│   │
│   ├── ml/
│   │   ├── train_model.py  ← Run once to train the AI model
│   │   ├── predict.py      ← Makes predictions using trained model
│   │   └── sample_data.csv ← Historical data the model learns from
│   │
│   └── reports/
│       └── generate_pdf.py ← Creates PDF reports
│
├── frontend/
│   ├── index.html          ← Login page
│   ├── dashboard.html      ← Main dashboard
│   ├── beds.html           ← Visual bed map
│   ├── forecast.html       ← 72-hour prediction chart
│   ├── reports.html        ← Audit log and PDF download
│   │
│   ├── css/
│   │   └── style.css       ← All visual styling
│   │
│   └── js/
│       └── dashboard.js    ← Dashboard logic
│
├── database/
│   └── hea.db              ← Auto-created when you run app.py
│
└── README.md               ← This file
```

---

## API endpoints (for developers)

| Method | URL | What it does |
|---|---|---|
| GET | /api/health | Check if API is running |
| GET | /api/dashboard | Full dashboard summary |
| GET | /api/beds | All beds |
| GET | /api/beds/summary | Occupancy by ward |
| POST | /api/beds/allocate | Assign bed to patient |
| POST | /api/beds/release | Free up a bed |
| PUT | /api/beds/:id/status | Update bed status |
| GET | /api/patients | All active patients |
| POST | /api/patients/admit | Admit new patient |
| POST | /api/patients/:id/discharge | Discharge patient |
| GET | /api/forecast | 72h AI predictions |
| GET | /api/alerts | Active shortage alerts |
| GET | /api/resources | Equipment list |
| PUT | /api/resources/:id | Update resource count |
| GET | /api/reports/audit | Audit log |
| GET | /api/reports/pdf | Download PDF report |
| GET | /api/staff | Staff on duty |

---

## Improvements made over original pitch

1. **Full working code** — not just slides, this actually runs
2. **Auto bed assignment** — admits a patient and assigns bed in one API call
3. **Indian holiday calendar** — forecast accounts for Diwali, Republic Day etc.
4. **Audit trail** — every action logged with timestamp
5. **PDF export** — one-click professional report download
6. **Graceful fallback** — forecast works even before ML model is trained
7. **Auto-refresh** — dashboard updates every 30 seconds without reload
8. **Visual bed map** — click any bed cell to change its status
9. **Alert severity levels** — critical vs warning, not just one type
10. **Works fully offline** — SQLite, no cloud needed

---

## Common errors and fixes

**"python: command not found"**
→ Use `python3` instead of `python`, or reinstall Python with PATH option checked.

**"No module named flask"**
→ Run `pip install -r requirements.txt` again inside the `backend/` folder.

**Dashboard shows "API not reachable"**
→ Make sure `python app.py` is still running in another terminal.

**PDF download fails**
→ Run `pip install reportlab` separately.

**Port 5000 already in use**
→ Change the last line of `app.py` from `port=5000` to `port=5001`, and update `const API = ...` in all JS files to match.

---

## Next steps to make it production-ready

- Add real login with hashed passwords (use `flask-login` + `bcrypt`)
- Move to PostgreSQL for larger hospitals
- Add WebSocket for truly real-time updates (use `flask-socketio`)
- Deploy on a hospital intranet server (use `gunicorn`)
- Add more training data to improve ML accuracy
- Add SMS alerts via Twilio API
- Build a mobile app using the existing REST API
