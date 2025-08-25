from flask import Flask, jsonify


app = Flask("app")

'''Приветствие на главной странице сайта'''
@app.route("/")
def cmd_hello():
    return "Добро пожаловать!"


if __name__ == "__main__":
    app.run(debug=True)


