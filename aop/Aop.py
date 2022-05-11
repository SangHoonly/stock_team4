import jwt
from flask import request, redirect, url_for

from config import config


def login_required(f):
    JWT_SECRET_KEY = config.JWT_config.SECRET_KEY

    def wrapper():
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, JWT_SECRET_KEY, algorithms=['HS256'])
            return f(payload)

        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="expired"))

        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="wrong"))


    wrapper.__name__ = f.__name__

    return wrapper

