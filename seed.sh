#!/bin/bash
echo "Registering user..."
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/register -H "Content-Type: application/json" -d '{"email":"qa2@example.com", "password":"password123", "full_name":"QA Inspector"}' | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "Registration failed or already registered, trying login..."
    TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/login -d "username=qa2@example.com&password=password123" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
fi

echo "Got token: $TOKEN"

echo "Uploading image..."
RES=$(curl -s -X POST http://127.0.0.1:8000/api/inspections/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/shivanisrimurugesan/civilcortex_project/Datasets/DATA_Maguire_20180517_ALL/SDNET2018/D/UD/7002-180.jpg" \
  -F "building_id=1")
INSPECTION_ID=$(echo $RES | grep -o '"inspection_id":[0-9]*' | grep -o '[0-9]*')
echo "Created inspection ID: $INSPECTION_ID"

echo "Confirming crack (Step 2)..."
curl -s -X POST http://127.0.0.1:8000/api/inspections/$INSPECTION_ID/confirm-crack \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "NEW",
    "observation_data": {
      "element_type": "Column",
      "severity_level": "MODERATE",
      "cv_detection": {
        "detection_id": "det_1",
        "model_confidence": 0.95,
        "bounding_box": [10, 20, 100, 200],
        "defect_type": "Diagonal Crack",
        "measurement": {
          "pixel_length": 1420,
          "physical_length": 150,
          "physical_width": 2.5,
          "calibration_status": "CALIBRATED"
        },
        "geometry": {
          "orientation_degrees": 45
        }
      }
    }
  }'

echo "Done"
