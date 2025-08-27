import os
from functools import wraps           # Для создания декораторов
from flask import request, jsonify   # Для работы с запросами Flask
import jwt                          # Для работы с JWT токенами
from datetime import datetime, timedelta  # Для работы с датами
from dotenv import load_dotenv

from models import Session, User, Announcement    # Наши модели


load_dotenv()

# Секретный ключ для подписи JWT токенов
# В production лучше брать из .env файла!
SECRET_KEY = os.getenv("SECRET_KEY")

def generate_token(user_id: int) -> str:
    '''Создаем JWT токен для пользователя'''

    # Payload - данные, которые мы хотим положить в токен
    payload = {
        "user_id": user_id,  # ID пользователя
        "exp": datetime.utcnow() + timedelta(hours=24),  # Когда токен истечёт (24 часа)
        "iat": datetime.utcnow()  # Когда токен создан
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    '''Проверяем JWT токен и возвращаем данные из него'''

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Возвращаем данные: {'user_id': 1, 'exp': ..., 'iat': ...}
    
    except jwt.ExpiredSignatureError:
        # Токен истёк (прошло 24 часа)
        return None
    
    except jwt.InvalidTokenError:
        # Невалидный токен (подделка, ошибка и т.д.)
        return None


def get_current_user() -> User:
    '''Получаем текущего пользователя из токена в заголовке запроса'''
    
    # Получаем заголовок Authorization
    # Пример: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    auth_header = request.headers.get("Authorization")
    
    # Если заголовка нет - пользователь не авторизован
    if not auth_header:
        return None
    
    try:
        # Разбиваем строку по пробелу: ["Bearer", "токен"]
        token = auth_header.split(" ")[1]  # Берём второй элемент - сам токен
        
        # Проверяем токен
        payload = verify_token(token)
        if not payload:
            return None  # Токен невалидный
        
        # Создаём сессию с базой
        session = Session()
        
        # Ищем пользователя по ID из токена
        user = session.get(User, payload["user_id"])
        session.close()
    
        return user  # Возвращаем объект пользователя
    
    except:
        # Если что-то пошло не так
        return None
    

def login_required(func) -> User:
    # @wraps(f) сохраняет оригинальное имя и документацию функции
    @wraps(func)
    def decorated_function(*args, **kwargs):
        '''Это "обёртка" вокруг оригинальной функции'''
        user = get_current_user()  # Получаем текущего пользователя
        if not user:
            return jsonify({"Ошибка": "Требуется аутентификация!"}), 401
        request.current_user = user  # Если пользователь есть - сохраняем его в request

        return func(*args, **kwargs) # Возвращаем оригинальную функцию
    return decorated_function  # Возвращаем обёртку


def check_announcement_owner(func):
    '''ДЕКОРАТОР: проверяет, что пользователь является владельцем объявлени'''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Сначала проверяем авторизацию
        user = get_current_user()
        if not user:
            return jsonify({"Ошибка": "Требуется аутентификация"}), 401
        
        # Получаем ID объявления из URL
        announcement_id = kwargs.get("announcement_id")
        if not announcement_id:
            return jsonify({"Ошибка": "Не указан ID объявления"}), 400
        
        # Ищем объявление в базе
        session = Session()
        announcement = session.get(Announcement, announcement_id)
        session.close()

        # Если объявления нет
        if not announcement:
            return jsonify({"Ошибка": "Объявление не найдено!"}), 404
        
        # Главная проверка: пользователь является владельцем?
        if announcement.user_id != user.id:
            return jsonify({"Ошибка": "Нет прав для выполнения операции!"}), 403
        
        # Если всё ок - сохраняем данные для использования в оригинальной функции
        request.current_user = user
        request.announcement = announcement
        
        return func(*args, **kwargs)
    return decorated_function



