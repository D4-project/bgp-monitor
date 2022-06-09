from Databases import database


class BGPClickHouse(database.Database):
    def __init__(self, client) -> None:
        super().__init__(client)

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

    def save(self, record):
        self.client.execute("INSERT INTO bgp VALUES ", "")

    def start(self):
        # client.execute('CREATE DATABASE BGP')
        # client.execute('DROP DATABASE BGP')
        self.client.execute("DROP TABLE IF EXISTS bgp")
        self.client.execute(
            "CREATE TABLE IF NOT EXISTS bgp ("
            "begin DateTime,"
            "type FixedString(1),"
            "peerasn Int32,"
            "collector String,"
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
