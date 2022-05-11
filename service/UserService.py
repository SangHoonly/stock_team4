class UserService:
    user_dao = None
    req = None

    def __init__(self, user_dao):
        self.user_dao = user_dao

    def insert_user(self, doc):
        return self.user_dao.insert_user(doc)

    def find_user(self, doc):
        return self.user_dao.find_user(doc)

    def delete_user(self, doc):
        return self.user_dao.delete_user(doc)
