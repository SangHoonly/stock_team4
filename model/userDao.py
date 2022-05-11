from util import get_hash


class UserDao:
    database = None

    def __init__(self, database):
        self.database = database

    def insert_user(self, doc):

        try:
            self.database.user.insert_one(doc)

        except Exception as exception:
            print(exception)
            return False

        return True

    def find_user(self, user):
        return self.database.user.find_one(user)

    def delete_user(self, user):
        return self.database.user.delete_one(user)

    # def find_all_user(self, user):
    #     return self.database.user.find(user)
