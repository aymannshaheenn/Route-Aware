import requests

url = "https://animosity-pregnant-stamp.ngrok-free.dev/api/segments/summary"
response = requests.get(url)

print("Status code:", response.status_code)
print("Response text:", response.text[:500])