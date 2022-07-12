from Databases.database import Database
import redis


class KvrocksDB(Database):
    name = "kvrocks"

    def __init__(self, config):
        super().__init__()
        self.client = redis.Redis(
            host=config["host"], port=config["port"], db=config["db"]
        )
        self.pipe = self.client.pipeline(True)

    def start(self):
        print(f"Database size : {self.client.dbsize()}")

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
        """Can't be tested now"""

        pass

    def save(self, record):
        """Store data in a sorted set named "bgp" with a scorebased on Time

        Format :
            bgp-prefix:path:source time time:type:peer_asn:collector:country_code

        Args:
            record (`BGPElem`): BGP Element to save
        """
        e = record

        if e.type == "A":
            self.pipe.sadd(f"prefixes-{e.source}", e.prefix)  # pr AS {cidr, cidr }
            self.pipe.sadd(f"prefixes-{e.country_code}", e.prefix)  # pr LU {cidr, cidr}
            self.pipe.sadd(f"as-{e.prefix}", e.source)  # as-cidr {as, as, as }
            self.pipe.sadd(
                f"countries-{e.prefix}", e.country_code
            )  # countries-cidr {LU, FR}
            self.pipe.sadd(f"paths-{e.prefix}", e.path)  # paths-cidr {path, path, path}

            self.pipe.zadd(
                "bgp-{}:{}:{}".format(e.prefix, e.path, e.source),
                {
                    f"{e.time}:{e.type}:{e.peer_asn}:"
                    f"{e.collector}:{e.country_code}": int(float(e.time))
                },
            )
            self.pipe.execute()

        elif e.type == "W":
            for as_source in self.client.smembers(f"as-{e.prefix}"):
                self.pipe.srem(f"prefixes-{as_source}", e.prefix)  # pr AS {cidr, cidr}

            for pr in self.client.smembers(f"country-{e.prefix}"):
                self.pipe.srem(f"prefixes-{e.country_code}", pr)  # pr LU {cidr, cidr}

            self.pipe.delete(f"countries-{e.prefix}")  # countries-cidr {LU, FR}
            self.pipe.delete(f"as-{e.prefix}")  # as-cidr {as, as, as }
            self.pipe.delete(f"paths-{e.prefix}")  # paths-cidr {path, path, path}

            self.pipe.zadd(
                "bgp-{}".format(e.prefix),
                {f"{e.time}:{e.type}:{e.peer_asn}:{e.collector}": int(float(e.time))},
            )
            self.pipe.zadd(
                "bgp-{}:{}".format(record.prefix, record._maybe_field("as-path")),
                {
                    f"{record.time}:{record.type}:{record.peer_asn}:"
                    f"{record.collector}": int(float(record.time))
                },
            )

    def stop(self):
        pass
