from Databases.database import Database

class QuestDB(Database):
    name = "quest"
    def __init__(self, config= None):
        super().__init__(config)

    def get(
        self,
        as_numbers=None,
        prefixes=None,
        match_type="more",
        start_time=None,
        end_time=None,
        countries=None,
    ): pass

    def save(self, record):
        pass
