from Databases.database import Database
import socket


class QuestDB(Database):
    name = "quest"

    def __init__(self, config):
        super().__init__()
        # For UDP, change socket.SOCK_STREAM to socket.SOCK_DGRAM
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((config["host"], int(config["port"])))

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
        super().get()
        pass

    def start(self):
        pass

    def save(self, record):
        """Save bgp record using InfluxDB Line protocol
        Args:
            record (_type_): BGPElem
        """

        self.send_utf8(
            f"bgp,type={record.type},collector={record.collector},"
            f"country={record.country_code} peerasn={record.peer_asn},"
            f'peeraddress="{record.peer_address}",prefix="{record.prefix}",'
            f'aspath="{record.path}",source={record.source}'
            f" {int(record.time*1000000000)}\n"
        )

    def stop(self):
        self.sock.close()

    def send_utf8(self, msg):
        self.sock.sendall(msg.encode())
