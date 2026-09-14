# CivilCortex Annotation Standard Operating Procedure (SOP)

## 1. Image Screening
- **Quality Check:** Reject images that are excessively blurry, unreadable, or corrupted.
- **Privacy Check:** Reject images containing PII (faces, license plates, documents).

## 2. Defect Identification & Instance Separation
- **Identification:** Annotator identifies visible structural defects.
- **Instance Rule:** ONE physical visible defect = ONE annotated instance. If a crack branches continuously, it is one instance. Disconnected physical cracks are separate instances.

## 3. Mask / Polygon Creation
- Trace polygons tightly (≤ 3 pixels) around the true physical boundary of the defect.
- **Thin Crack Policy:** Do NOT artificially dilate, thicken, or hallucinate boundaries for very thin cracks. Annotate only the actual visible evidence without adding healthy concrete. 
- **Ambiguity:** Distinguish between a genuine thin crack, discoloration, and image noise. Do not automatically classify faint lines as cracks.

## 4. Morphology Tagging
- Select all applicable morphology tags (`horizontal`, `vertical`, `diagonal`, `branching`, `irregular`) for the traced polygon.
- Do NOT create separate/overlapping polygons just to accommodate multiple morphology characteristics.

## 5. Occlusion Handling
- If a defect is interrupted by a foreground occlusion (e.g., pipe, wire), trace the visible segments as separate polygons, but link them semantically if the tooling permits, or leave them as independent visual instances.

## 6. Uncertainty and Fabrication
- Annotators must NEVER fabricate a defect boundary or hallucinate an engineering interpretation (e.g., assigning a shear failure mechanism).
- If evidence is insufficient, mark the instance as `uncertain` or reject the image.

## 7. Review and QC
- **Peer Review:** 20% of annotations will undergo peer review.
- **Disputes:** Disagreements regarding defect boundaries or classifications must be escalated to a senior annotator/structural engineer. Do not resolve disputes arbitrarily.
