from abc import ABC, abstractmethod


class Database(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get(
        self,
        time_start,
        time_end,
        record_type=None,
        peer_asn=None,
        collectors=None,
        countries=None,
        as_numbers=None,
        prefixes=None,
        as_paths=None
    ): 
        pass

    @abstractmethod
    def save(self, record):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class BGPDatabases:
    def __init__(self, database_conf=[]):
        self.__databases = []
        self.databases = database_conf
        self.start()

    @property
    def databases(self) -> list:
        """
        List of databases classes.

        A class is loaded if it inherits from `Database`
        and parameters are given in config.cfg"""
        return self.__databases

    @databases.setter
    def databases(self, config):
        if config is not None:
            for db in config:
                for db_class in Database.__subclasses__():
                    if db_class.name == db:
                        self.__databases.append(db_class(config[db]))

    def save(self, record):
        for db in self.__databases:
            db.save(record)

    def start(self):
        for db in self.__databases:
            db.start()

    def stop(self):
        for db in self.__databases:
            db.stop()
