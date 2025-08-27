import requests

response = requests.post(
    "http://127.0.0.1:5000/register/",
    json={
        "email": "user@example.com",
        "password": "password123"
    }
)

print("Регистрация:")
print(response.json())
print(response.status_code)

