import os
from datetime import datetime, timezone
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def sanitize_text(text: str) -> str:
    """Sanitizes text for safe DOCX output."""
    if not text:
        return ""
    text = text.replace("₹", "INR ").replace("–", "-").replace("—", "-")
    return text

def generate_inspection_docx(inspection):
    """
    Takes an Inspection SQLAlchemy model and generates a DOCX bytes object.
    """
    doc = Document()
    
    # Header
    title = doc.add_heading("CIVILCORTEX ENGINEERING REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_paragraph("Structural Health Assessment & Remediation Strategy")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    assessment = None
    observation = None
    if inspection.observations:
        observation = inspection.observations[0]
        assessment = observation.assessment

    # 1. Inspection Overview
    doc.add_heading("1. Inspection Overview", level=1)
    
    crack_type = observation.defect.defect_type if observation and observation.defect else 'Unknown'
    severity = assessment.severity if assessment else 'Unknown'
    
    p1 = doc.add_paragraph()
    p1.add_run(f"Inspection Record ID: #{inspection.id}\n")
    p1.add_run(f"Timestamp: {inspection.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    building_name = inspection.building.name if hasattr(inspection, 'building') else 'Building'
    p1.add_run(f"Target Structure: {str(building_name).capitalize()}\n")
    p1.add_run(f"Identified Defect: {crack_type}\n")
    p1.add_run(f"Visual Severity: {str(severity).upper()}")

    # 2. Key Telemetry & Diagnostic Metrics
    doc.add_heading("2. Key Telemetry & Diagnostic Metrics", level=1)
    
    risk_score = assessment.risk_score if assessment and assessment.risk_score else "N/A"
    risk_lvl = assessment.risk if assessment and assessment.risk else "N/A"
    priority = assessment.priority if assessment and assessment.priority else "N/A"
    
    p2 = doc.add_paragraph()
    p2.add_run(f"Risk Assessment Score: {risk_score}/100\n")
    p2.add_run(f"Risk Level: {str(risk_lvl).upper().replace('_', ' ')}\n")
    p2.add_run(f"Intervention Priority: {priority}")

    # 3. Official Remediation Strategy & Action Plan
    doc.add_heading("3. Official Remediation Strategy & Recommendation", level=1)
    
    recommendation_text = assessment.llm_report if assessment and assessment.llm_report else (assessment.repair_recommendation if assessment and assessment.repair_recommendation else "Not available")
    cleaned_rec = recommendation_text.replace("### ", "").replace("## ", "").replace("**", "")
    
    doc.add_paragraph(sanitize_text(cleaned_rec))
    
    # 4. Standards Citations
    rag_context = assessment.rag_context if assessment and assessment.rag_context else "Not available"
    if rag_context and rag_context != "Not available":
        doc.add_heading("4. Regulatory Standards & Compliance References:", level=1)
        doc.add_paragraph(sanitize_text(rag_context))

    # Signature Block
    doc.add_paragraph("\n\n")
    sig = doc.add_paragraph("___________________________________\nLead Structural Engineer Signature\n")
    sig.add_run(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    import io
    file_stream = io.BytesIO()
    doc.save(file_stream)
    return file_stream.getvalue()
