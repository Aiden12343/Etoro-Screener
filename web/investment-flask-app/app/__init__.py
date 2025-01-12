# filepath: /c:/Users/aiden/OneDrive/Documents/Desktop/Stock Python Scripts/AutomatingEtoroPosts/investment-flask-app/app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        from . import routes

    return app