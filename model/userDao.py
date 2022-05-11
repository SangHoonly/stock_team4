class UserDao:
    database = None

    def __init__(self, database):
        self.database = database

    def insert_user(self, doc):
        return self.database.user.insert_one(doc)


    def find_user(self, user):
        return self.database.user.find_one(user)

    def delete_user(self, user):
        return self.database.user.delete_one(user)
