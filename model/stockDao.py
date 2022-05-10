class StockDao:
    database = None
    _id = None
    name = None
    code = None
    created_at = None
    updated_at = None

    def __init__(self, database,
                 _id,
                 name,
                 code,
                 created_at,
                 updated_at):

        self.name = name
        self._id = _id
        self.code = code
        self.created_at = created_at
        self.updated_at = updated_at
        self.database = database
