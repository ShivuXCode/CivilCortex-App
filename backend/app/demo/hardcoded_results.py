"""
CivilCortex - Temporary Hardcoded Demo Mode Mapping
Provides exact, deterministic inspection payloads keyed by filename.
Includes: 1.jpg, 7001-21.jpg, 7001-115.jpg, 7001-10.jpg, 7001-1.jpg, 7001-17.jpg
All monetary costs formatted in Indian Rupees (₹).
"""

import os
from typing import Dict, Any, Optional

HARDCODED_DEMO_RESULTS: Dict[str, Dict[str, Any]] = {
    # 1. Base 1.jpg demo
    "1.jpg": {
        "crack_type": "Structural Crack",
        "severity": "medium",
        "crack_probability": 0.94,
        "crack_detected": True,
        "health_score": 0,
        "condition": "Critical",
        "risk_score": 68.0,
        "risk_level": "High",
        "priority": "Routine (Monitor)",
        "days": 30,
        "maintenance_action": (
            "Conduct detailed structural inspection of the affected region and evaluate the crack for load-bearing distress. "
            "For confirmed structural cracking, perform appropriate epoxy injection / structural repair based on engineering inspection."
        ),
        "required_workers": 3,
        "required_materials": [
            "Epoxy Injection Resin",
            "Injection Packers",
            "Surface Repair Mortar",
            "Wire Brushes",
            "Protective Equipment"
        ],
        "estimated_cost": "₹10,000 – ₹25,000",
        "rag_context": (
            "Source: FHWA_Bridge_Inspection\n"
            "Section: 4.2 STRUCTURAL CRACKING\n\n"
            "Structural cracks indicate potential load-bearing distress. "
            "Cracks wider than 0.05 inches (1.3 mm) in load-bearing substructures must be addressed via epoxy injection "
            "to restore structural integrity. If cracking is accompanied by active settlement, foundation underpinning is mandated.\n\n"
            "4.3 NON-STRUCTURAL CRACKING (SHRINKAGE/TEMPERATURE)\n"
            "Hairline cracks (< 0.01 inches) on bridge decks or retaining walls are typically non-structural. "
            "The standard maintenance action is surface sealing using polyurethane sealant to prevent water ingress and freeze-thaw damage."
        ),
        "recommendation": (
            "### Condition Summary\n"
            "- **Crack Type:** Structural Crack\n"
            "- **Health Score:** 0 / 100\n"
            "- **Condition:** CRITICAL\n"
            "- **Visual Severity:** MEDIUM\n"
            "- **Crack Probability:** 94.0%\n\n"
            "---\n\n"
            "### Regulatory Compliance & Standards Justification\n"
            "**Source:** FHWA_Bridge_Inspection  \n"
            "**Section:** 4.2 STRUCTURAL CRACKING  \n\n"
            "Structural cracks indicate potential load-bearing distress. Cracks wider than 0.05 inches (1.3 mm) in load-bearing substructures must be addressed via epoxy injection to restore structural integrity. If cracking is accompanied by active settlement, foundation underpinning is mandated.\n\n"
            "**Section:** 4.3 NON-STRUCTURAL CRACKING (SHRINKAGE/TEMPERATURE)  \n"
            "Hairline cracks (< 0.01 inches) on bridge decks or retaining walls are typically non-structural. The standard maintenance action is surface sealing using polyurethane sealant to prevent water ingress and freeze-thaw damage.\n\n"
            "---\n\n"
            "### Action Plan & Resource Requirements\n"
            "- **Proposed Action:** Conduct detailed structural inspection of the affected region and evaluate the crack for load-bearing distress. For confirmed structural cracking, perform appropriate epoxy injection / structural repair based on engineering inspection.\n"
            "- **Workforce:** 3 technicians / inspectors\n"
            "- **Estimated Cost:** ₹10,000 – ₹25,000\n"
            "- **Required Materials & Equipment:**\n"
            "  - Epoxy Injection Resin\n"
            "  - Injection Packers\n"
            "  - Surface Repair Mortar\n"
            "  - Wire Brushes\n"
            "  - Protective Equipment\n\n"
            "---\n\n"
            "### Next Steps & Recommendations\n"
            "1. Conduct detailed structural inspection.\n"
            "2. Measure crack width and propagation.\n"
            "3. Verify whether the crack is load-bearing.\n"
            "4. Perform appropriate structural repair.\n"
            "5. Continue monitoring after repair."
        )
    },

    # 2. 7001-21.jpg: Visible linear concrete crack
    "7001-21.jpg": {
        "crack_type": "Visible linear concrete crack — structural significance undetermined from image alone",
        "severity": "medium",
        "crack_probability": 0.78,
        "crack_detected": True,
        "health_score": 65,
        "condition": "Moderate",
        "risk_score": 55.0,
        "risk_level": "Moderate",
        "priority": "Inspection / Monitor",
        "days": 14,
        "maintenance_action": (
            "Perform a close visual inspection of the complete crack. Measure maximum crack width using a crack gauge. "
            "Record crack length and orientation. Check for moisture, efflorescence, rust staining, or exposed reinforcement. "
            "Determine whether the crack is active/moving or dormant. If confirmed non-structural, routing/sealing may be appropriate to limit water intrusion. "
            "If confirmed structural and dormant, an engineer should evaluate whether epoxy injection is appropriate. "
            "If evidence of movement, settlement, reinforcement corrosion, or significant distress is found, escalate for engineering assessment."
        ),
        "required_workers": 3,
        "required_materials": [
            "Crack-width comparator/gauge",
            "Measuring tape",
            "Wire brush",
            "Inspection camera",
            "Appropriate crack sealant or epoxy system (after assessment)",
            "PPE"
        ],
        "estimated_cost": "₹25,000 – ₹1,00,000",
        "rag_context": (
            "Source: FHWA Long-Term Bridge Performance (LTBP) – Concrete Cracking\n\n"
            "FHWA guidance recommends documenting the crack's location, length, orientation, maximum width, depth where possible, "
            "and associated characteristics such as moisture, efflorescence, rust, and exposed reinforcement. "
            "Crack width should be measured using a crack comparator rather than estimated from a photograph.\n\n"
            "For reinforced-concrete bridge elements, FHWA's LTBP protocol specifically records cracks at 0.025 in (0.64 mm) or greater. "
            "Prestressed concrete elements require much more sensitive assessment, with cracks at approximately 0.005 in (0.13 mm) being significant for the inspection protocol.\n\n"
            "The visible crack therefore warrants field measurement and condition assessment before selecting a repair method."
        ),
        "recommendation": (
            "### Condition Summary\n"
            "- **Crack Type:** Visible linear concrete crack — structural significance undetermined from image alone\n"
            "- **Health Score:** 65 / 100\n"
            "- **Overall Risk Level:** Moderate\n"
            "- **Priority:** Inspection / Monitor\n\n"
            "The image shows a clearly visible, continuous, irregular crack running diagonally across the concrete surface. "
            "The crack is substantially more pronounced than a barely perceptible hairline surface mark. However, the image provides "
            "no scale, member identification, or evidence of movement, reinforcement corrosion, or structural displacement, so it should not be classified as a confirmed structural crack solely from the photograph.\n\n"
            "---\n\n"
            "### Regulatory Compliance & Standards Justification\n"
            "**Source:** FHWA Long-Term Bridge Performance (LTBP) – Concrete Cracking  \n\n"
            "FHWA guidance recommends documenting the crack's location, length, orientation, maximum width, depth where possible, and associated characteristics such as moisture, efflorescence, rust, and exposed reinforcement. Crack width should be measured using a crack comparator rather than estimated from a photograph.\n\n"
            "For reinforced-concrete bridge elements, FHWA's LTBP protocol specifically records cracks at 0.025 in (0.64 mm) or greater. Prestressed concrete elements require much more sensitive assessment, with cracks at approximately 0.005 in (0.13 mm) being significant for the inspection protocol.\n\n"
            "The visible crack therefore warrants field measurement and condition assessment before selecting a repair method.\n\n"
            "---\n\n"
            "### Action Plan & Resource Requirements\n"
            "- **Proposed Action:** Perform a close visual inspection of the complete crack. Measure maximum crack width using a crack gauge. Record crack length and orientation. Check for moisture, efflorescence, rust staining, or exposed reinforcement. Determine whether the crack is active/moving or dormant. If confirmed non-structural, routing/sealing may be appropriate. If confirmed structural and dormant, evaluate epoxy injection per FHWA guidelines. If evidence of distress is found, escalate for engineering assessment.\n"
            "- **Workforce:** 2 Workers + Engineering Inspector (3 Staff)\n"
            "- **Estimated Cost:** ₹25,000 – ₹1,00,000\n"
            "- **Required Materials & Equipment:**\n"
            "  - Crack-width comparator/gauge\n"
            "  - Measuring tape\n"
            "  - Wire brush\n"
            "  - Inspection camera\n"
            "  - Appropriate crack sealant or epoxy system\n"
            "  - PPE\n\n"
            "---\n\n"
            "### Next Steps & Recommendations\n"
            "Conduct a field measurement of the crack before assigning a structural rating or repair method. The visible crack is sufficiently pronounced to justify inspection, but the photograph alone does not demonstrate structural failure."
        )
    },

    # 3. 7001-115.jpg: Fine/hairline surface cracking
    "7001-115.jpg": {
        "crack_type": "Fine/hairline surface cracking",
        "severity": "low",
        "crack_probability": 0.62,
        "crack_detected": True,
        "health_score": 85,
        "condition": "Good",
        "risk_score": 25.0,
        "risk_level": "Low",
        "priority": "Routine (Monitor)",
        "days": 30,
        "maintenance_action": (
            "Document the crack location photographically. Measure the maximum width if accessible. "
            "Check whether the crack is increasing in length or width. Inspect for moisture or staining. "
            "If confirmed as a minor, stable, non-structural crack, apply an appropriate surface-sealing treatment where environmental exposure warrants it. "
            "No structural injection should be specified based solely on this photograph."
        ),
        "required_workers": 2,
        "required_materials": [
            "Crack-width gauge",
            "Inspection camera",
            "Wire brush",
            "Appropriate concrete surface sealant",
            "PPE"
        ],
        "estimated_cost": "₹8,000 – ₹32,000",
        "rag_context": (
            "Source: FHWA Long-Term Bridge Performance (LTBP) – Concrete Cracking\n\n"
            "FHWA recognizes that concrete cracking can result from several mechanisms, including shrinkage, structural loading, "
            "reinforcement corrosion, creep, chemical reactions, and external events. Therefore, crack appearance alone is insufficient to establish its cause.\n\n"
            "For minor visible cracking without evidence of associated deterioration, the appropriate first step is documentation and monitoring rather than automatically treating the crack as structural."
        ),
        "recommendation": (
            "### Condition Summary\n"
            "- **Crack Type:** Fine/hairline surface cracking\n"
            "- **Health Score:** 85 / 100\n"
            "- **Overall Risk Level:** Low\n"
            "- **Priority:** Routine (Monitor)\n\n"
            "The image shows a very narrow, short, mostly vertical surface indication. It appears substantially less pronounced than larger structural fissures. No obvious spalling, exposed reinforcement, major displacement, or significant surface deterioration is visible. The crack width cannot be reliably measured from the image alone.\n\n"
            "---\n\n"
            "### Regulatory Compliance & Standards Justification\n"
            "**Source:** FHWA Long-Term Bridge Performance (LTBP) – Concrete Cracking  \n\n"
            "FHWA recognizes that concrete cracking can result from several mechanisms, including shrinkage, structural loading, reinforcement corrosion, creep, chemical reactions, and external events. Therefore, crack appearance alone is insufficient to establish its cause.\n\n"
            "For minor visible cracking without evidence of associated deterioration, the appropriate first step is documentation and monitoring rather than automatically treating the crack as structural.\n\n"
            "---\n\n"
            "### Action Plan & Resource Requirements\n"
            "- **Proposed Action:** Document the crack location photographically. Measure maximum width if accessible. Check whether the crack is increasing in length or width. Inspect for moisture or staining. If confirmed as minor and stable, apply surface sealant where environmental exposure warrants it. No structural injection required.\n"
            "- **Workforce:** 1–2 Workers\n"
            "- **Estimated Cost:** ₹8,000 – ₹32,000\n"
            "- **Required Materials & Equipment:**\n"
            "  - Crack-width gauge\n"
            "  - Inspection camera\n"
            "  - Wire brush\n"
            "  - Appropriate concrete surface sealant\n"
            "  - PPE\n\n"
            "---\n\n"
            "### Next Steps & Recommendations\n"
            "Continue routine monitoring. Reinspect during subsequent maintenance inspections and compare crack width and length with the baseline record."
        )
    },

    # 4. 7001-10.jpg: No clearly identifiable crack / surface texture
    "7001-10.jpg": {
        "crack_type": "No clearly identifiable crack / surface texture",
        "severity": "low",
        "crack_probability": 0.05,
        "crack_detected": False,
        "health_score": 95,
        "condition": "Excellent",
        "risk_score": 5.0,
        "risk_level": "Low",
        "priority": "Routine (No Immediate Action)",
        "days": 90,
        "maintenance_action": (
            "No immediate crack repair recommended. Perform a close-range visual inspection if this location has been flagged by an automated detection system. "
            "Clean the surface if necessary to distinguish dirt/surface texture from actual cracking. Photograph the area again under improved lighting if a suspected defect remains. "
            "If a crack becomes clearly identifiable during inspection, measure and classify it before selecting a repair method."
        ),
        "required_workers": 1,
        "required_materials": [
            "Inspection camera",
            "Cleaning brush",
            "Crack-width gauge (if crack is subsequently identified)",
            "PPE"
        ],
        "estimated_cost": "₹0 – ₹12,000",
        "rag_context": (
            "Source: FHWA Concrete Cracking Inspection Protocol\n\n"
            "FHWA inspection procedures require cracks to be identified and then characterized by measurable properties such as width, length, orientation, and depth where possible.\n\n"
            "Because a definite crack cannot be established from this image, prescribing crack injection or sealing would not be justified."
        ),
        "recommendation": (
            "### Condition Summary\n"
            "- **Crack Type:** No clearly identifiable crack / surface texture\n"
            "- **Health Score:** 95 / 100\n"
            "- **Overall Risk Level:** Low\n"
            "- **Priority:** Routine (No Immediate Action)\n\n"
            "The photograph does not show a clearly defined concrete crack. The visible features appear predominantly consistent with normal surface texture, pores, or minor surface irregularities. There is no clearly discernible continuous crack requiring repair in this image.\n\n"
            "---\n\n"
            "### Regulatory Compliance & Standards Justification\n"
            "**Source:** FHWA Concrete Cracking Inspection Protocol  \n\n"
            "FHWA inspection procedures require cracks to be identified and then characterized by measurable properties such as width, length, orientation, and depth where possible. Because a definite crack cannot be established from this image, prescribing crack injection or sealing would not be justified.\n\n"
            "---\n\n"
            "### Action Plan & Resource Requirements\n"
            "- **Proposed Action:** No immediate crack repair recommended. Perform a close-range visual inspection if flagged. Clean surface if necessary. Re-photograph under improved lighting if suspected defect remains.\n"
            "- **Workforce:** 1 Inspector\n"
            "- **Estimated Cost:** ₹0 – ₹12,000\n"
            "- **Required Materials & Equipment:**\n"
            "  - Inspection camera\n"
            "  - Cleaning brush\n"
            "  - Crack-width gauge\n"
            "  - PPE\n\n"
            "---\n\n"
            "### Next Steps & Recommendations\n"
            "No repair action should be initiated based on this image alone. Verify the suspected defect during close-range inspection."
        )
    },

    # 5. 7001-1.jpg: Very fine surface crack / hairline indication
    "7001-1.jpg": {
        "crack_type": "Very fine surface crack / hairline indication",
        "severity": "low",
        "crack_probability": 0.55,
        "crack_detected": True,
        "health_score": 88,
        "condition": "Good",
        "risk_score": 20.0,
        "risk_level": "Low",
        "priority": "Routine (Monitor)",
        "days": 30,
        "maintenance_action": (
            "Verify the indication using close-range inspection. Clean the surface around the suspected crack. "
            "Measure the maximum opening with a crack comparator. Photograph the area at higher resolution. "
            "Monitor for propagation. If confirmed as a stable non-structural surface crack, use an appropriate sealing treatment where necessary to limit moisture penetration. "
            "Do not specify epoxy injection without confirmation of structural significance and suitability of the crack for injection."
        ),
        "required_workers": 2,
        "required_materials": [
            "Crack-width comparator",
            "Wire brush",
            "Inspection camera",
            "Surface sealant (if required)",
            "PPE"
        ],
        "estimated_cost": "₹8,000 – ₹32,000",
        "rag_context": (
            "Source: FHWA Long-Term Bridge Performance (LTBP) – Concrete Cracking\n\n"
            "FHWA emphasizes that crack width should be measured rather than visually estimated and that the inspector should consider crack characteristics and associated conditions when determining significance.\n\n"
            "The image does not provide enough information to establish whether this is a structural crack or a superficial surface feature."
        ),
        "recommendation": (
            "### Condition Summary\n"
            "- **Crack Type:** Very fine surface crack / hairline indication\n"
            "- **Health Score:** 88 / 100\n"
            "- **Overall Risk Level:** Low\n"
            "- **Priority:** Routine (Monitor)\n\n"
            "A faint, short linear indication is visible toward the left-center portion of the image. It is difficult to distinguish confidently from surface texture because of the low contrast and image resolution. No visible spalling, exposed reinforcement, or major displacement is apparent.\n\n"
            "---\n\n"
            "### Regulatory Compliance & Standards Justification\n"
            "**Source:** FHWA Long-Term Bridge Performance (LTBP) – Concrete Cracking  \n\n"
            "FHWA emphasizes that crack width should be measured rather than visually estimated and that the inspector should consider crack characteristics and associated conditions when determining significance. The image does not provide enough information to establish whether this is a structural crack or a superficial surface feature.\n\n"
            "---\n\n"
            "### Action Plan & Resource Requirements\n"
            "- **Proposed Action:** Verify the indication using close-range inspection. Clean surface around suspected crack. Measure maximum opening with crack comparator. Photograph at higher resolution. Monitor for propagation. If confirmed as stable non-structural surface crack, apply surface sealant.\n"
            "- **Workforce:** 1–2 Workers\n"
            "- **Estimated Cost:** ₹8,000 – ₹32,000\n"
            "- **Required Materials & Equipment:**\n"
            "  - Crack-width comparator\n"
            "  - Wire brush\n"
            "  - Inspection camera\n"
            "  - Surface sealant\n"
            "  - PPE\n\n"
            "---\n\n"
            "### Next Steps & Recommendations\n"
            "Treat this as a low-severity observation requiring verification, rather than immediately classifying it as a structural defect."
        )
    },

    # 6. 7001-17.jpg: Irregular cracking with localized surface deterioration
    "7001-17.jpg": {
        "crack_type": "Irregular cracking with localized surface deterioration / possible void or aggregate-related defect",
        "severity": "medium",
        "crack_probability": 0.72,
        "crack_detected": True,
        "health_score": 70,
        "condition": "Fair",
        "risk_score": 50.0,
        "risk_level": "Moderate",
        "priority": "Inspection / Maintenance",
        "days": 14,
        "maintenance_action": (
            "Perform close-range inspection of the entire affected area. Determine whether the dark areas are voids, exposed aggregate, staining, or reinforcement-related deterioration. "
            "Remove any loose or unsound concrete if deterioration is confirmed. Check for exposed or corroding reinforcement. "
            "Measure any identifiable crack width and depth. If the crack is non-structural, consider appropriate routing/sealing. "
            "If the crack is confirmed to be a dormant structural crack, obtain engineering review before epoxy injection. "
            "If reinforcement corrosion is present, repair should address the corrosion mechanism rather than simply filling the crack."
        ),
        "required_workers": 3,
        "required_materials": [
            "Crack-width gauge",
            "Wire brushes",
            "Small hammer/chipping tools for soundness assessment",
            "Inspection camera",
            "Concrete repair mortar",
            "Appropriate crack sealant/epoxy",
            "PPE"
        ],
        "estimated_cost": "₹25,000 – ₹1,25,000",
        "rag_context": (
            "Source: FHWA Bridge Inspection / Concrete Deterioration Guidance\n\n"
            "FHWA notes that concrete surface deterioration can provide pathways for moisture and oxygen to reach the interior of concrete, potentially accelerating deterioration.\n\n"
            "FHWA inspection guidance also recommends considering characteristics such as crack width, spacing, location, orientation, moisture, efflorescence, rust, and exposed reinforcement when evaluating concrete cracking.\n\n"
            "If the apparent voids are confirmed as spalling or concrete loss, the repair approach should address loose/deteriorated concrete before surface treatment."
        ),
        "recommendation": (
            "### Condition Summary\n"
            "- **Crack Type:** Irregular cracking with localized surface deterioration / possible void or aggregate-related defect\n"
            "- **Health Score:** 70 / 100\n"
            "- **Overall Risk Level:** Moderate\n"
            "- **Priority:** Inspection / Maintenance\n\n"
            "The image shows an irregular dark crack-like feature together with several localized dark/void-like areas and an uneven concrete surface. The condition is more visually complex than a simple isolated hairline crack. However, the image resolution and absence of scale make it impossible to determine whether the dark areas represent actual voids, exposed aggregate, surface damage, staining, or markings.\n\n"
            "---\n\n"
            "### Regulatory Compliance & Standards Justification\n"
            "**Source:** FHWA Bridge Inspection / Concrete Deterioration Guidance  \n\n"
            "FHWA notes that concrete surface deterioration can provide pathways for moisture and oxygen to reach the interior of concrete, potentially accelerating deterioration. FHWA inspection guidance also recommends considering characteristics such as crack width, spacing, location, orientation, moisture, efflorescence, rust, and exposed reinforcement when evaluating concrete cracking.\n\n"
            "If the apparent voids are confirmed as spalling or concrete loss, the repair approach should address loose/deteriorated concrete before surface treatment.\n\n"
            "---\n\n"
            "### Action Plan & Resource Requirements\n"
            "- **Proposed Action:** Perform close-range inspection of the entire affected area. Determine whether the dark areas are voids, exposed aggregate, staining, or reinforcement deterioration. Remove loose or unsound concrete. Check for exposed/corroding rebar. Measure crack width/depth. Apply routing/sealing if non-structural, or obtain engineering review for epoxy injection if dormant structural crack.\n"
            "- **Workforce:** 2 Workers + Inspector (3 Staff)\n"
            "- **Estimated Cost:** ₹25,000 – ₹1,25,000\n"
            "- **Required Materials & Equipment:**\n"
            "  - Crack-width gauge\n"
            "  - Wire brushes\n"
            "  - Small hammer/chipping tools\n"
            "  - Inspection camera\n"
            "  - Concrete repair mortar\n"
            "  - Appropriate crack sealant/epoxy\n"
            "  - PPE\n\n"
            "---\n\n"
            "### Next Steps & Recommendations\n"
            "Perform a detailed inspection before repair selection. The combination of irregular cracking and apparent localized surface deterioration makes this image more deserving of follow-up than a simple hairline crack."
        )
    }
}

# Add .jpeg aliases for all entries
for base_key in list(HARDCODED_DEMO_RESULTS.keys()):
    if base_key.endswith(".jpg"):
        jpeg_key = base_key[:-4] + ".jpeg"
        HARDCODED_DEMO_RESULTS[jpeg_key] = HARDCODED_DEMO_RESULTS[base_key]

def get_hardcoded_demo_result(filename: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Checks if a filename matches a configured hardcoded demo result.
    Normalizes filename safely using basename and lowercase.
    """
    if not filename:
        return None
    normalized_name = os.path.basename(filename).strip().lower()
    return HARDCODED_DEMO_RESULTS.get(normalized_name)
