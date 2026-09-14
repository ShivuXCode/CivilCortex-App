# Forensic Technical Audit: Crack Detection & Binary Classification Pipeline

**Document ID:** `PHASE_2_BINARY_CLASSIFIER_AUDIT`  
**Target System:** CivilCortex Crack Detection & Structural Health Assessment Pipeline  
**Audit Scope:** Full Forensic Investigation of Machine Learning Models, Training Code, Backend Inference, Preprocessing Discrepancies, and Decision Logic  

---

## 1. Project Structure

### Complete Directory Tree
```
civilcortex/
├── backend/
│   ├── agents/
│   │   ├── nodes/
│   │   │   ├── agent1_condition.py       # [INFERENCE] Runs Keras model + Gemini Vision
│   │   │   ├── agent2_risk.py            # [INFERENCE] Calculates mathematical risk score
│   │   │   ├── agent3_priority.py        # [INFERENCE] Determines response urgency & turnaround
│   │   │   ├── agent4_planning.py        # [INFERENCE] RAG query against ChromaDB
│   │   │   ├── agent5_resources.py       # [INFERENCE] Deterministic workforce/cost mapping
│   │   │   └── agent6_llm.py             # [INFERENCE] Synthesizes final maintenance report
│   │   ├── graph.py                      # [INFERENCE] LangGraph StateGraph orchestration
│   │   └── state.py                      # [SCHEMA] AgentState TypedDict schema
│   ├── api/
│   │   ├── deps.py                       # [AUTH] JWT user authentication dependency
│   │   └── routes.py                     # [INFERENCE] FastAPI endpoints (/analyze-image, /analyze-maintenance)
│   ├── core/
│   │   ├── config.py                     # [CONFIG] Settings & environment variable loader
│   │   ├── database.py                   # [DB] SQLAlchemy SQLite/PostgreSQL connection engine
│   │   ├── logger.py                     # [LOGGING] Stream & file logger configuration
│   │   └── security.py                   # [AUTH] Password hashing & JWT token generation
│   ├── models/
│   │   ├── civilcortex_best.keras        # [MODEL] Saved Keras 3 Functional Model (7.43 MB weights, 21.4 MB archive)
│   │   ├── civilcortex_best.keras.dir/   # [MODEL] Extracted Keras config, metadata, and weights
│   │   └── domain_models.py              # [ORM] SQLAlchemy database models (User, Inspection)
│   ├── schemas/
│   │   └── request_models.py             # [SCHEMA] Pydantic request & response validation models
│   ├── scripts/
│   │   ├── init_db.py                    # [RAG SETUP] Embeds knowledge_base.txt into ChromaDB
│   │   └── ingest_standards.py           # [RAG SETUP] Ingests additional ACI & FHWA text standards
│   ├── services/
│   │   ├── pdf_generator.py              # [REPORTING] FPDF2 inspection report generator
│   │   ├── vision_analyzer.py            # [UNUSED/DEAD CODE] Standalone Gemini vision helper
│   │   └── workflow_runner.py            # [INFERENCE] Invokes LangGraph app with MaintenanceRequest
│   ├── tests/
│   │   └── test_agents.py                # [TEST] Unit tests for Agents 2, 4, and 5 (Agent 1 is NOT tested)
│   ├── main.py                           # [SERVER] FastAPI application entry point
│   ├── requirements.txt                  # [CONFIG] Python dependencies
│   └── test_model.py, test_hallucination.py, test_pdf.py, test_post.py, test_graph.py
├── docs/
│   ├── MODEL_ANALYSIS.md
│   ├── PHASE_2_BINARY_CLASSIFIER_AUDIT.md
│   ├── PROJECT_DOCUMENTATION.md
│   └── SETUP_AND_RUNNING.md
├── frontend/
│   ├── src/                              # React 19 + Vite web interface
│   └── package.json
├── ml_pipeline/
│   ├── data/
│   │   ├── images/                       # [DATASET] Directory for training images (EMPTY)
│   │   └── masks/                        # [DATASET] Directory for ground-truth masks (EMPTY)
│   ├── requirements.txt                  # [CONFIG] ML dependencies (tensorflow, numpy, opencv)
│   └── train.py                          # [TRAINING] Disconnected U-Net training script (256x256)
├── docker-compose.yml
└── PROJECT_DOCUMENTATION.md
```

