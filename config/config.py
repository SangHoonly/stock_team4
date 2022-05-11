import pymongo

class Config:
    db_config = pymongo.MongoClient(
        'mongodb+srv://test:sparta@cluster0.zu2cz.mongodb.net/Cluster0?retryWrites=true&w=majority'
    ).dbsparta

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


class JWT_config:
    SECRET_KEY = 'SPARTA'
