import datetime

import jwt
import requests
from bs4 import BeautifulSoup
from flask import render_template, jsonify, request, redirect, url_for
from config import config
from util import get_hash


def create_endpoints(app, service):
    JWT_SECRET_KEY = config.JWT_config.SECRET_KEY

    # Home
    @app.route("/", methods=["GET"])
    def home():
        info = service.stock.get_crawling()
        return render_template('index.html', stock=info)

    # Rendering Log in Page
    @app.route("/login", methods=["GET"])
    def login():
        return render_template('login.html')

    # Rendering sign up Page
    @app.route('/sign_up')
    def sign_up():
        return render_template('sign_up.html')

    # Rendering my_page Page
    @app.route('/my_page')
    def my_page():
        token_receive = request.cookies.get('mytoken')

        try:
            payload = jwt.decode(token_receive, JWT_SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

        result = service.user.find_user({"id": payload['id']})
        return render_template('my_page.html', id=result["id"], nick=result["nick"])

    # mypage password check
    @app.route('/api/password-check', methods=['POST'])
    def password_check():
        req = request.form

        pw_hash = get_hash(req['pw_give'])
        user = {'id': req['id_give'], 'pw': pw_hash}

        if service.user.find_user(user):
            return jsonify({'result': 'success', 'msg': '비밀번호 일치'})
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다.'})

    # 회원탈퇴
    @app.route('/api/secession', methods=['DELETE'])
    def secession_check():
        req = request.form
        pw_hash = get_hash(req['pw_give'])
        user = {'id': req['id_give'], 'pw': pw_hash}
        if service.user.delete_user(user):
            return jsonify({'result': 'success', 'msg': '탈퇴 완료'})
        return jsonify({'result': 'fail', 'msg': '탈퇴 실패'})

    # stock crawling
    @app.route("/stock/crawling", methods=["GET"])
    def stock_get_crawl():
        return jsonify({'stock': service.stock.get_crawling()})

    # register single user
    @app.route('/api/register', methods=['POST'])
    def api_register():
        req = request.form
        doc = dict(id=req['id_give'], pw=get_hash(req['pw_give']), nick=req['nickname_give'])

        return jsonify(dict(result=service.user.insert_user(doc)))

    # 아이디 중복체크
    @app.route('/api/check-dup', methods=['POST'])
    def api_check_dup():
        req = request.form
        doc = dict(id=req['userid_give'])
        exists = bool(service.user.find_user(doc))
        return jsonify({'result': 'success', 'exists': exists})

    # 로그인된 user main page
    @app.route("/user/main", methods=["GET"])
    def user_main():
        token_receive = request.cookies.get('mytoken')

        try:
            payload = jwt.decode(token_receive, JWT_SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

        return render_template('user_main.html', nickname=service.user.find_user({"id": payload['id']})["nick"])

    @app.route('/api/login', methods=['POST'])
    def api_login():
        req = request.form

        pw_hash = get_hash(req['pw_give'])
        user = {'id': req['id_give'], 'pw': pw_hash}

        if service.user.find_user(user):
            payload = {
                'id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
            }
            token = jwt.encode(payload, config.JWT_config.SECRET_KEY, algorithm='HS256')

            return jsonify({'result': 'success', 'token': token, 'user_id': user['id']})

        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

    @app.route('/api/nick', methods=['GET'])
    def api_valid():
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, JWT_SECRET_KEY, algorithms=['HS256'])
            userinfo = service.user.find_user({'id': payload['id']}, {'_id': 0})

            return jsonify({'result': 'success', 'nickname': userinfo['nick']})
        except jwt.ExpiredSignatureError:

            return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
        except jwt.exceptions.DecodeError:
            return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

    # 유저의 관심종목 불러오기
    @app.route("/favorites", methods=["POST"])
    def get_favorites():

        user_id_receive = request.form['user_id_give']

        doc = ({'user_id': user_id_receive}, {'_id': False})

        stock_list = list(service.favorite.find_favorites(doc))

        result = []
        for stock in stock_list:
            url = 'https://finance.naver.com/'
            url += 'item/main.naver?code=' + stock['stock_code']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
            data = requests.get(url, headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')

            close = soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

            date_delta = str(datetime.datetime.now() - stock['buy_date']).split('day')
            if len(date_delta) == 1:
                date_delta = 1
            elif len(date_delta) == 2:
                date_delta = int(date_delta[0]) + 1
            else:
                print("error in date_delta")

            temp_doc = {
                'stock_name': stock['stock_name'],
                'stock_code': stock['stock_code'],
                'buy_price': stock['buy_price'],
                'close': close,
                'date_delta': date_delta,
                'buy_date': str(stock['buy_date'])[:10]
            }
            result.append(temp_doc)

        return jsonify({'result': result})

    # 유저의 관심종목 등록
    @app.route("/favorite", methods=["POST"])
    def insert_favorite():
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
        service.favorite.insert_favorite(doc)

        return jsonify({'msg': '저장 완료!'})

    return
