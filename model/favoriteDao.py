class FavoriteDao:
    database = None

    def __init__(self, database):
        self.database = database

    def insert_favorite(self, doc):
        return self.database.favorites.insert_one(doc)

    def find_favorites(self, doc):
        return self.database.favorites.find(doc)

    def delete_favorite(self, doc):
        return self.database.favorites.delete_one(doc)

    def delete_favorite_many(self, doc):
        return self.database.favorites.delete_many(doc)
