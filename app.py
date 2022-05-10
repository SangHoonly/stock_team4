from flask import Flask, request

from config.config import Config
from model.stockDao import StockDao
from model.userDao import UserDao
from service.StockService import StockService
from service.UserService import UserService
from service.service import Service
from view.view import create_endpoints



def create_app():
    app = Flask(__name__)
    database = Config.db_config
    req = request.form


    stock_dao = StockDao(database)
    user_dao = UserDao(database, req)

    service = Service
    service.stock = StockService(stock_dao)
    service.user = UserService(user_dao)

    create_endpoints(app, service)

    return app
