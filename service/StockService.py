import requests
from bs4 import BeautifulSoup

from config.config import Config


class StockService:
    stock_dao = None

    def __init__(self, stock_dao):
        self.stock_dao = stock_dao

    def get_crawling(self):
        data = requests.get('https://finance.naver.com/', headers=Config.headers)
        stocks = BeautifulSoup(data.text, 'html.parser').select('#_topItems1 > tr')

        return [{'stock_name': stock.select_one('th > a').text,
                 'stock_code': stock.select_one('th > a')['href'].split("code=")[1]}\
                for stock in stocks]