from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import Session, Announcement
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


class AnnouncementView(MethodView):
    '''View-класс по обработке методов CRUD'''

    def get(self, announcement_id: int):
        '''Получение объявлений'''
        announcement = get_announcement_by_id(announcement_id)
        return jsonify(announcement.json_format)
    

    def post(self):
        '''Создание объявления'''
        json_data = validate(CreateAnnouncementRequest, request.json)
        announcement = Announcement(
            headline=json_data["headline"],
            description=json_data["description"],
            owner=json_data["owner"]
        )
        add_announcement(announcement)
        return jsonify(announcement.id_json)


    def patch(self, announcement_id: int):
        '''Изменение объявления'''
        json_data = validate(UpdateAnnouncementRequest, request.json)
        announcement = get_announcement_by_id(announcement_id)

        if "headline" in json_data:
            announcement.headline = json_data["headline"]
        if "description" in json_data:
            announcement.description = json_data["description"]
        if "owner" in json_data:
            announcement.owner = json_data["owner"]

        add_announcement(announcement)
        return jsonify(announcement.id_json)


    def delete(self, announcement_id: int):
        '''Удаление объявления'''
        announcement = get_announcement_by_id(announcement_id)
        request.session.delete(announcement)
        request.session.commit()
        return jsonify({"Ответ": "Объявление успешно удалено!"})


announcement_view = AnnouncementView.as_view("announcement_View")

# Регистрация в маршрутизаторе метода POST
app.add_url_rule("/announcement/", view_func=announcement_view, methods=["POST"])

# Регистрация в маршрутизаторе методов GET, PATCH, DELETE
app.add_url_rule(
    "/announcement/<int:announcement_id>",
    view_func=announcement_view, methods=["GET", "PATCH", "DELETE"])


if __name__ == "__main__":
    app.run(debug=True)


