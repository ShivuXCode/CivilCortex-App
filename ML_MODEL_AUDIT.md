# CivilCortex ML Model Audit

## Executive Summary
This audit reviews the current Computer Vision / ML system embedded in the CivilCortex backend. The repository contains a single Keras model (`civilcortex_best.keras`) which performs binary image segmentation. While the model successfully generates a segmentation mask, the current implementation severely mishandles the model's output by computing an overall image confidence using the maximum pixel probability (`np.max(mask)`). The system is not production-ready for engineering decision support in its current state.

## Model Identity
- **File:** `backend/models/civilcortex_best.keras`
- **Inferred Architecture:** U-Net or similar Fully Convolutional Network for image segmentation.
- **Model Type:** Binary Image Segmentation

## Model Architecture
Status: INFERRED
Evidence: `backend/app/services/ml_service.py`
The model generates a spatial mask instead of a classification vector, implying a segmentation architecture. The custom loss/metrics used during training (`combined_loss`, `dice_metric`, `iou_metric`) are standard for segmentation models.

## Input Contract
Status: CONFIRMED
Evidence: `backend/app/services/ml_service.py`
- **Input Shape:** `(1, 384, 384, 3)`
- **Input Datatype:** `float32`
- **Expected Preprocessing:** RGB color space, resized to `384x384`, and normalized to the range `[0, 1]` via `/ 255.0`.

## Output Contract
Status: CONFIRMED
Evidence: `backend/app/services/ml_service.py`
- **Output Shape:** Spatial mask, inferred as `(1, 384, 384, 1)`.
- **Output Datatype:** Float array of probabilities.
- **Output Activation:** Sigmoid (inferred, as values represent probabilities).
- **Meaning:** Each pixel value represents the probability of belonging to the "crack" class.
- **Class Labels:** Implicitly Binary (0 = Background/None, 1 = Crack).

## Preprocessing
Status: CONFIRMED
Evidence: `backend/app/services/ml_service.py`
The image is read via OpenCV, converted from BGR to RGB, resized to `384x384`, normalized to `[0, 1]`, and expanded to a batch size of 1.

## Postprocessing
Status: CONFIRMED
Evidence: `backend/app/services/ml_service.py`
The model output is currently only processed by extracting the maximum pixel value (`np.max(mask)`). The spatial mask is otherwise completely ignored and discarded. 

## Confidence Calculation
Status: CONFIRMED
Evidence: `backend/app/services/ml_service.py`
- **Calculation:** `confidence = float(np.max(mask))`
- **Analysis:** This calculation is technically unjustified and highly fragile. "Maximum pixel probability" is not an overall image confidence score. If a single pixel is falsely predicted with a 0.9 probability due to noise or a speck of dirt, the entire image is flagged as "crack" with 90% confidence, even if 99.999% of the pixels correctly predicted 0. 
- **Suitability:** This is entirely unsuitable for engineering decision support. A spatial statistic (such as area of contiguous pixels above a threshold) must be used instead.

## Segmentation Analysis
Status: CONFIRMED
- **Supported by Current Implementation:** Detecting if any single pixel exceeds a 0.5 threshold.
- **Possible but Not Implemented:** Crack area, crack density, mask contours, bounding regions, crack skeletonization (length/width). The model outputs the mask, but the service discards it.
- **Requires Additional Model/Training Data:** Distinguishing between multiple defect types (e.g., spalling, efflorescence) or measuring physical crack depth.

## Model Loading
Status: CONFIRMED
Evidence: `backend/app/services/ml_service.py`
The model is loaded using `tf.keras.models.load_model` with `compile=False`. Custom metrics (`dice_metric`, `iou_metric`) and losses (`combined_loss`) are successfully bypassed using dummy functions, ensuring reliable loading in the inference environment without needing the original training code.

## Runtime / Hardware
Status: INFERRED
Evidence: `backend/app/services/ml_service.py`
The model runs synchronously inside the Python process on the CPU (unless TensorFlow detects a GPU). It uses basic `model.predict`, which may be slow for large batches but is acceptable for async single-image processing.

## Performance Considerations
Status: INFERRED
Inference happens sequentially on a 384x384 image. It is relatively lightweight but could bottleneck the celery/RQ worker if scaled to thousands of images concurrently.

## Evaluation Evidence
Status: UNKNOWN
Evidence: NOT ESTABLISHED FROM REPOSITORY.
There are no test datasets, validation metrics, IoU/Dice scores, or calibration curves available in the repository to evaluate the model's real-world accuracy.

## Reliability Limitations
Status: HIGH CONFIDENCE
The reliance on `np.max(mask) > 0.5` means the model is almost certainly producing a high rate of False Positives on noisy images. 

## Engineering Suitability
Status: LOW CONFIDENCE
In its current state, the ML service acts merely as a naive trigger. The AI cannot be trusted for structural decision-making until the mask is properly thresholded and geometrically analyzed (e.g., crack width/length).

## Missing Evidence
- No validation metrics.
- No class imbalance mitigation documentation.
- No calibration reports.

## Recommended ML Work
1. **Refactor Postprocessing:** Replace `np.max` with a contour-finding or area-summation algorithm (e.g., sum of pixels > 0.5, or largest connected component).
2. **Expose Geometric Features:** Use the mask to estimate crack length and area, providing these as contextual inputs to the LLM instead of a naive "crack detected" boolean.
3. **Threshold Calibration:** Determine a statistically valid threshold (e.g., minimum contiguous area) before classifying an image as defective.

## Phase 18 ML Readiness
The system is NOT ready for production ML deployment until postprocessing is rewritten to extract meaningful engineering metrics from the spatial mask.