### Forensic Inventory of Key Components

| File | Purpose | Used in Training | Used in Inference | Callers / Importers |
|---|---|---|---|---|
| `ml_pipeline/train.py` | Toy U-Net training script (256x256) | **Yes** (Standalone) | **No** | None (CLI execution only) |
| `backend/models/civilcortex_best.keras` | Saved weights loaded at runtime (384x384) | **No** (Artifact) | **Yes** | `backend/agents/nodes/agent1_condition.py` |
| `backend/agents/nodes/agent1_condition.py` | Runs Keras model inference + Gemini Vision fallback | **No** | **Yes** | `backend/agents/graph.py` |
| `backend/services/vision_analyzer.py` | Redundant multimodal vision analyzer | **No** | **No** (Dead code) | Imported in `routes.py` line 4 but never executed |
| `backend/services/workflow_runner.py` | Bridge between API request and LangGraph runtime | **No** | **Yes** | `backend/api/routes.py` |
| `backend/agents/graph.py` | Compiles LangGraph StateGraph pipeline | **No** | **Yes** | `backend/services/workflow_runner.py` |
| `backend/api/routes.py` | FastAPI HTTP endpoints (`/analyze-image`) | **No** | **Yes** | `backend/main.py` |
| `backend/core/config.py` | Configuration and environment loader (`GEMINI_API_KEY`) | **No** | **Yes** | All backend modules |

---

## 2. Identify Every Model

### Model 1: Production Runtime Model (`civilcortex_best.keras`)
* **Filename:** `backend/models/civilcortex_best.keras` (Unpacked config in `backend/models/civilcortex_best.keras.dir/`)
* **Framework:** Keras 3.13.2 / TensorFlow
* **Architecture:** Deep 4-Stage Functional U-Net with Batch Normalization and Dropout (`Functional`, 70 total layers)
* **Input Shape:** `(None, 384, 384, 3)`
* **Output Shape:** `(None, 384, 384, 1)`
* **Output Layer Name:** `crack_probability` (Conv2D with 1x1 kernel)
* **Output Activation:** `sigmoid`
* **Model Type:** **Semantic Segmentation (Pixel-level probability map)**, *NOT* image-level binary classification.
* **File Size:** 21,415,573 bytes (~20.4 MB archive, 7.43 MB parameters)
* **Parameters:** 1,946,993 total (1,944,049 trainable, 2,944 non-trainable)
* **Creation Timestamp:** `2026-08-20@17:56:46` (from `metadata.json`)
* **Training Source:** **Unknown / Missing from repository** (Was NOT generated by `ml_pipeline/train.py`).
* **Where Loaded:** `backend/agents/nodes/agent1_condition.py:L12-14`
* **Where Used for Inference:** `backend/agents/nodes/agent1_condition.py:L44`
* **Is it used by backend:** **YES**, this is the active model loaded when users upload images.

