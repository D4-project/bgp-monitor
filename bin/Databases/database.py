from abc import ABC, abstractmethod

class Database(ABC):
    def __init__(self, config=None):
        """ """
        self.client = config

    @abstractmethod
    def get(
        self,
        as_numbers=None,
        prefixes=None,
        match_type="more",
        start_time=None,
        end_time=None,
        countries=None,
    ): pass

    @abstractmethod
    def save(self, record):
        pass
