from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.zu2cz.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')

  
@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route("/stock", methods=["POST"])
def stock_post():
    code_receive = request.form['code_give']
    url = 'https://finance.naver.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # content > div.section.section_chart.inner_sub > cq-context > div.ciq-chart-area

    # 여기에 코딩을 해서 meta tag를 먼저 가져와보겠습니다.

    exday_down = soup.select('#chart_area > div.rate_info > div > p.no_exday > em:nth-child(2) > span.ico.down')
    exday_up = soup.select('#chart_area > div.rate_info > div > p.no_exday > em:nth-child(2) > span.ico.up')
    is_up = True

    if exday_down:
        is_up = False
    elif exday_up:
        is_up = True
    else:
        print("error in 'is_up'")

    stock_name = soup.select_one('#middle > div.h_company > div.wrap_company > h2 > a').text

    close = soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

    gap_close = []
    if is_up:
        gap_close.append(
            soup.select_one("#chart_area > div.rate_info > div > p.no_exday > em:nth-child(2) > span.blind").text)
        gap_close.append(
            soup.select_one("#chart_area > div.rate_info > div > p.no_exday > em:nth-child(4) > span.blind").text)
    else:
        gap_close.append(
            '-' + soup.select_one("#chart_area > div.rate_info > div > p.no_exday > em:nth-child(2) > span.blind").text)
        gap_close.append(
            '-' + soup.select_one("#chart_area > div.rate_info > div > p.no_exday > em:nth-child(4) > span.blind").text)

    doc = {
        'stock_name': stock_name,
        'stock_code': code_receive,
        'close': close,
        'gclose1': gap_close[0],
        'gclose2': gap_close[1],
        'is_up': is_up
    }

    return jsonify({'msg': '저장 완료!'})


@app.route("/stock", methods=["GET"])
def stock_get():
    stock_list = list(db.stock.find({}, {'_id': False}))
    return jsonify({'movies': stock_list})


@app.route("/stock/crawling", methods=["GET"])
def stock_get_crawl():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://finance.naver.com/', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # #_topItems1 > tr:nth-child(1) > td:nth-child(3)
    # #_topItems1 > tr:nth-child(1) > td:nth-child(4)
    # print(stocks)
    # _topItems1 > tr:nth-child(1) > th > a
    stocks = soup.select('#_topItems1 > tr')
    result = []
    for stock in stocks:
        name = stock.select_one('th > a').text
        price = stock.select_one('td').text
        up_down = stock.select_one('td:nth-child(3)').text
        percent = stock.select_one('td:nth-child(4)').text
        code = stock.select_one('th > a')['href'].split('code=')[1]
        #print(name, price, up_down, percent, code)
        doc = {
            'stock_name': name,
            'stock_code': code
        }
        result.append(doc)

    return jsonify({'stock': result})


@app.route("/main", methods=["GET"])
def get():
    return render_template('guest_main.html')


@app.route("/user/main", methods=["GET"])
def user_get():
    return render_template('user_main.html')


@app.route("/sign_up", methods=["POST"])
def sign_up_post():
    user_name_give = request.form['user_name_give']
    id_give = request.form['id_give']
    password_give = request.form['password_give']

    if user_name_give and id_give and password_give: ## 하나라도 비어있으면 False
        user_list = list(db.users.find({}, {'_id': False}))

        for user in user_list:
            if user_name_give in user['user_name']:
                return jsonify({'msg': '이름이 중복되었습니다.', 'state': False})
            if id_give in user['id']:
                return jsonify({'msg': '아이디가 중복되었습니다.', 'state': False})

        user_info = {
            'user_name':user_name_give,
            'id':id_give,
            'password':password_give,
        }
        db.users.insert_one(user_info)
        return jsonify({'msg':'회원가입 완료.', 'state': True})
    else:
        return jsonify({'msg':'모든 칸을 채워주세요.', 'state': False})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