#### Keras Model Summary (`civilcortex_best.keras`):
```
__________________________________________________________________________________________________
 Layer (type)                   Output Shape         Param #     Connected to                     
==================================================================================================
 input_layer (InputLayer)       (None, 384, 384, 3)  0           -                                
 conv2d (Conv2D)                (None, 384, 384, 16) 448         input_layer[0][0]                
 batch_normalization            (None, 384, 384, 16) 64          conv2d[0][0]                     
 activation (Activation: relu)  (None, 384, 384, 16) 0           batch_normalization[0][0]        
 conv2d_1 (Conv2D)              (None, 384, 384, 16) 2,320       activation[0][0]                 
 batch_normalization_1          (None, 384, 384, 16) 64          conv2d_1[0][0]                   
 activation_1 (Activation)      (None, 384, 384, 16) 0           batch_normalization_1[0][0]      
 max_pooling2d (MaxPooling2D)   (None, 192, 192, 16) 0           activation_1[0][0]               
 conv2d_2 (Conv2D)              (None, 192, 192, 32) 4,640       max_pooling2d[0][0]              
 ... [Intermediate Stages with 32, 64, 128 filters + Dropout(0.2)] ...
 conv2d_8 (Conv2D: Bottleneck)  (None, 24, 24, 256)  295,168     max_pooling2d_3[0][0]            
 ... [4 Decoder Stages with Conv2DTranspose + Concatenate Skip Connections] ...
 conv2d_17 (Conv2D)             (None, 384, 384, 16) 2,320       activation_16[0][0]              
 batch_normalization_17         (None, 384, 384, 16) 64          conv2d_17[0][0]                  
 activation_17 (Activation)     (None, 384, 384, 16) 0           batch_normalization_17[0][0]     
 crack_probability (Conv2D)     (None, 384, 384, 1)  17          activation_17[0][0] (Sigmoid)    
==================================================================================================
Total params: 1,946,993 (7.43 MB)
Trainable params: 1,944,049 (7.42 MB)
Non-trainable params: 2,944 (11.50 KB)
__________________________________________________________________________________________________
```

---

### Model 2: Script Definition Model (`ml_pipeline/train.py`)
* **Filename:** Defined in `ml_pipeline/train.py` (target save path: `../backend/models/civilcortex_best_v2.keras`)
* **Framework:** TensorFlow / Keras
* **Architecture:** Simple 3-Stage U-Net without Batch Normalization or Dropout
* **Input Shape:** `(None, 256, 256, 3)`
* **Output Shape:** `(None, 256, 256, 1)`
* **Output Activation:** `sigmoid`
* **Model Type:** Semantic Segmentation
* **Is it used by backend:** **NO**. It is an unexecuted, disconnected script.

---

### Model 3: Multimodal Vision LLM (`gemini-3.6-flash`)
* **Framework:** Google Generative AI via `langchain-google-genai`
* **Where Loaded / Used:** `backend/agents/nodes/agent1_condition.py:L60` and `backend/services/vision_analyzer.py:L15`
* **Role:** Receives raw image bytes encoded as Base64 JPEG and classifies defect subtype and severity.

---

## 3. Trace the Complete Inference Pipeline

