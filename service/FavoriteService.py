class FavoriteService:
    favorite_dao = None

    def __init__(self, favorite_dao):
        self.favorite_dao = favorite_dao

    def insert_favorite(self, doc):
        return self.favorite_dao.insert_favorite(doc)

    def find_favorites(self, doc):
        return self.favorite_dao.find_favorites(doc)

    def delete_favorite(self, doc):
        return self.favorite_dao.delete_favorite(doc)

    def delete_favorite_many(self, doc):
        return self.favorite_dao.delete_favorite_many(doc)