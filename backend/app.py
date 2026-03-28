"""
HEA — Hospital Emergency Allocation
Main Flask application

Run with: python app.py
API runs on http://localhost:5000
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from db import init_db, get_db
from models.bed import get_all_beds, get_bed_summary, allocate_bed, release_bed, get_occupancy_rate
from models.patient import admit_patient, discharge_patient, get_active_patients, get_patient_stats
from ml.predict import predict_next_72h
from alerts import check_alerts

app = Flask(__name__)
CORS(app)  # Allow frontend to call API from same machine

# ─── HEALTH CHECK ───────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "HEA API running"})

# ─── DASHBOARD SUMMARY ──────────────────────────────────────────
@app.route('/api/dashboard')
def dashboard():
    bed_summary = get_bed_summary()
    patient_stats = get_patient_stats()
    alerts = check_alerts()
    occupancy = get_occupancy_rate()

    conn = get_db()
    resources = [dict(r) for r in conn.execute("SELECT * FROM resources").fetchall()]
    conn.close()

    return jsonify({
        "bed_summary": bed_summary,
        "patient_stats": patient_stats,
        "alerts": alerts,
        "occupancy_rate": occupancy,
        "resources": resources
    })

# ─── BEDS ────────────────────────────────────────────────────────
@app.route('/api/beds')
def beds():
    ward = request.args.get('ward')
    all_beds = get_all_beds()
    if ward:
        all_beds = [b for b in all_beds if b['ward'].lower() == ward.lower()]
    return jsonify(all_beds)

@app.route('/api/beds/summary')
def beds_summary():
    return jsonify(get_bed_summary())

@app.route('/api/beds/allocate', methods=['POST'])
def allocate():
    data = request.get_json()
    patient_id = data.get('patient_id')
    ward = data.get('ward')
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400
    bed, err = allocate_bed(patient_id, ward)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"bed": bed, "message": "Bed allocated successfully"})

@app.route('/api/beds/release', methods=['POST'])
def release():
    data = request.get_json()
    bed_id = data.get('bed_id')
    if not bed_id:
        return jsonify({"error": "bed_id is required"}), 400
    release_bed(bed_id)
    return jsonify({"message": "Bed released"})

@app.route('/api/beds/<int:bed_id>/status', methods=['PUT'])
def update_bed_status(bed_id):
    data = request.get_json()
    status = data.get('status')
    if status not in ['available', 'occupied', 'maintenance']:
        return jsonify({"error": "Invalid status"}), 400
    conn = get_db()
    conn.execute("UPDATE beds SET status=? WHERE id=?", (status, bed_id))
    conn.execute("INSERT INTO audit_log (action, details) VALUES (?, ?)",
                 ("BED_STATUS_CHANGE", f"Bed {bed_id} set to {status}"))
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated"})

# ─── PATIENTS ────────────────────────────────────────────────────
@app.route('/api/patients', methods=['GET'])
def patients():
    return jsonify(get_active_patients())

@app.route('/api/patients/admit', methods=['POST'])
def admit():
    data = request.get_json()
    required = ['name', 'age', 'gender', 'condition']
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    patient_id = admit_patient(
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        condition=data['condition'],
        priority=data.get('priority', 'normal'),
        ward=data.get('ward')
    )
    # Auto-allocate bed
    bed, err = allocate_bed(patient_id, data.get('ward'))
    return jsonify({
        "patient_id": patient_id,
        "bed": bed,
        "message": "Patient admitted" + (" and bed allocated" if bed else " (no bed available)")
    })

@app.route('/api/patients/<int:patient_id>/discharge', methods=['POST'])
def discharge(patient_id):
    ok, msg = discharge_patient(patient_id)
    if not ok:
        return jsonify({"error": msg}), 404
    return jsonify({"message": msg})

# ─── FORECAST ────────────────────────────────────────────────────
@app.route('/api/forecast')
def forecast():
    predictions = predict_next_72h()
    return jsonify(predictions)

# ─── ALERTS ──────────────────────────────────────────────────────
@app.route('/api/alerts')
def alerts():
    return jsonify(check_alerts())

# ─── RESOURCES ───────────────────────────────────────────────────
@app.route('/api/resources')
def resources():
    conn = get_db()
    rows = conn.execute("SELECT * FROM resources").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/resources/<int:res_id>', methods=['PUT'])
def update_resource(res_id):
    data = request.get_json()
    available = data.get('available')
    conn = get_db()
    conn.execute("UPDATE resources SET available=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                 (available, res_id))
    conn.execute("INSERT INTO audit_log (action, details) VALUES (?, ?)",
                 ("RESOURCE_UPDATE", f"Resource {res_id} set available={available}"))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

# ─── REPORTS ─────────────────────────────────────────────────────
@app.route('/api/reports/audit')
def audit_log():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/reports/pdf')
def download_pdf():
    try:
        from reports.generate_pdf import generate_report
        path = generate_report()
        return send_file(path, as_attachment=True, download_name="HEA_Report.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── STAFF ───────────────────────────────────────────────────────
@app.route('/api/staff')
def staff():
    conn = get_db()
    rows = conn.execute("SELECT * FROM staff").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─── STARTUP ─────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Initialising HEA database...")
    init_db()
    print("HEA API running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)