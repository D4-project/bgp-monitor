import collections
import threading
from Databases.database import Database
from clickhouse_driver import Client
from queue import Queue


class ClickHouseDB(Database):
    name = "clickhouse"

    def __init__(self, config):
        """
        Args:
            config (dict): Format : {"host":"127.0.0.1", "port":9000, "batch_size":15000}
        """
        super().__init__()
        self.started = False
        self.BATCH_SIZE = int(config["batch_size"]) if "batch_size" in config else 15000
        self.queue = Queue()
        self.client = Client(
            host=config["host"], port=int(config["port"]), compression="lz4"
        )
        self.client.execute(
            "CREATE TABLE IF NOT EXISTS bgp ("
            "time DateTime,"
            "type FixedString(1),"
            "peer Int32,"
            "collector String,"
            "project String,"
            "country String,"
            "source String,"
            "prefix String,"
            "path String"
            ") ENGINE = MergeTree ORDER BY (time, prefix, path)"
            "SETTINGS old_parts_lifetime=10"
        )
        print("Clickhouse : Generated BGP table :D")

    def start(self):
        """
        Create bgp table
        (time DateTime, type, peer, collector, country, source, prefix, path)
        Start thread for batch inserts
        """
        # self.client.execute("DROP TABLE IF EXISTS bgp")
        self.started = True
        threading.Thread(
            target=self.insert_batches, daemon=True, name="BGP monitor - clickhouse"
        ).start()

    def stop(self):
        """Stop inserts"""
        if self.started:
            self.started = False

    ###############
    #   INSERTS   #
    ###############

    def save(self, data):
        """Input data in queue for processing

        Args:
            data (BGPElem): bgp element to save
        """
        self.queue.put(data)

    def get_data(self):
        """Retrieve data for inserts
        Yields:
            dict: Data to insert
        """
        for idx in range(self.BATCH_SIZE):
            rec = self.queue.get()
            yield {
                "time": int(rec["time"]),
                "type": rec["type"],
                "peer": rec["peer_asn"],
                "collector": rec["collector"],
                "country": rec["country_code"] or "",
                "source": rec["source"] or "",
                "prefix": rec["prefix"],
                "path": rec.get("as-path", ""),
                "project": rec["project"],
            }
            if self.queue.qsize() == 0 and not self.started:
                print("Clickhouse : Inserting last batch")
                return

    def insert_batches(self):
        """
        Insert BATCH_SIZE(15000 lines) batches
        https://clickhouse.com/docs/en/about-us/performance/"""
        while self.started:
            self.client.execute("INSERT INTO bgp VALUES ", self.get_data())

    ##############
    #   GETTER   #
    ##############

    var_names = {
        "time_start": "time_start",
        "time_end": "time_end",
        "record_type": "type",
        "peer_asn": "peer",
        "collectors": "collector",
        "countries": "country",
        "as_numbers": "source",
        "prefixes": "prefix",
        "as_paths": "path",
    }
    # Used in `ClickHouseDB.get` function as arg_name:db_column_name

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
