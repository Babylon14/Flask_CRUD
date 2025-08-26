from flask import Flask, jsonify
from flask.views import MethodView


app = Flask("app")

'''Приветствие на главной странице сайта'''
@app.route("/")
def cmd_hello():
    return "Добро пожаловать!"

class AnnouncementView(MethodView):

    def get(self, announcement_id):
        '''Получение объявлений'''
        pass

    def post(self):
        '''Создание объявления'''
        pass

    def patch(self, announcement_id):
        '''Изменение объявления'''
        pass

    def delete(self, announcement_id):
        '''Удаление объявления'''
        pass


announcement_view = AnnouncementView.as_view("announcement_View")

# Регистрация в маршрутизаторе метода POST
app.add_url_rule("/announcement/", view_func=announcement_view, methods=["POST"])

# Регистрация в маршрутизаторе методов GET, PATCH, DELETE
app.add_url_rule(
    "/announcement/<int:announcement_id>/",
    view_func=announcement_view, methods=["GET", "PATCH", "DELETE"])


if __name__ == "__main__":
    app.run(debug=True)


