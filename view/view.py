import jwt
from flask import render_template, jsonify, request, redirect, url_for
from config import config


def create_endpoints(app, service):
    JWT_SECRET_KEY = config.JWT_config.SECRET_KEY

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

    # stock crawling
    @app.route("/stock/crawling", methods=["GET"])
    def stock_get_crawl():
        return jsonify({'stock': service.stock.get_crawling()})

    # register single user
    @app.route('/api/register', methods=['POST'])
    def api_register():
        return jsonify(dict(result=eval(service.user.insert_user())))


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
        return service.user.login()

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
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


    return
