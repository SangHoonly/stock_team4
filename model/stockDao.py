class StockDao:
    database = None

    def __init__(self, database):
        self.database = database
