import requests


response = requests.patch(
    "http://127.0.0.1:5000/announcement/3",
    json={
        "headline": "Вакансия Python-backend разработчик",
        "description": "Предлагаем работу программером!",
        "owner": "ООО Netology"
    }
)

print(response.json())
print(response.status_code)

