"""
models/patient.py  (note: filename is paient.py to match original project)
Functions for admitting, discharging, and querying patients.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from db import get_db


def admit_patient(name, age, gender, condition, priority='normal', ward=None):
    """Insert a new patient row and return the new patient ID."""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO patients (name, age, gender, condition, priority)
           VALUES (?, ?, ?, ?, ?)""",
        (name, int(age), gender, condition, priority)
    )
    patient_id = cur.lastrowid
    conn.execute(
        "INSERT INTO audit_log (action, details) VALUES (?, ?)",
        ("PATIENT_ADMIT", f"Admitted {name} (ID {patient_id}), condition: {condition}, priority: {priority}")
    )
    conn.commit()
    conn.close()
    return patient_id


def discharge_patient(patient_id):
    """Mark a patient as discharged and release their bed."""
    conn = get_db()
    patient = conn.execute(
        "SELECT * FROM patients WHERE id=? AND discharged_at IS NULL", (patient_id,)
    ).fetchone()

    if not patient:
        conn.close()
        return False, "Patient not found or already discharged"

    conn.execute(
        "UPDATE beds SET status='available', patient_id=NULL, updated_at=CURRENT_TIMESTAMP WHERE patient_id=?",
        (patient_id,)
    )
    conn.execute(
        "UPDATE patients SET discharged_at=CURRENT_TIMESTAMP WHERE id=?",
        (patient_id,)
    )
    conn.execute(
        "INSERT INTO audit_log (action, details) VALUES (?, ?)",
        ("PATIENT_DISCHARGE", f"Discharged patient ID {patient_id} ({patient['name']})")
    )
    conn.commit()
    conn.close()
    return True, f"Patient {patient['name']} discharged successfully"


def get_active_patients():
    """Return all patients who have not yet been discharged, with their bed info."""
    conn = get_db()
    rows = conn.execute(
        """SELECT p.*, b.bed_number, b.ward
           FROM patients p
           LEFT JOIN beds b ON b.patient_id = p.id
           WHERE p.discharged_at IS NULL
           ORDER BY p.admitted_at DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_patient_stats():
    """Return aggregate counts used by the dashboard."""
    conn = get_db()
    total  = conn.execute("SELECT COUNT(*) FROM patients WHERE discharged_at IS NULL").fetchone()[0]
    urgent = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE discharged_at IS NULL AND priority IN ('urgent','critical')"
    ).fetchone()[0]
    today  = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE DATE(admitted_at)=DATE('now')"
    ).fetchone()[0]
    conn.close()
    return {"total_active": total, "urgent": urgent, "admitted_today": today}