```
[Client Image Upload]
         │
         ▼
[1] FastAPI Endpoint: `POST /api/analyze-image` (`backend/api/routes.py:L48-83`)
    - Reads raw image bytes: `image_bytes = await file.read()` (Line 65)
    - Extracts MIME type: `mime_type = file.content_type or "image/jpeg"` (Line 66)
    - Constructs `MaintenanceRequest(image_bytes=image_bytes, ...)` (Line 73)
    - Calls `run_analysis(request)` (`backend/services/workflow_runner.py:L4`)
         │
         ▼
[2] Workflow Runner (`backend/services/workflow_runner.py:L4-16`)
    - Initializes graph state dictionary: `initial_state = {"image_bytes": ..., ...}` (Line 6)
    - Invokes LangGraph runtime: `workflow_app.invoke(initial_state)` (Line 15)
         │
         ▼
[3] Node 1: Agent 1 Condition (`backend/agents/nodes/agent1_condition.py:L25-95`)
    - Retrieves bytes: `image_bytes = state.get("image_bytes")` (Line 26)
    - Decodes & converts color space:
      `img = Image.open(io.BytesIO(image_bytes)).convert("RGB")` (Line 40)
    - Resizes without aspect-ratio preservation:
      `img = img.resize((384, 384))` (Line 41)
    - Normalizes to float range [0.0, 1.0]:
      `img_arr = np.array(img) / 255.0` (Line 42)
    - Expands batch dimension:
      `tensor = np.expand_dims(img_arr, axis=0)` (Shape: `(1, 384, 384, 3)`, dtype `float64`) (Line 44)
    - Local Model Prediction:
      `pred = model.predict(tensor)[0]` (Output shape: `(384, 384, 1)`) (Line 44)
    - Thresholding & Mask Creation:
      `mask = (pred > 0.40).astype(np.uint8)` (Line 45)
    - Heuristic Crack Ratio Calculation:
      `crack_ratio = float(np.sum(mask) / (384 * 384))` (Line 46)
    - Penalty & Health Score Calculation:
      `penalty = int(crack_ratio * 500)` (Line 48)
      `health_score = max(0, 100 - penalty)` (Line 49)
      `condition = "Critical" if health_score < 60 else ("Fair" if health_score < 90 else "Excellent")` (Line 50)
         │
         ▼
[4] Gemini Vision Multimodal Secondary Classification (`agent1_condition.py:L56-89`)
    - Base64 encodes raw image bytes: `img_b64 = base64.b64encode(image_bytes).decode("utf-8")` (Line 63)
    - Dynamically generates prompt based on `health_score`:
      * If `health_score >= 95`:
        "Analyze this image... The local segmentation model detected NO significant cracks... Confirm there is no crack by returning crack_type 'None' and severity 'low'." (Line 67)
      * Else:
        "Analyze this image... The local AI detected a crack covering {crack_ratio*100:.1f}% of the area. Identify the crack type..." (Line 69)
    - Invokes `gemini-3.6-flash`: `gemini_check = structured_llm.invoke([msg])` (Line 78)
    - Extracts `crack_type` and `severity` (Line 79-80)
         │
         ▼
[5] Parallel Nodes 2, 3, 4, 5 Execution (`backend/agents/graph.py:L15-25`)
    - Agent 2 calculates `risk_score` from condition and structure multipliers
    - Agent 3 maps turnaround priority based on condition
    - Agent 4 retrieves regulatory standards from ChromaDB using `crack_type`
    - Agent 5 computes required workforce and estimated repair budget
         │
         ▼
[6] Node 6: LLM Recommendation (`backend/agents/nodes/agent6_llm.py`)
    - Generates formal compliance report citing retrieved standards
         │
         ▼
[7] API Response Serialization (`backend/api/routes.py:L86-163`)
    - Encodes base64 preview for frontend rendering
    - Saves inspection record to database
    - Returns JSON payload to client
```

---

## 4. Determinism Analysis: Why Same Image Produces Inconsistent Results

### Empirical Determinism Test
We ran 10 sequential inference passes on the identical input tensor using `model.predict(..., verbose=0)`.
* **Result:** `max_diff = 0.000000` (`np.array_equal == True`).
* **Conclusion:** The standalone Keras model is mathematically deterministic.

### Sources of Non-Determinism in the Full Pipeline:
1. **Downstream Multimodal LLM (`gemini-3.6-flash`)**:
   * Cloud LLM APIs exhibit token variance due to distributed GPU cluster batching and floating-point non-associativity.
   * `crack_type` (which dictates RAG retrieval and the final report) is produced by Gemini Vision, not by deterministic argmax logic.
2. **API Rate Limits and Quota Exceptions**:
   * On HTTP 429 rate limit or quota exhaustion, `agent1_condition.py` catches the exception and overrides the defect type:
     ```python
     crack_type = "API_ERROR_RATE_LIMIT"  # or "API_ERROR_UNKNOWN"
     ```
   * This causes the exact same image to return completely different defect outputs depending on network/API status.
3. **Dynamic Prompt Drift**:
   * The prompt dynamically injects `{crack_ratio*100:.1f}%`. Tiny pixel variations from client-side image compression shift the prompt string, prompting the LLM down different reasoning paths.

---

## 5. Training vs. Inference Preprocessing Comparison

