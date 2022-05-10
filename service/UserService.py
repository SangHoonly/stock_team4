import datetime

import jwt
from flask import request, jsonify

from config import config
from util import get_hash


class UserService:
    user_dao = None
    req = None

    def __init__(self, user_dao, req):
        self.user_dao = user_dao
        self.req = req

    def login(self):
        pw_hash = get_hash(self.req['pw_give'])
        user = {'id': self.req['id_give'], 'pw': pw_hash}

        if self.user_dao.find_user(user):
            payload = {
                'id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
            }
            token = jwt.encode(payload, config.JWT_config.SECRET_KEY, algorithm='HS256')

            return jsonify({'result': 'success', 'token': token, 'user_id': user['id']})

        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
