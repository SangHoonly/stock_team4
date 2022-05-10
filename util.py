import hashlib


def get_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

# 내일의 내가 하는걸로
def jwt_auth():
    pass
