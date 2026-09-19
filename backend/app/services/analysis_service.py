import os
from sqlalchemy.orm import Session
from app.models import InspectionImage, Inspection, Building, AnalysisJob, CrackObservation, Assessment, Defect
from app.schemas.ai_contract import (
    AnalysisInput, InspectionContext, ElementContext, ObservationContext, 
    CVOutputContext, CVModelMetadata
)
from app.services.ml_service import MLService
from app.services.workflow_runner import run_analysis
from app.core.exceptions import AuthorizationError
from app.core.logger import logger
from datetime import datetime

class AnalysisService:
    @staticmethod
    def run_synchronous_analysis(image_id: str, inspection_id: str, db: Session, user_id: str):
        # 1. Load context
        image = db.query(InspectionImage).join(Inspection).filter(
            InspectionImage.id == image_id,
            Inspection.id == inspection_id,
            Inspection.inspector_id == user_id
        ).first()
        
        if not image:
            raise AuthorizationError("Image not found or access denied")
            
        inspection = image.inspection
        building = db.query(Building).filter(Building.id == inspection.building_id).first()
        
        # Resolve the structural element linked to this inspection.
        # Prior to this fix, element context was hardcoded ("Concrete Structure", "Commercial", etc.)
        # Now we look up the actual element from the DB using the ID stored on the inspection record.
        structural_element = None
        if inspection.structural_element_id:
            from app.models import StructuralElement
            structural_element = db.query(StructuralElement).filter(
                StructuralElement.id == inspection.structural_element_id
            ).first()

        element_context = ElementContext(
            element_id=str(structural_element.id) if structural_element else str(image.id),
            element_type=structural_element.element_type if structural_element else "Unknown Element",
            building_type=building.building_type if building and hasattr(building, 'building_type') else None,
            is_load_bearing=structural_element.is_load_bearing if structural_element and hasattr(structural_element, 'is_load_bearing') else True
        )
        
        # Ensure we have an AnalysisJob to track this
        job = db.query(AnalysisJob).filter(AnalysisJob.image_id == image.id).first()
        if not job:
            job = AnalysisJob(image_id=image.id, status="PROCESSING", started_at=datetime.utcnow())
            db.add(job)
        else:
            job.status = "PROCESSING"
            job.started_at = datetime.utcnow()
        db.commit()

        # We will not catch exceptions here and set job.status = FAILED.
        # The worker or route calling this should handle CivilCortexError and mark the job.
        
        # 2. CV Inference
        logger.info(f"event=analysis_stage stage=CV status=started")
        from app.services.storage_service import storage_service
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            temp_path = tmp_file.name
            
        try:
            # Download image from StorageService to temp file
            storage_service.download_file(image.object_key, temp_path)
            
            # MLService.analyze_image returns CVAnalysisResult
            cv_result = MLService.analyze_image(temp_path)
            
            # Read image bytes for LangGraph to use in Gemini step
            with open(temp_path, "rb") as f:
                image_bytes = f.read()
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
        # 3. Retrieve RAG Evidence
        logger.info(f"event=analysis_stage stage=RAG status=started")
        from app.services.rag_service import rag_service
        rag_evidence = rag_service.retrieve_evidence(cv_result["defect_type"])
        
        # 4. Construct AnalysisInput
        input_data = AnalysisInput(
            inspection=InspectionContext(
                inspection_id=str(inspection.id),
                title=f"Inspection for {building.name if building else 'Unknown Building'}"
            ),
            element=element_context,
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
        
        # 5. Invoke LangGraph via workflow_runner
        logger.info(f"event=analysis_stage stage=LLM status=started")
        ai_result = run_analysis(input_data)
        
        # 6. Persist Results
        logger.info(f"event=analysis_stage stage=PERSISTENCE status=started")
        
        # Update AnalysisJob
        job.status = "COMPLETED"
        job.completed_at = datetime.utcnow()
        
        # Persist Defect/Assessment if defect detected
        if ai_result.defect_detected:
            # Create a Defect with structural_element_id=None (allowed by our new migration)
            defect = Defect(
                structural_element_id=None,
                defect_type=cv_result["defect_type"],
                status="CANDIDATE"
            )
            db.add(defect)
            db.flush() # To get defect.id
            
            observation = CrackObservation(
                defect_id=defect.id,
                inspection_id=inspection.id,
                image_id=image.id
            )
            db.add(observation)
            db.flush() # To get observation.id
            
            # Use the first piece of RAG evidence if available, or just join them
            rag_context_text = None
            if ai_result.rag_evidence:
                rag_context_text = "\n\n".join([f"Source: {ev.source}\n{ev.text}" for ev in ai_result.rag_evidence])
            
            assessment = Assessment(
                observation_id=observation.id,
                severity=ai_result.severity if ai_result.severity else "UNKNOWN",
                risk=ai_result.risk_level if ai_result.risk_level else "REQUIRES_REVIEW",
                priority=ai_result.priority,
                rag_context=rag_context_text,
                repair_recommendation=ai_result.recommendation
            )
            db.add(assessment)
            
        db.commit()
        
        # Return result mapped back to a dict for the API response, or the Pydantic model directly
        return ai_result.model_dump()
