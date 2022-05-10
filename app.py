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


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/user/main", methods=["GET"])
def user_main():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('user_main.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 게스트 메인
@app.route("/main", methods=["GET"])
def get():
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
        # print(name, price, up_down, percent, code)
        doc = {
            'stock_name': name,
            'stock_code': code
        }
        result.append(doc)
    stock = {'stock': result}
    print(stock)
    return render_template('guest_main.html', stock=stock)


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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        # 디코드가 되어있어서 .decode('utf-8') 없앰
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token, 'user_id': id_receive})
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


# 기존 코드 : 주식 DB 조회
@app.route("/stock", methods=["GET"])
def stock_get():
    stock_list = list(db.stock.find({}, {'_id': False}))
    return jsonify({'movies': stock_list})


@app.route("/sign_up", methods=["POST"])
def sign_up_post():
    user_name_give = request.form['user_name_give']
    id_give = request.form['id_give']
    password_give = request.form['password_give']

    if user_name_give and id_give and password_give:  ## 하나라도 비어있으면 False
        user_list = list(db.users.find({}, {'_id': False}))

        for user in user_list:
            if user_name_give in user['user_name']:
                return jsonify({'msg': '이름이 중복되었습니다.', 'state': False})
            if id_give in user['id']:
                return jsonify({'msg': '아이디가 중복되었습니다.', 'state': False})

        user_info = {
            'user_name': user_name_give,
            'id': id_give,
            'password': password_give,
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now()
        }
        db.users.insert_one(user_info)
        return jsonify({'msg': '회원가입 완료.', 'state': True})
    else:
        return jsonify({'msg': '모든 칸을 채워주세요.', 'state': False})


# 주식 DB 조회
@app.route("/my-stock-list", methods=["GET"])
def my_stock_list():
    # 수정하기 - /stock 참고
    return jsonify({'stock': 'result'})


# 유저의 관심종목 등록
@app.route("/user/stock/post", methods=["POST"])
def user_stock_post():
    code_receive = request.form['code_give']
    buy_price_receive = request.form['buy_price_give']
    buy_date_receive = request.form['buy_date_give']
    user_id_receive = request.form['user_id_give']
    url = 'https://finance.naver.com/'
    url += 'item/main.naver?code=' + code_receive
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    stock_name = soup.select_one('#middle > div.h_company > div.wrap_company > h2 > a').text
    # close = soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

    a = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    doc = {
        'user_id': user_id_receive,
        'stock_name': stock_name,
        'stock_code': code_receive,
        'buy_price': buy_price_receive,
        'buy_date': datetime.datetime.strptime(buy_date_receive, "%Y-%m-%d"),
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    }
    db.favorites.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


# 유저의 관심종목 불러오기
@app.route("/user/stock/post2", methods=["POST"])
def user_stock_get():
    user_id_receive = request.form['user_id_give']
    stock_list = list(db.favorites.find({'user_id': user_id_receive}, {'_id': False}))
    result = []
    for stock in stock_list:
        url = 'https://finance.naver.com/'
        url += 'item/main.naver?code=' + stock['stock_code']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')

        close = soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

        temp_doc = {
            'stock_name': stock['stock_name'],
            'stock_code': stock['stock_code'],
            'buy_price': stock['buy_price'],
            'close': close,
            'date_delta': str(datetime.datetime.now() - stock['buy_date']).split('day')[0]
        }
        result.append(temp_doc)

    return jsonify({'result': result})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
