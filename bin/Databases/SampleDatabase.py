from Databases.database import Database


class SampleDatabase(Database):

    name = "SampleDatabase"
    """This variable is used for configuration file

    You must specify it in config to load an instance"""

    def __init__(self, config):
        """config contains parameters given in etc/config.cfg file"""
        super().__init__()

    def start(self):
        """Create Table or anything else"""
        pass

    def stop(self):
        pass

    ###############
    #   INSERTS   #
    ###############

    def save(self, record):
        """All records are sent one by one using this function"""
        pass

    ##############
    #   GETTER   #
    ##############
    # The followings aren't used

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
        as_paths=None,
    ):
        """
        Retrieve data and return it as iterable

        See `Database.get()`
        """
        pass
