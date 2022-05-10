from util import get_hash


class UserDao:
    database = None
    req = None

    def __init__(self, database, req):
        self.database = database
        self.req = req

    def insert_user(self):

        try:
            self.database.user.insert_one(
                dict(id=self.req['id_give'], pw=get_hash(self.req['pw_give']), nick=self.req['nickname_give'])
            )

        except Exception as exception:
            print(exception)
            return False

        return True

    def find_user(self, user):
        return self.database.user.find_one(user)