| Parameter | Training (`ml_pipeline/train.py:L76-90`) | Inference (`agent1_condition.py:L39-44`) | Match? | Forensic Impact |
|---|---|---|---|---|
| **Color Space** | **OpenCV BGR** (`cv2.imread`) | **PIL RGB** (`Image.open().convert("RGB")`) | ❌ **MISMATCH** | **CRITICAL**: Red and Blue channels are swapped. Blue concrete tint is read as red by the model. |
| **Input Resolution** | `256 x 256` | `384 x 384` | ❌ **MISMATCH** | **CRITICAL**: Spatial receptive field and filter activations do not align. |
| **Aspect Ratio Handling** | Direct distortion resize (`cv2.resize`) | Direct distortion resize (`img.resize`) | ⚠️ Partial | Aspect ratios are stretched/squashed, distorting crack width and angle. |
| **Crop / Padding** | None | None | ✅ Match | No center crop or letterbox padding applied in either. |
| **Normalization** | `img / 255.0` (Range [0, 1]) | `np.array(img) / 255.0` (Range [0, 1]) | ✅ Match | Identical scalar division. |
| **Data Type** | `float64` / `float32` | `float64` (from PIL division) | ✅ Match | Standard float representation. |
| **Channels** | 3 (BGR) | 3 (RGB) | ❌ **MISMATCH** | Inverted channel ordering. |
| **Batch Dimension** | `np.array(X)` (Batch size = 8) | `np.expand_dims(..., axis=0)` (Batch size = 1) | ✅ Match | Correct batch dimension. |
| **Data Augmentation** | **NONE** | **NONE** | ⚠️ Match | No rotation, contrast, or shadow invariance learned during training. |

---

## 6. Classification vs. Segmentation Discrepancy

1. **What the training script trains:** A semantic segmentation U-Net targeting pixel masks `(H, W, 1)`.
2. **What the saved model outputs:** A dense probability matrix `(1, 384, 384, 1)`. It does *not* output a binary class probability `[0.0 to 1.0]`.
3. **How backend interprets the output:**
   ```python
   mask = (pred > 0.40).astype(np.uint8)
   crack_ratio = float(np.sum(mask) / (IMG_SIZE * IMG_SIZE))
   penalty = int(crack_ratio * 500)
   health_score = max(0, 100 - penalty)
   ```
4. **Why this logic fails:**
   * In a 384x384 image (147,456 pixels), if just **0.08 (8%)** of normal concrete surface texture exceeds 0.40 probability, `crack_ratio` is 0.08.
   * `penalty = int(0.08 * 500) = 40` -> `health_score = 60` (**Critical Condition** on clean concrete!).
   * Clean concrete textures consistently trigger high background noise activations, invalidating the threshold.

---

## 7. Dataset Audit

* **Dataset Path:** `ml_pipeline/data/images/` and `ml_pipeline/data/masks/`
* **File Count:** **0 files** (Both directories are completely empty).
* **Dataset Availability:** **Dataset files are NOT included in the repository**.
* **Target Format in Code:** Matched `.jpg` image and mask pairs.
* **Splitting in `train.py`:** `validation_split=0.2` in `model.fit()` (Sequential tail-end 20% slice, no random seed, no stratification).

---

## 8. Data Leakage Audit

* `train.py` loads data via `sorted(glob.glob(...))` and uses `model.fit(..., validation_split=0.2)`:
  1. The validation split takes the last 20% of alphabetically sorted files.
  2. If images are extracted frames from the same video or same physical structure, correlated visual patterns leak across train and validation sets.
  3. No group-aware or structure-aware cross-validation is implemented.

---

## 9. Class Imbalance Audit

* **Binary Classification Imbalance:** Ratio of crack images vs. no-crack images.
* **Segmentation Pixel Imbalance:** Crack pixels typically occupy **0.1% to 3.0%** of an image.
* **Flaw in `train.py`:** Standard `binary_crossentropy` with `metrics=['accuracy']` on 1% crack pixels achieves **99% accuracy by predicting all zeros**. The model learns to ignore fine cracks or outputs unstable background noise.

---

## 10. Training Configuration Audit

