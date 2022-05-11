class Service:
    stock = None
    user = None
    favorite = None

    def __init__(self, stock, user, favorite):
        self.stock = stock
        self.user = user
        self.favorite = favorite
