from datetime import datetime

from util import get_stock_price


class FavoriteService:
    favorite_dao = None

    def __init__(self, favorite_dao):
        self.favorite_dao = favorite_dao

    def insert_favorite(self, doc):
        return self.favorite_dao.insert_favorite(doc)

    def find_favorites(self, doc):
        favorite_stocks = self.favorite_dao.find_favorites(doc)

        return [{
            'stock_name': stock['stock_name'],
            'stock_code': stock['stock_code'],
            'buy_price': stock['buy_price'],
            'close': get_stock_price(stock),
            'date_delta': (datetime.now() - stock['buy_date']).days + 1,
            'buy_date': str(stock['buy_date'])[:10],
            '_id':str(stock['_id'])
        } for stock in favorite_stocks]

    def delete_favorite(self, doc):
        return self.favorite_dao.delete_favorite(doc)

    def delete_favorite_many(self, doc):
        return self.favorite_dao.delete_favorite_many(doc)