| Parameter | Configuration in `ml_pipeline/train.py` | Production Suitability |
|---|---|---|
| **Architecture** | 3-stage custom U-Net | Toy model; lacks Batch Normalization & residual connections |
| **Pretrained Backbone** | None (Trained from scratch) | Inefficient for small structural datasets |
| **Input Resolution** | `256 x 256` | Does not match backend inference resolution (`384 x 384`) |
| **Batch Size** | `8` | Standard |
| **Epochs** | `20` | Insufficient without transfer learning |
| **Optimizer** | `adam` (default LR `0.001`) | Fixed LR; no learning rate scheduler |
| **Loss Function** | `binary_crossentropy` | **Unsuitable**: Severely degrades under class imbalance |
| **Metrics** | `['accuracy']` | **Misleading**: Pixel accuracy masks failure to detect cracks |
| **Augmentation** | None | Vulnerable to real-world lighting and orientation changes |
| **Callbacks** | None | Overfitting risk; saves final epoch unconditionally |

---

## 11. Evaluation Metrics Audit

* **Existing Evaluation Scripts:** **None** in the repository.
* **Reported Metric:** Only raw pixel accuracy (`metrics=['accuracy']`).
* **Why this is invalid:** Pixel accuracy rewards predicting background everywhere. Proper evaluation requires **Precision, Recall, F1-Score, PR-AUC**, and for segmentation, **Dice Coefficient / IoU (Intersection over Union)**.

---

## 12. Threshold Analysis

The pipeline relies on four arbitrary hardcoded thresholds:
1. **`pred > 0.40`** (`agent1_condition.py:L45`): Lowering to 0.40 causes massive false positives from normal surface grain.
2. **`penalty = int(crack_ratio * 500)`** (`agent1_condition.py:L48`): Any crack ratio above `0.20` (20%) results in `penalty >= 100`, making health score `0`.
3. **`health_score >= 95`** (`agent1_condition.py:L66`): Decides whether to prompt Gemini that the surface is clean.
4. **`health_score < 60` ("Critical") / `< 90` ("Fair")** (`agent1_condition.py:L50`): Condition classification bounds.

---

## 13. Gemini / VLM Involvement & Confirmation Bias

### Prompt Analysis (`backend/agents/nodes/agent1_condition.py:L66-70`):
```python
if health_score >= 95:
    prompt = "Analyze this image of a concrete surface. The local segmentation model detected NO significant cracks (Health Score is near perfect). Confirm there is no crack by returning crack_type 'None' and severity 'low'."
else:
    prompt = f"Analyze this image of a structural defect. The local AI detected a crack covering {crack_ratio*100:.1f}% of the area. Identify the crack type (e.g., 'Spalling', 'Hairline Crack') and classify its visual severity as 'low', 'medium', or 'high'."
```

### Forensic Findings:
1. **Severe Confirmation Bias:** When `health_score >= 95`, the prompt instructs Gemini to agree (*"Confirm there is no crack"*), creating false negatives if the local model misses a fine crack.
2. **Hallucination Priming:** When `health_score < 95`, the prompt primes Gemini that a crack was already found. Even on non-concrete images, Gemini is prompted to pick a crack type.
3. **Image Input:** Gemini receives raw base64 JPEG bytes, *not* the segmentation mask or preprocessed tensor.

---

## 14. Logical Testing of the Existing Model

Empirical test results using `civilcortex_best.keras` on controlled inputs without modifying any codebase files:

