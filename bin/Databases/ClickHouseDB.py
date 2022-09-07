import collections
import threading
from Databases.database import Database
from clickhouse_driver import Client
from queue import Queue


class ClickHouseDB(Database):
    name = "clickhouse"

    var_names = {
        "time_start": "time_start",
        "time_end": "time_end",
        "record_type": "type",
        "peer_asn": "peerasn",
        "collectors": "collector",
        "countries": "country",
        "as_numbers": "sourceasn",
        "prefixes": "prefix",
        "as_paths": "aspath",
    }
    
    def __init__(self, config):
        """_summary_

        Args:
            config (dict): Format : {"host":"127.0.0.1", "port":9000}
        """
        super().__init__()
        self.BATCH_SIZE = int(config["batch_size"]) if "batch_size" in config else 10000
        self.client = Client(host=config["host"], port=int(config["port"]), compression="lz4")
        self.queue = Queue()
        self.started = False

    def start(self):
        """
        Create bgp table (time DateTime, type, peerasn, collector, country, sourceasn, prefix, aspath)
        
        Start thread for batch inserts
        """
        # self.client.execute("DROP TABLE IF EXISTS bgp")
        self.started = True
        self.client.execute(
            "CREATE TABLE IF NOT EXISTS bgp ("
            "time DateTime,"
            "type FixedString(1),"
            "peerasn Int32,"
            "collector String,"
            "country String,"
            "sourceasn String,"
            "prefix String,"
            "aspath String"
            ") ENGINE = MergeTree ORDER BY (time, prefix, aspath)"
            "SETTINGS old_parts_lifetime=10"
        )
        print("Clickhouse : Generated BGP table :D")
        threading.Thread(
            target=self.insert_batches, daemon=True, name="BGP monitor - clickhouse"
        ).start()

    def stop(self):
        """Stop inserts"""
        if self.started:
            self.started = False
            print("Clickhouse : Inserting last batch")
            # self.client.execute("INSERT INTO bgp VALUES ", self.get_data())



    ### INSERT ###

    def save(self, data):
        """Input data in queue for processing

        Args:
            data (BGPElem): bgp element to save
        """
        self.queue.put(data)

    def get_data(self):
        """Retrieve data for 

        Yields:
            dict: Data to insert
            
        """
        for idx in range(self.BATCH_SIZE):
            rec = self.queue.get()
            yield {
                    "time": int(rec.time),
                    "type": rec.type,
                    "peerasn": rec.peer_asn,
                    "collector": rec.collector or "",
                    "country": rec.country_code or "",
                    "sourceasn": rec.source or "",
                    "prefix": rec.prefix or "",
                    "aspath": rec["path"] or "",
                }
            if self.queue.qsize() == 0 and not self.started: # Return 
                return

    def insert_batches(self):
        """
        Insert BATCH_SIZE(15000 lines) batches
        
        https://clickhouse.com/docs/en/about-us/performance/"""
        while self.started:
            self.client.execute("INSERT INTO bgp VALUES ", self.get_data())


    ### GET ###

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
        query = "SELECT * FROM bgp WHERE"
        params = {key: value for key, value in locals() if value is not None}

        if len(params) > 0:
            for k, v in params:
                query += (
                    f" %({ClickHouseDB.var_names[k]}) "
                    + ("IN " if isinstance(v, collections.Sequence) else "== ")
                    + f"%({k}) and"
                )
            query += query.rsplit(" ", 1)[0]
        return self.client.execute_iter(query, params)
