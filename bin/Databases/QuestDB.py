import collections
from Databases.database import Database
import socket
import psycopg2


class QuestDB(Database):
    name = "quest"

    def __init__(self, config):
        super().__init__()
        # For UDP, change socket.SOCK_STREAM to socket.SOCK_DGRAM
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Required args for line protocol and postgre connection
        self.conf = {
            "host": config["host"],
            "tcp_port": int(config["tcp_port"]),
            "pg_port": int(config["pg_port"]),
        }
        self.connection = None

    def start(self):
        """Connect to server using etc/config.cfg file"""
        self.sock.connect((self.conf["host"], self.conf["tcp_port"]))
        self.connection = psycopg2.connect(
            host=self.conf["host"],
            port=self.conf["pg_port"],
            user="admin",
            password="quest",
            database="qdb",
        )

    def stop(self):
        """Close connection to server"""
        self.sock.close()
        if self.connection:
            self.connection.close()
            print("PostgreSQL connection is closed")

    ###############
    #   INSERTS   #
    ###############

    def save(self, record):
        """Save bgp record using InfluxDB Line protocol

        Format :
                bgp,type={record['type']},project={record['project']},
                collector={record['collector']},country={record['country_code'] or ''}
                 peer={record["peer_asn"]},prefix="{record["prefix"]}",
                path="{record.get("as-path", "")}",source="{record["source"]}"
                 {int(record['time']*1000000000)}\n

        Args:
            record (BGPElem)
        """

        self.send_utf8(
            (
                f"bgp,type={record['type']},project={record['project']},"
                f"collector={record['collector']},country={record['country_code'] or ''}"
                f' peer={record["peer_asn"]},prefix="{record["prefix"]}",'
                f'path="{record.get("as-path", "")}",source="{record["source"]}"'
                f" {int(record['time']*1000000000)}\n"
            )
        )

    def send_utf8(self, msg):
        """Encode message and send it to server"""
        self.sock.sendall(msg.encode())

    ##############
    #   GETTER   #
    ##############
    # The followings aren't used

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
    # Used in `QuestDB.get` function as arg_name:db_column_name

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
        Retrieve data from QuestDB using psycopg2 (Postgre) connection

        See `Database.get()`
        """
        if not self.cursor:
            self.cursor = self.connection.cursor()

        query = "SELECT * FROM bgp WHERE"
        params = {key: value for key, value in locals() if value is not None}

        if len(params) > 0:
            for k, v in params:
                query += (
                    f" {QuestDB.var_names[k]} "
                    + ("IN " if isinstance(v, collections.Sequence) else "== ")
                    + f"%s and"
                )
            query += query.rsplit(" ", 1)[0]

        self.cursor.execute(query, params.values())
        return self.cursor.fetchall()
