import requests
from bs4 import BeautifulSoup

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://finance.naver.com/',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

stocks = soup.select('#_topItems1 > tr')
# #_topItems1 > tr:nth-child(1) > td:nth-child(3)
# #_topItems1 > tr:nth-child(1) > td:nth-child(4)
# print(stocks)

for stock in stocks:
    name = stock.select_one('th > a').text
    price = stock.select_one('td').text
    up_down = stock.select_one('td:nth-child(3)').text
    percent = stock.select_one('td:nth-child(4)').text
    print(name, price, up_down, percent)
