
import requests

url = "http://127.0.0.1:5000/api/analyze"

with open("road.jpg", "rb") as image:
    response = requests.post(
        url,
        files={"image": ("road.jpg", image, "image/jpeg")}
    )

print("Status code:", response.status_code)
print(response.json())
