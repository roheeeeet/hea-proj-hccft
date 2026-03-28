"""
alerts.py
Checks hospital state and returns a list of active alerts.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from db import get_db


def check_alerts():
    conn = get_db()
    alerts = []

    # ── Overall occupancy ──────────────────────────────────────────
    row = conn.execute(
        "SELECT COUNT(*) AS total, SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) AS occ FROM beds"
    ).fetchone()
    if row and row['total'] > 0:
        pct = (row['occ'] / row['total']) * 100
        if pct >= 95:
            alerts.append({"level": "critical", "message": f"Hospital at {pct:.0f}% capacity — CRITICAL overload"})
        elif pct >= 80:
            alerts.append({"level": "warning",  "message": f"Hospital at {pct:.0f}% capacity — high demand"})

    # ── ICU specifically ───────────────────────────────────────────
    icu = conn.execute(
        "SELECT COUNT(*) AS total, SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) AS occ FROM beds WHERE ward='ICU'"
    ).fetchone()
    if icu and icu['total'] > 0:
        icu_avail = icu['total'] - (icu['occ'] or 0)
        icu_pct   = ((icu['occ'] or 0) / icu['total']) * 100
        if icu_avail <= 1:
            alerts.append({"level": "critical", "message": f"ICU: only {icu_avail} bed(s) left!"})
        elif icu_pct >= 80:
            alerts.append({"level": "warning",  "message": f"ICU at {icu_pct:.0f}% — consider transfers"})

    # ── Emergency ward ─────────────────────────────────────────────
    er = conn.execute(
        "SELECT COUNT(*) AS total, SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) AS occ FROM beds WHERE ward='Emergency'"
    ).fetchone()
    if er and er['total'] > 0:
        er_pct = ((er['occ'] or 0) / er['total']) * 100
        if er_pct >= 90:
            alerts.append({"level": "critical", "message": f"Emergency ward at {er_pct:.0f}%!"})

    # ── Resources ──────────────────────────────────────────────────
    resources = conn.execute("SELECT * FROM resources").fetchall()
    for r in resources:
        if r['total'] > 0:
            avail_pct = (r['available'] / r['total']) * 100
            if avail_pct <= 10:
                alerts.append({"level": "critical", "message": f"{r['name']}: only {r['available']} left (critical)"})
            elif avail_pct <= 25:
                alerts.append({"level": "warning",  "message": f"{r['name']}: low stock ({r['available']} available)"})

    conn.close()
    return alerts
