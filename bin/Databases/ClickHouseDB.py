import collections
from Databases.database import Database
from clickhouse_driver import Client


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
        super().__init__()
        self.client = Client(host=config["host"], port=int(config["port"]))

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

    def save(self, record):
        self.client.execute(
            "INSERT INTO bgp VALUES ",
            [
                {
                    "time": int(record.time),
                    "type": record.type,
                    "peerasn": record.peer_asn,
                    "collector": record.collector,
                    "country": record.country_code,
                    "sourceasn": record.source,
                    "prefix": record._maybe_field("prefix") or "",
                    "aspath": record._maybe_field("as-path") or "",
                }
            ],
        )

    def start(self):
        # client.execute('CREATE DATABASE BGP')
        # client.execute('DROP DATABASE BGP')
        # self.client.execute("DROP TABLE IF EXISTS bgp")
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
        print("Created table")

    def stop(self):
        pass


# client = clickhouse_driver
#           .Client(host="localhost", password="enes57", compression='lz4')

# client.execute('INSERT INTO bgprecords VALUES ',
# [{'begin': 1653383977, 'end': 0, 'type': 'A', 'peerasn':
# e.peer_asn, 'collector': e.collector, 'prefix': e._maybe_field('prefix'),
# 'aspath': "255126 15461 1564"}])
