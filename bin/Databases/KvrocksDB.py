from Databases.database import Database
import redis


class KvrocksDB(Database):
    """
    This database store data as live
    --> When a withdraw is received, concerned prefixes are removed
    """

    name = "kvrocks"

    def __init__(self, config):
        super().__init__()
        self.client = redis.Redis(
            host=config["host"], port=config["port"], db=config["db"]
        )

    def start(self):
        print(f"Database size : {self.client.dbsize()}")

    def stop(self):
        pass

    ###############
    #   INSERTS   #
    ###############

    def save(self, record):
        """Store data in a sorted set named "bgp" with a scorebased on Time

        Format :
            bgp-prefix:path:source time time:type:peer_asn:collector:country_code

        Args:
            record (`BGPElem`): BGP Element to save
        """
        e = record

        if e["type"] == "A":
            self.client.sadd(
                f"prefixes-{e['source']}", e["prefix"]
            )  # prefixes-{ASN} : (cidr, cidr)
            self.client.sadd(
                f"prefixes-{e['country_code']}", e["prefix"]
            )  # prefixes-{LU} : (cidr, cidr)
            self.client.sadd(
                f"as-{e['prefix']}", e["source"]
            )  # as-{cidr} : (as, as, as)
            self.client.sadd(
                f"countries-{e['prefix'] or ''}", e["country_code"]
            )  # countries-{cidr} : (LU, FR)
            self.client.sadd(
                f"paths-{e['prefix']}", e.get("as-path")
            )  # paths-{cidr} : (path, path, path)

            self.client.zadd(
                "bgp-{}:{}:{}".format(e["prefix"], e.get("as-path"), e["source"]),
                {
                    f"{e['time']}:{e['type']}:{e['peer_asn']}:"
                    f"{e['collector']}:{e['country_code']}": int(float(e["time"]))
                },
            )
        #            self.client.execute()

        elif e["type"] == "W":
            return
            for as_source in self.client.smembers(f"as-{e['prefix']}"):
                self.client.srem(
                    f"prefixes-{as_source}", e["prefix"]
                )  # pr AS {cidr, cidr}

            for pr in self.client.smembers(f"country-{e['prefix']}"):
                self.client.srem(
                    f"prefixes-{e['country_code']}", pr
                )  # pr LU {cidr, cidr}

            self.client.delete(f"countries-{e['prefix']}")  # countries-cidr {LU, FR}
            self.client.delete(f"as-{e['prefix']}")  # as-cidr {as, as, as }
            self.client.delete(f"paths-{e['prefix']}")  # paths-cidr {path, path, path}

            self.client.zadd(
                "bgp-{}".format(e["prefix"]),
                {
                    f"{e['time']}:{e['type']}:{e['peer_asn']}:{e['collector']}": int(
                        float(e["time"])
                    )
                },
            )
            self.client.zadd(
                "bgp-{}:{}".format(e["prefix"], e.get("as-path")),
                {
                    f"{e['time']}:{e['type']}:{e['peer_asn']}:"
                    f"{e['collector']}": int(float(e["time"]))
                },
            )

    ##############
    #   GETTER   #
    ##############

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
