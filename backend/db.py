import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'hea.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Beds table
    c.execute('''CREATE TABLE IF NOT EXISTS beds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_number TEXT NOT NULL UNIQUE,
        ward TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'available',
        patient_id INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Patients table
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        condition TEXT,
        priority TEXT DEFAULT 'normal',
        admitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        discharged_at TIMESTAMP,
        bed_id INTEGER
    )''')

    # Resources table (ventilators, OT rooms, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        total INTEGER DEFAULT 0,
        available INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Audit log table
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT,
        performed_by TEXT DEFAULT 'system',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Staff table
    c.execute('''CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        ward TEXT,
        shift TEXT,
        on_duty INTEGER DEFAULT 1
    )''')

    conn.commit()

    # Seed initial data if empty
    _seed_data(conn)
    conn.close()

def _seed_data(conn):
    c = conn.cursor()

    # Seed beds (only if empty)
    c.execute("SELECT COUNT(*) FROM beds")
    if c.fetchone()[0] == 0:
        wards = [
            ("General", "general", 20),
            ("ICU", "icu", 8),
            ("Emergency", "emergency", 10),
            ("Pediatric", "pediatric", 12),
            ("Maternity", "maternity", 8),
        ]
        for ward_name, ward_code, count in wards:
            for i in range(1, count + 1):
                bed_num = f"{ward_code.upper()}-{i:03d}"
                # Make some occupied for demo
                status = "occupied" if i % 3 == 0 else "available"
                c.execute(
                    "INSERT INTO beds (bed_number, ward, type, status) VALUES (?, ?, ?, ?)",
                    (bed_num, ward_name, ward_code, status)
                )

    # Seed resources
    c.execute("SELECT COUNT(*) FROM resources")
    if c.fetchone()[0] == 0:
        resources = [
            ("Ventilators", "equipment", 20, 14),
            ("OT Rooms", "facility", 6, 4),
            ("ICU Monitors", "equipment", 15, 9),
            ("Wheelchairs", "equipment", 30, 22),
            ("Oxygen Cylinders", "supply", 50, 38),
        ]
        for name, cat, total, avail in resources:
            c.execute(
                "INSERT INTO resources (name, category, total, available) VALUES (?, ?, ?, ?)",
                (name, cat, total, avail)
            )

    # Seed staff
    c.execute("SELECT COUNT(*) FROM staff")
    if c.fetchone()[0] == 0:
        staff = [
            ("Dr. Priya Sharma", "Doctor", "ICU", "Morning"),
            ("Dr. Rahul Verma", "Doctor", "Emergency", "Morning"),
            ("Nurse Meena Rao", "Nurse", "General", "Morning"),
            ("Nurse Suresh Kumar", "Nurse", "ICU", "Night"),
            ("Dr. Anjali Singh", "Doctor", "Pediatric", "Afternoon"),
        ]
        for name, role, ward, shift in staff:
            c.execute(
                "INSERT INTO staff (name, role, ward, shift) VALUES (?, ?, ?, ?)",
                (name, role, ward, shift)
            )

    conn.commit()
