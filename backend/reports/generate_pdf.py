"""
reports/generate_pdf.py
Generates a PDF hospital status report using ReportLab.
"""
import os, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from db import get_db

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'database')


def generate_report():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    output_path = os.path.join(OUTPUT_DIR, 'HEA_Report.pdf')
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    BLUE   = colors.HexColor('#1a4480')
    GREEN  = colors.HexColor('#2e7d32')
    RED    = colors.HexColor('#c62828')

    title_style = ParagraphStyle('Title2', parent=styles['Title'],
                                  textColor=BLUE, fontSize=20, spaceAfter=6)
    h2_style    = ParagraphStyle('H2', parent=styles['Heading2'],
                                  textColor=BLUE, fontSize=13, spaceBefore=14, spaceAfter=6)
    body_style  = styles['Normal']

    conn = get_db()

    # ── Data ──────────────────────────────────────────────────────
    beds     = conn.execute("SELECT * FROM beds ORDER BY ward, bed_number").fetchall()
    patients = conn.execute(
        "SELECT * FROM patients WHERE discharged_at IS NULL ORDER BY admitted_at DESC LIMIT 30"
    ).fetchall()
    resources = conn.execute("SELECT * FROM resources").fetchall()
    audit    = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20"
    ).fetchall()
    conn.close()

    total_beds  = len(beds)
    occupied    = sum(1 for b in beds if b['status'] == 'occupied')
    available   = sum(1 for b in beds if b['status'] == 'available')
    maintenance = sum(1 for b in beds if b['status'] == 'maintenance')
    occ_pct     = round((occupied / total_beds) * 100) if total_beds else 0

    story = []

    # Title
    story.append(Paragraph("HEA — Hospital Emergency Allocation", title_style))
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
                            ParagraphStyle('Sub', parent=body_style, textColor=colors.grey, fontSize=9)))
    story.append(Spacer(1, 16))

    # Summary
    story.append(Paragraph("Summary", h2_style))
    summary_data = [
        ["Metric", "Value"],
        ["Total Beds", str(total_beds)],
        ["Occupied", str(occupied)],
        ["Available", str(available)],
        ["Under Maintenance", str(maintenance)],
        ["Occupancy Rate", f"{occ_pct}%"],
        ["Active Patients", str(len(patients))],
    ]
    t = Table(summary_data, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), BLUE),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor('#e0e0e0')),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('PADDING',     (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # Ward occupancy
    story.append(Paragraph("Bed Occupancy by Ward", h2_style))
    ward_data = [["Ward", "Total", "Occupied", "Available", "Occupancy %"]]
    wards = {}
    for b in beds:
        w = b['ward']
        if w not in wards:
            wards[w] = {"total": 0, "occupied": 0, "available": 0}
        wards[w]["total"] += 1
        wards[w][b['status']] = wards[w].get(b['status'], 0) + 1
    for w, d in sorted(wards.items()):
        pct = round((d.get('occupied', 0) / d['total']) * 100)
        ward_data.append([w, d['total'], d.get('occupied', 0), d.get('available', 0), f"{pct}%"])
    wt = Table(ward_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    wt.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), BLUE),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor('#e0e0e0')),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('PADDING',     (0,0), (-1,-1), 6),
    ]))
    story.append(wt)
    story.append(Spacer(1, 14))

    # Resources
    story.append(Paragraph("Resource Availability", h2_style))
    res_data = [["Resource", "Category", "Total", "Available", "In Use"]]
    for r in resources:
        in_use = r['total'] - r['available']
        res_data.append([r['name'], r['category'].title(), r['total'], r['available'], in_use])
    rt = Table(res_data, colWidths=[5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    rt.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), BLUE),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor('#e0e0e0')),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('PADDING',     (0,0), (-1,-1), 6),
    ]))
    story.append(rt)
    story.append(Spacer(1, 14))

    # Recent audit log
    story.append(Paragraph("Recent Activity (last 20 entries)", h2_style))
    audit_data = [["Timestamp", "Action", "Details"]]
    for a in audit:
        ts = a['timestamp'][:16] if a['timestamp'] else ''
        audit_data.append([ts, a['action'], a['details'] or ''])
    at = Table(audit_data, colWidths=[4*cm, 4.5*cm, 7.5*cm])
    at.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), BLUE),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor('#e0e0e0')),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('PADDING',     (0,0), (-1,-1), 5),
        ('WORDWRAP',    (2,1), (2,-1), True),
    ]))
    story.append(at)

    doc.build(story)
    return output_path
