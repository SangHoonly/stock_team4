import hashlib

import requests
from bs4 import BeautifulSoup

from config import config


def get_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def get_stock_price(stock):
    url = 'https://finance.naver.com/item/main.naver?code=' + stock['stock_code']
    data = requests.get(url, headers=config.Config.headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    return soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

def get_stock_name_by_code(code_name):
    url = 'https://finance.naver.com/'+ 'item/main.naver?code=' + code_name
    data = requests.get(url, headers=config.Config.headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    return soup.select_one('#middle > div.h_company > div.wrap_company > h2 > a').text
