from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import Session, Announcement, User
from auth import login_required, check_announcement_owner, generate_token
from errors import HttpError
from schema import CreateAnnouncementRequest, UpdateAnnouncementRequest, validate


app = Flask("app")

'''Декоратор, открывает сессию'''
@app.before_request
def before_request():
    session = Session()
    request.session = session

'''Декоратор, закрывает сессию'''
@app.after_request
def after_request(response):
    request.session.close()
    return response

'''Декоратор, обработчик ошибок'''
@app.errorhandler(HttpError)
def error_handler(err: HttpError):
    http_response = jsonify({"Ошибка": err.message})
    http_response.status_code = err.status_code
    return http_response

'''Функция по получению объявления по id'''
def get_announcement_by_id(announcement_id: int) -> Announcement:
    announcement = request.session.get(Announcement, announcement_id)
    if announcement is None:
        raise HttpError(status_code=404, message="Объявление не найдено!")
    return announcement

'''Функция по созданию объявления, добавлению в сессию и коммиту'''
def add_announcement(announcement: Announcement) -> Announcement:
    try:
        request.session.add(announcement)
        request.session.commit()
    except IntegrityError:
        raise HttpError(status_code=409, message="Такое объявление уже существует!")


'''Приветствие на главной странице сайта'''
@app.route("/")
def cmd_hello():
    return "Добро пожаловать на сайт Объявлений!"


class UserView(MethodView):
    '''View-класс для работы с пользователями'''
    
    def post(self):
        '''Регистрация пользователя'''
        json_data = request.json

        if not json_data.get("email") or not json_data.get("password"):
            raise HttpError(status_code=404, message="Email и пароль обязательны!")

        session = Session()
        try:
            user = User(email=json_data["email"])
            user.set_password(json_data["password"])
            session.add(user)
            session.commit()
            token = generate_token(user.id)
            result = {
                "user": user.json_format,
                "token": token
            }
            session.close()
            return jsonify(result), 201
        except IntegrityError:
            session.rollback()
            session.close()
            raise HttpError(409, "Пользователь с таким email уже существует")
        except Exception as err:
            session.rollback()
            session.close()
            raise HttpError(500, str(err))


class AuthView(MethodView):
    '''View-класс для аутентификации'''
    
    def post(self):
        '''Вход пользователя'''
        json_data = request.json
        
        if not json_data.get("email") or not json_data.get("password"):
            raise HttpError(status_code=400, message="Email и пароль обязательны!")
        
        session = Session()
        user = session.query(User).filter(User.email == json_data["email"]).first()
        session.close()
        
        if not user or not user.check_password(json_data["password"]):
            raise HttpError(status_code=401, message="Неверный email или пароль")
        
        token = generate_token(user.id)
        return jsonify({
            "user": user.json_format,
            "token": token
        })
    

class AnnouncementView(MethodView):
    '''View-класс по обработке методов CRUD'''

    def get(self, announcement_id: int):
        '''Получение объявлений'''
        announcement = get_announcement_by_id(announcement_id)
        return jsonify(announcement.json_format)
    
    @login_required
    def post(self):
        '''Создание объявления - только для авторизованных'''
        json_data = validate(CreateAnnouncementRequest, request.json)
        announcement = Announcement(
            headline=json_data["headline"],
            description=json_data["description"],
            owner=json_data["owner"],
            user_id=request.current_user.id
        )
        add_announcement(announcement)
        return jsonify(announcement.id_json)

    @check_announcement_owner
    def patch(self, announcement_id: int):
        '''Изменение объявления - только для владельца'''
        validated_data = validate(UpdateAnnouncementRequest, request.json)
        
        announcement = request.announcement
        for field, value in validated_data.items():
            setattr(announcement, field, value)
    
        add_announcement(announcement)
        return jsonify(announcement.id_json)

    @check_announcement_owner
    def delete(self, announcement_id: int):
        '''Удаление объявления - только для владельца'''
        announcement = request.announcement
        request.session.delete(announcement)
        request.session.commit()
        return jsonify({"Ответ": "Объявление успешно удалено!"})


app.add_url_rule("/register/", view_func=UserView.as_view("user_view"), methods=["POST"])
app.add_url_rule("/login/", view_func=AuthView.as_view("auth_view"), methods=["POST"])

announcement_view = AnnouncementView.as_view("announcement_View")
app.add_url_rule("/announcement/", view_func=announcement_view, methods=["POST"])
app.add_url_rule(
    "/announcement/<int:announcement_id>",
    view_func=announcement_view, methods=["GET", "PATCH", "DELETE"])


if __name__ == "__main__":
    app.run(debug=True)


