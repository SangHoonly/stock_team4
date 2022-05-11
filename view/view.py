from datetime import datetime, timedelta

import jwt
from flask import render_template, jsonify, request

from aop.Aop import login_required
from config import config
from util import get_hash, get_stock_name_by_code


def create_endpoints(app, service):
    req = request.form

    def is_correct_password():
        return bool(service.user.find_user({'id': req['id_give'], 'pw': get_hash(req['pw_give'])}))

    # Home
    @app.route("/", methods=["GET"])
    def home():
        return render_template('index.html')

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
    @login_required
    def my_page(payload):
        result = service.user.find_user({"id": payload['id']})

        return render_template('my_page.html', id=result["id"], nick=result["nick"])


    # mypage password check
    @app.route('/api/password-check', methods=['POST'])
    def password_check():
        return jsonify({'result': 'success', 'msg': '비밀번호 일치'}) \
            if is_correct_password() \
            else jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다.'})


    # 회원탈퇴
    @app.route('/api/secession', methods=['POST'])
    def secession_check():
        if is_correct_password():
            service.user.delete_user({'id': req['id_give'], 'pw': get_hash(req['pw_give'])})
            return jsonify({'result': 'success', 'msg': '탈퇴 완료'})

        return jsonify({'result': 'fail', 'msg': '탈퇴 실패'})

    # stock crawling
    @app.route("/stock/crawling", methods=["GET"])
    def stock_get_crawl():
        return jsonify({'stock': service.stock.get_crawling()})

    # register single user
    @app.route('/api/register', methods=['POST'])
    def api_register():
        doc = dict(id=req['id_give'], pw=get_hash(req['pw_give']), nick=req['nickname_give'])

        return jsonify(dict(result=bool(service.user.insert_user(doc))))

    # 아이디 중복체크
    @app.route('/api/check-dup', methods=['POST'])
    def api_check_dup():
        doc = dict(id=req['userid_give'])

        return jsonify({'result': 'success', 'exists': bool(service.user.find_user(doc))})


    # 로그인된 user main page
    @app.route("/user/main", methods=["GET"])
    @login_required
    def user_main(payload):
        return render_template('user_main.html', nickname=service.user.find_user({"id": payload['id']})["nick"])


    @app.route('/api/login', methods=['POST'])
    def api_login():
        user_id = req['id_give']

        if is_correct_password():
            payload = {
                'id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
            }
            token = jwt.encode(payload, config.JWT_config.SECRET_KEY, algorithm='HS256')

            return jsonify({'result': 'success', 'token': token, 'user_id': user_id})

        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


    # 유저의 관심종목 불러오기
    @app.route("/favorites", methods=["POST"])
    def get_favorites():
        doc = {'user_id': req['user_id_give']}
        favorite_stocks = service.favorite.find_favorites(doc)

        return jsonify({'result': favorite_stocks})


    # 유저의 관심종목 등록
    @app.route("/favorite", methods=["POST"])
    def insert_favorite():
        doc = {
            'user_id': req['user_id_give'],
            'stock_name': get_stock_name_by_code(req['code_give']),
            'stock_code': req['code_give'],
            'buy_price': req['buy_price_give'],
            'buy_date': datetime.strptime(req['buy_date_give'], "%Y-%m-%d"),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        service.favorite.insert_favorite(doc)

        return jsonify({'msg': '저장 완료!'})

    return
