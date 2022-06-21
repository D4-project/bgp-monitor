from Databases.database import Database
from clickhouse_driver import Client


class ClickHouseDB(Database):
    name = "clickhouse"

    def __init__(self, config):
        super().__init__()
        self.client = Client(host=config["host"])

    def get(
        self,
        as_numbers=None,
        prefixes=None,
        match_type="more",
        start_time=None,
        end_time=None,
        countries=None,
    ):
        res = self.client.execute_iter("SELECT * FROM bgp")
        return res

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
            ") ENGINE = MergeTree ORDER BY (begin, prefix, aspath)"
            "SETTINGS old_parts_lifetime=10"
        )


# client = clickhouse_driver
#           .Client(host="localhost", password="enes57", compression='lz4')

# client.execute('INSERT INTO bgprecords VALUES ',
# [{'begin': 1653383977, 'end': 0, 'type': 'A', 'peerasn':
# e.peer_asn, 'collector': e.collector, 'prefix': e._maybe_field('prefix'),
# 'aspath': "255126 15461 1564"}])
