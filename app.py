from flask import Flask

from config.config import Config
from model.favoriteDao import FavoriteDao
from model.stockDao import StockDao
from model.userDao import UserDao
from service.FavoriteService import FavoriteService
from service.StockService import StockService
from service.UserService import UserService
from service.service import Service
from view.view import create_endpoints


def create_app():
    app = Flask(__name__)
    database = Config.db_config

    stock_dao = StockDao(database)
    user_dao = UserDao(database)
    favorite_dao = FavoriteDao(database)

    service = Service
    service.stock = StockService(stock_dao)
    service.user = UserService(user_dao)
    service.favorite = FavoriteService(favorite_dao)

    create_endpoints(app, service)

    return app


if __name__ == '__main__':
    create_app().run('0.0.0.0', port=5000, debug=True)
