import abc


class Database(abc.ABC):
    def __init__(self, client) -> None:
        """ """
        pass

    @abc.abstractmethod
    def get(
        self,
        as_numbers,
        prefixes,
        match_type,
        start_time,
        end_time,
        countries=None,
    ):
        pass

    @abc.abstractmethod
    def save(self, record):
        pass
