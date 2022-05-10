from flask import Flask, render_template, jsonify, request, session, redirect, url_for

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.zu2cz.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index2.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        # 디코드가 되어있어서 .decode('utf-8') 없앰
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


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



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
