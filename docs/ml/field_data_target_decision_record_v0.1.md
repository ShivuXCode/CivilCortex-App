# Field Data Target Decision Record v0.1

## 1. Decision Status
**APPROVED**

## 2. Problem Statement
The Phase 9 field data collection documentation contained a mathematically irreconcilable contradiction regarding the minimum number of physical defect instances required to open the production ML readiness gate.

## 3. Existing Conflicting Targets
- **Physical-defect total target:** 2,000 total physical defect instances.
- **Class-specific minimums:**
  - Crack: 1,500
  - Spalling: 800
  - Efflorescence: 800
- **Hard negatives:** 800 (Separate non-defect population, NOT included in physical-defect instances).

## 4. Mathematical Reconciliation
The sum of the class-specific minimums (1,500 + 800 + 800 = 3,100) mathematically exceeds the initially stated total minimum of 2,000 physical defect instances.

## 5. Approved Option — 3,100 Total (Option B)
- The class targets of 1,500 crack, 800 spalling, and 800 efflorescence remain mandatory.
- The minimum physical-defect target MUST be increased to 3,100.
- Rationale: The 3,100 target is selected because the existing class-specific minimums already require it. Reducing those class minimums merely to preserve the previous 2,000 aggregate would contradict the established class-coverage requirements. The 3,100 target is treated as the minimum collection requirement, not an exact upper limit.

## 6. Treatment of Hard Negatives
Hard negatives (target: 800) are explicitly excluded from the physical-defect instance count. They represent joints, seams, shadows, and stains.

## 7. Consequences
- **Field Sampling**: 55% higher acquisition volume.
- **Structures/Sites**: May require >15 distinct sites to avoid over-sampling.
- **Annotation Workload**: Significantly higher manual polygon annotation cost.
- **Reviewer Workload**: 20% review = 620 instances.
- **Calibration Coverage**: 40% = 1,240 calibrated instances.
- **Longitudinal Subset**: Larger, more robust longitudinal holdout.
- **Splits (Train/Val/Test)**: Larger test set, more stable generalization metrics.
- **Class Balance**: Enforces balance at higher absolute volumes.
- **Publication Methodology**: Statistically rigorous, highly defensible.

## 8. Explicit Approval Fields
- **approved_total_physical_defects:** 3100
- **approved_crack_target:** 1500
- **approved_spalling_target:** 800
- **approved_efflorescence_target:** 800
- **approved_hard_negative_target:** 800
- **decision_owner:** [PENDING_PROJECT_OWNER_ENTRY]
- **decision_date:** [PENDING_PROJECT_OWNER_ENTRY]
- **rationale:** Maintain strict class minimums to ensure statistical rigor for the research publication; adjusting the aggregate up to 3,100 correctly resolves the math without weakening coverage.

## 9. Rule
**The target gate is now resolved. Field collection may commence. However, production ML training remains BLOCKED until the required 3,100 instances are collected and pass the readiness checker.**
