# Field Data Target Resolution Required v0.1

**STATUS: RESOLVED**

*Note: The target contradiction documented below has been formally resolved. For the approved engineering decision and impact analysis, see [field_data_target_decision_record_v0.1.md](field_data_target_decision_record_v0.1.md).*

## 1. Historical Overview (Resolved State)
A mathematical contradiction existed in the documented Phase 9 field data collection targets. This contradiction prevented the ML pipelines from safely determining whether the field dataset satisfied the production training gate. It is now resolved.

## 2. Historical Conflicting Requirements
According to historical project documentation (`field_dataset_schema_v0.1.md` and `field_dataset_target_matrix_v0.1.md`):

**Target A: Total Volume**
- Minimum 2,000 unique physical defect instances.

**Target B: Class-Specific Coverage**
- Minimum 1,500 crack instances.
- Minimum 800 spalling instances.
- Minimum 800 efflorescence instances.

*(Note: The 800 labeled hard negatives are correctly treated as a separate non-defect population and are not included in the physical defect instance count.)*

## 3. The Mathematical Contradiction
The individual class minimums summed to 3,100 physical instances (1,500 + 800 + 800). This mathematically exceeded the initially stated total minimum of 2,000 physical defect instances.

## 4. Resolution
Engineering Leadership has formally **APPROVED** Option B (3,100 Total). The minimum target for field collection is now explicitly established as 3,100 physical defects, maintaining the robust 1,500 / 800 / 800 class coverages. Hard negatives remain a strictly separate population. Field data collection is now unblocked. Production ML training remains blocked until these targets are met.
