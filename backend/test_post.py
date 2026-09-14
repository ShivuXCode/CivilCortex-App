import requests

url = "http://127.0.0.1:8000/api/analyze-image"
files = {'file': ('dummy.jpg', b'dummy content', 'image/jpeg')}
data = {'helmet_compliance': 100.0, 'delay_risk': 'low'}

print("Sending POST request to /api/analyze-image...")
response = requests.post(url, files=files, data=data)
print(f"Status Code: {response.status_code}")
try:
    print(response.json())
except Exception as e:
    print("Error parsing JSON:", e)
    print("Raw text:", response.text)