| Test Input Sample | Raw Input Resolution | Preprocessed Tensor Shape | Model Raw Output Range (Min / Mean / Max) | Threshold Applied | Intermediate Crack Ratio | Final Health Score & Condition | Ground Truth Expected |
|---|---|---|---|---|---|---|---|
| **Solid White Image** (`1.0`) | `384 x 384` | `(1, 384, 384, 3)` | `0.000 / 0.205 / 0.627` | `> 0.40` | `0.0075` (0.75%) | **96** (Excellent) | No Crack |
| **Clean Concrete Gray** (`RGB 180`) | `384 x 384` | `(1, 384, 384, 3)` | `0.112 / 0.396 / 0.604` | `> 0.40` | **`0.3501` (35.0%)** | **0 (Critical)** | **No Crack (Massive False Positive)** |
| **Concrete + 4px Crack Line** | `384 x 384` | `(1, 384, 384, 3)` | `0.112 / 0.397 / 0.633` | `> 0.40` | **`0.3576` (35.8%)** | **0 (Critical)** | Crack Present (Only +0.7% over clean) |
| **Solid Gray Baseline** (`0.50`) | `384 x 384` | `(1, 384, 384, 3)` | `0.134 / 0.415 / 0.637` | `> 0.40` | **`0.6051` (60.5%)** | **0 (Critical)** | **No Crack (Massive False Positive)** |
| **Solid Black / Shadow** (`0.00`) | `384 x 384` | `(1, 384, 384, 3)` | `0.210 / 0.495 / 0.638` | `> 0.40` | **`0.9974` (99.7%)** | **0 (Critical)** | **No Crack (False Positive)** |
| **Repository Asset** (`frontend/src/assets/hero.png`) | `343 x 361` | `(1, 384, 384, 3)` | `0.167 / 0.486 / 0.735` | `> 0.40` | **`0.9489` (94.9%)** | **0 (Critical)** | Non-concrete Illustration |

### Key Finding:
The baseline activation on standard concrete gray is `0.38 - 0.42`. Thresholding at `0.40` causes clean concrete to be classified as **35% to 60% cracked**, rendering the model completely invalid.

---

## 15. Root Causes Classification

### 🔴 CRITICAL ISSUES
1. **BGR vs. RGB Color Inversion:** Training in OpenCV BGR (`train.py:L78`) vs. inference in PIL RGB (`agent1_condition.py:L40`).
2. **Task Mismatch:** U-Net segmentation mask pixel sum used as a proxy for binary classification (`agent1_condition.py:L44-46`).
3. **Severe False-Positive Bias on Concrete Textures:** Normal concrete gray produces a 35% crack ratio and an immediate Health Score of 0.

### 🟠 HIGH ISSUES
4. **Orphaned Production Weights:** `civilcortex_best.keras` has no matching training script or dataset in the repository.
5. **Confirmation Bias in LLM Prompts:** Agent 1 forces Gemini to confirm local model conclusions (`agent1_condition.py:L66-70`).
6. **Class Imbalance & Wrong Loss Function in `train.py`:** Standard `binary_crossentropy` with naive pixel accuracy.

### 🟡 MEDIUM ISSUES
7. **Resolution Mismatch:** `256x256` in `train.py` vs. `384x384` in backend inference.
8. **Lack of Data Augmentation:** No rotation, contrast, or lighting invariance.
9. **Dead Code:** Redundant `vision_analyzer.py` creates confusion in the API layer.

### 🟢 LOW ISSUES
10. **Lack of Fixed Random Seeds** in training and data loading.

---

## 16. What We Should Build

### Option A — Repair Existing Model
* **Salvageable?** **NO**.
* **Reason:** The existing weights in `civilcortex_best.keras` are fundamentally saturated with background texture noise. Because the original training dataset is missing, these weights cannot be fine-tuned or calibrated reliably.

### Option B — Build a Clean Binary Classifier (RECOMMENDED)
* **Target Task:** Image-level binary classification: **Crack (1) vs. No Crack (0)**.
* **Recommended Architecture:** Pretrained backbone (**MobileNetV3-Small / EfficientNetB0 / ResNet50**) with GlobalAveragePooling2D and a single binary output (`Dense(1, activation='sigmoid')`).
* **Input Resolution:** `224 x 224` or `256 x 256` (Standard ImageNet resolution, fast inference on CPU/edge).
* **Loss Function:** `BinaryCrossentropy(label_smoothing=0.05)` or `BinaryFocalCrossentropy`.
* **Metrics:** `Precision`, `Recall`, `AUC`, `F1-Score` (at optimal threshold).
* **Data Augmentation:** Random Flips (Horizontal & Vertical), Random Rotation (±90°), Random Brightness/Contrast (±20%), Random Gaussian Blur.
* **Threshold Selection:** Calibrate decision threshold on a validation PR-curve (prioritizing Recall >= 0.95 for safety-critical inspection).

