import requests

from client_login import token


token = token

response = requests.post(
    "http://127.0.0.1:5000/announcement",
    json={
        "headline": "Вакансия продавец-консультант",
        "description": "Работа продавцом в Магнит",
        "owner": "IT-команда"
    },
    headers={
        "Authorization": f"Bearer {token}"
    }
)

print(response.json())
print(response.status_code)

