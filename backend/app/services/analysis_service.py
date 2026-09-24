import os
from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.schemas.ai_contract import (
    AnalysisInput, InspectionContext, ElementContext, ObservationContext, 
    CVOutputContext, CVModelMetadata
)
from app.services.ml_service import MLService
from app.services.workflow_runner import run_analysis
from app.core.exceptions import CivilCortexError
from app.core.logger import logger
from app.services.storage_service import storage_service
import tempfile
import bleach

class AnalysisService:
    @staticmethod
    def run_analysis_pipeline(analysis: Analysis, db: Session):
        logger.info(f"event=analysis_stage stage=CV status=started")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            temp_path = tmp_file.name
            
        try:
            # 1. Download image from MinIO
            storage_service.download_file(analysis.original_image_key, temp_path)
            
            # 2. Run Computer Vision Inference
            cv_result = MLService.analyze_image(temp_path)
            
            with open(temp_path, "rb") as f:
                image_bytes = f.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        # 3. Retrieve RAG Evidence
        logger.info(f"event=analysis_stage stage=RAG status=started")
        from app.services.rag_service import rag_service
        defect_type = cv_result["defect_type"]
        
        search_query = defect_type if defect_type in ["Unknown", "none"] else f"Standards, repair guidelines, and safety assessment for {defect_type}."
        rag_evidence = rag_service.retrieve_evidence(search_query)
        
        # 4. Construct AI Context (Simplified)
        input_data = AnalysisInput(
            inspection=InspectionContext(
                inspection_id=analysis.id,
                title=analysis.title
            ),
            element=ElementContext(
                element_id="generic",
                element_type="Generic Structure",
                building_type="Generic",
                is_load_bearing=True
            ),
            observation=ObservationContext(
                crack_type=cv_result["defect_type"],
                delay_risk="unknown"
            ),
            cv_output=CVOutputContext(
                defect_type=cv_result["defect_type"],
                confidence=cv_result["confidence"],
                mask_coverage=cv_result.get("mask_coverage"),
                component_count=cv_result.get("component_count"),
                largest_component_area=cv_result.get("largest_component_area"),
                metadata=CVModelMetadata(
                    model_name=cv_result["model_name"],
                    model_version=cv_result["model_version"],
                    model_status=cv_result["model_status"]
                )
            ),
            image_bytes=image_bytes,
            rag_evidence=rag_evidence
        )
        
        # 5. Run LangGraph LLM Agent with DEMO FAIL-SAFE
        logger.info(f"event=analysis_stage stage=LLM status=started")
        try:
            ai_result = run_analysis(input_data)
            
            # 6. Save results back to DB
            logger.info(f"event=analysis_stage stage=PERSISTENCE status=started")
            report_lines = []
            if ai_result.defect_detected:
                report_lines.append(f"### Detected Defect: {cv_result['defect_type']}")
                report_lines.append(f"**Confidence:** {cv_result['confidence']:.2f}")
                report_lines.append(f"**Severity:** {ai_result.severity or 'Unknown'}")
                report_lines.append(f"**Risk Level:** {ai_result.risk_level or 'Unknown'}")
                
                if cv_result.get("length_mm"):
                    report_lines.append("\n### Physical Measurements (Geometric Analysis)")
                    report_lines.append(f"- **True Geodesic Length:** {cv_result['length_mm']} mm")
                    report_lines.append(f"- **Minimum Width:** {cv_result['min_width_mm']} mm")
                    report_lines.append(f"- **Average Width:** {cv_result['avg_width_mm']} mm")
                    report_lines.append(f"- **Maximum Width:** {cv_result['max_width_mm']} mm")
                    report_lines.append(f"\n*Scale Calibration:* {cv_result.get('calibration_method')}")
                    report_lines.append(f"\n*Note: Depth estimation is currently disabled pending RGB-D sensor integration.*")
                
                if ai_result.recommendation:
                    safe_rec = bleach.clean(ai_result.recommendation)
                    report_lines.append("\n### Repair Recommendation\n" + safe_rec)
                    
                if ai_result.rag_evidence:
                    report_lines.append("\n### Reference Standards\n")
                    for ev in ai_result.rag_evidence:
                        report_lines.append(f"- **{ev.source}**: {ev.text}")
            else:
                report_lines.append("No defects detected in this image. The structure appears healthy.")
                
            analysis.report_text = "\n".join(report_lines)
            
            # Try to map severity string to a float score out of 10
            severity_map = {"CRITICAL": 9.5, "HIGH": 7.5, "MEDIUM": 5.0, "LOW": 2.5}
            analysis.severity_score = severity_map.get(str(ai_result.severity).upper(), 0.0) if ai_result.defect_detected else 0.0
            
        except Exception as e:
            logger.error(f"Gemini API / LangGraph failed: {e}. Executing fail-safe offline mode.")
            # --- FAIL-SAFE OFFLINE DETERMINISTIC REPORT ---
            report_lines = []
            report_lines.append(f"### Detected Defect: {cv_result['defect_type']}")
            report_lines.append(f"**Confidence:** {cv_result['confidence']:.2f}")
            report_lines.append(f"**Severity:** HIGH (Offline Estimate)")
            report_lines.append(f"**Risk Level:** ACTION_REQUIRED")
            
            report_lines.append("\n### Engineering Recommendation (Offline Mode)\n")
            report_lines.append(f"The Computer Vision model detected {cv_result['defect_type']} with {cv_result['confidence']*100:.1f}% confidence, covering {cv_result['mask_coverage']*100:.1f}% of the visible surface.")
            report_lines.append("Due to a network interruption, the LLM synthesis is currently running in **Offline Fail-Safe Mode**.")
            report_lines.append("\n**Standard Repair Protocol:**")
            report_lines.append("1. **Surface Analysis:** 2D Computer Vision confirms surface degradation. However, optical sensors cannot determine internal structural depth.")
            report_lines.append("2. **NDT Assessment Required:** Deploy Non-Destructive Testing (NDT) such as Ultrasonic Pulse Velocity (UPV) or Ground Penetrating Radar (GPR) to assess deep crack propagation.")
            report_lines.append("3. **Intervention:** If crack depth exceeds structural reinforcement cover, inject epoxy resin (ACI 224.1R).")
            
            analysis.report_text = "\n".join(report_lines)
            analysis.severity_score = 7.5
