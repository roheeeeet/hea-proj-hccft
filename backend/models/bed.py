"""
models/bed.py
Functions for bed allocation, release, and occupancy reporting.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from db import get_db


def get_all_beds():
    conn = get_db()
    rows = conn.execute("SELECT * FROM beds ORDER BY ward, bed_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_bed_summary():
    """Return per-ward occupancy breakdown."""
    conn = get_db()
    rows = conn.execute(
        """SELECT ward,
                  COUNT(*) AS total,
                  SUM(CASE WHEN status='available'   THEN 1 ELSE 0 END) AS available,
                  SUM(CASE WHEN status='occupied'    THEN 1 ELSE 0 END) AS occupied,
                  SUM(CASE WHEN status='maintenance' THEN 1 ELSE 0 END) AS maintenance
           FROM beds GROUP BY ward ORDER BY ward"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def allocate_bed(patient_id, preferred_ward=None):
    """Find the first available bed (optionally in preferred_ward) and assign it."""
    conn = get_db()

    if preferred_ward:
        bed = conn.execute(
            "SELECT * FROM beds WHERE status='available' AND ward=? ORDER BY id LIMIT 1",
            (preferred_ward,)
        ).fetchone()

    if not preferred_ward or not bed:
        bed = conn.execute(
            "SELECT * FROM beds WHERE status='available' ORDER BY id LIMIT 1"
        ).fetchone()

    if not bed:
        conn.close()
        return None, "No beds available"

    conn.execute(
        "UPDATE beds SET status='occupied', patient_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (patient_id, bed['id'])
    )
    conn.execute(
        "INSERT INTO audit_log (action, details) VALUES (?, ?)",
        ("BED_ALLOCATE", f"Bed {bed['bed_number']} allocated to patient {patient_id}")
    )
    conn.commit()
    result = dict(bed)
    result['status'] = 'occupied'
    result['patient_id'] = patient_id
    conn.close()
    return result, None


def release_bed(bed_id):
    """Free a bed and clear its patient assignment."""
    conn = get_db()
    conn.execute(
        "UPDATE beds SET status='available', patient_id=NULL, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (bed_id,)
    )
    conn.execute(
        "INSERT INTO audit_log (action, details) VALUES (?, ?)",
        ("BED_RELEASE", f"Bed ID {bed_id} released")
    )
    conn.commit()
    conn.close()


def get_occupancy_rate():
    """Return overall occupancy as a percentage (0-100)."""
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) AS total, SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) AS occupied FROM beds"
    ).fetchone()
    conn.close()
    if not row or row['total'] == 0:
        return 0
    return round((row['occupied'] / row['total']) * 100, 1)
