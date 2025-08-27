import requests


response = requests.post(
    "http://127.0.0.1:5000/login/",
    json={
        "email": "user@example.com",
        "password": "password123"
    }
)

data = response.json()
print("Логин:")
print(data)
print(response.status_code)

# Здесь мы получаем токен!
token = data["token"]
print(f"\nВаш токен: {token}")