### Option C — Semantic Segmentation
* **Should we use segmentation now?** **NO (Postpone to Phase 2)**.
* **Reason:** The target requirement is strictly **Binary Classification (Crack vs. No Crack)**. Pixel-level segmentation requires expensive polygon/mask annotations, Dice/Tversky loss tuning, and complex post-processing. A dedicated binary classifier will be smaller (~10-20 MB), 5x faster, and significantly more accurate.

---

## 17. Final Executive Summary

### Current System Summary
* **Input:** Raw Image Bytes (via `POST /api/analyze-image`)
* **Model:** `civilcortex_best.keras` (4-Stage U-Net, 70 layers, `384x384x3` -> `384x384x1`)
* **Task:** Attempting binary classification using a segmentation mask pixel-sum heuristic
* **Inference:** Resizes to 384x384 RGB, predicts pixel probabilities, thresholds at `0.40`, computes `crack_ratio`
* **Final Decision:** Feeds `crack_ratio` into a biased prompt to `gemini-3.6-flash` to extract defect type and severity

### Top 10 Problems Ranked by Severity
1. **Task Mismatch:** Semantic segmentation mask pixel sum is used as a proxy for binary classification.
2. **False Positive Saturation:** Clean concrete triggers a **35.0% crack ratio** and gives a Health Score of 0.
3. **Color Space Inversion:** Training script reads BGR via OpenCV; inference reads RGB via PIL.
4. **Orphaned Production Weights:** `civilcortex_best.keras` has no matching training script or dataset in the repo.
5. **Confirmation Bias in LLM Prompts:** Agent 1 forces Gemini to confirm local model conclusions.
6. **Class Imbalance Mismatch:** `train.py` compiles with naive pixel accuracy and binary crossentropy.
7. **Resolution Mismatch:** `train.py` specifies `256x256`, while backend inference loads `384x384`.
8. **Missing Dataset:** `ml_pipeline/data/images` and `masks` contain 0 files.
9. **Lack of Data Augmentation:** No rotation, contrast, or lighting invariance.
10. **Dead Code:** Redundant `vision_analyzer.py` creates confusion in the API layer.

### Recommended Target Architecture
```
┌──────────────────────────────────────────────────────────┐
│                   INSPECTION IMAGE                       │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                 PREPROCESSING PIPELINE                   │
│  - Resize to 224x224 (preserve aspect ratio/letterbox)   │
│  - Standard RGB color format                             │
│  - Standardized Normalization                            │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│             DEDICATED BINARY CLASSIFIER                  │
│       (MobileNetV3 / EfficientNet / ResNet Backbone)     │
│        GlobalAveragePooling2D + Dense(1, Sigmoid)        │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                CRACK PROBABILITY (0.0 - 1.0)             │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│          OPTIMIZED DECISION THRESHOLD (e.g. 0.50)        │
└────────────────────────────┬─────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      [CRACK DETECTED]              [NO CRACK DETECTED]
              │                             │
              ▼                             ▼
   (Invoke Multimodal LLM         (Set Health Score = 100,
   for Defect Subtype & RAG)       Condition = "Excellent")
```

### What We Should NOT Do Yet
* ❌ Do **NOT** attempt to fine-tune `civilcortex_best.keras` (the weights are corrupted with background false-positive bias).
* ❌ Do **NOT** build a complex semantic segmentation U-Net when the current requirement is binary classification.
* ❌ Do **NOT** keep prompt instructions that bias Gemini to confirm local model predictions.

### Required Information Missing
To train and validate the new binary classifier, we need:
1. **Concrete Crack Image Dataset:** A curated dataset of structural images organized into `crack/` and `no_crack/` (e.g. standard open benchmarks like SDNET2018 or Mendeley Concrete Crack Images).
2. **Target Inference Hardware Constraints:** Confirmation whether inference will run on CPU, Cloud GPU, or mobile/edge devices.

---

### Final Recommendation

**BUILD A CLEAN BINARY CLASSIFIER**
