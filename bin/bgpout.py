import os
import sys
import json
import redis
import threading
from uuid import UUID
from queue import Queue
from pyail import PyAIL


class BGPOut:
    def __init__(self, redis=None, ail=None, stream_name="bgpmonitor") -> None:
        self.__redis = None
        self.__ail = None
        self.__source_uuid = None
        self.__expected_result = None
        self.__queue = Queue()
        self.isStarted = False
        self.stream_name = stream_name

    #######################
    #   GETTERS/SETTERS   #
    #######################

    @property
    def queue(self):
        return self.__queue

    @queue.setter
    def queue(self, isQueue):
        if isQueue:
            self.__queue = Queue()
        else:
            self.__queue = None

    @property
    def redis(self):
        return self.__redis

    @redis.setter
    def redis(self, values):
        """

        Args:
            host: Ip address of redis
            port: Port number of redis
            db:
        """
        try:
            host, port, db = values
        except ValueError:
            sys.stderr.write("Connection to Redis is not available")
            return
        self.__redis = redis.Redis(host=host, port=port, db=db)
        self.__redis.ping()

    @property
    def ail(self):
        return self.__ail

    @ail.setter
    def ail(self, values):
        """Define args for connection to ail instance

        Args:
            Ail: (url, api_key, source_uuid)
            url (string): Url (ip:port/path to import)
            apikey (string)
            source_uuid (string)

        Raises:
            ValueError: if args not defined
            ValueError: if source uuid doesn't respect uuid v4 format
        """
        try:
            url, api_key, source_uuid = values
        except ValueError:
            raise ValueError(
                "Ail url, api key, and source_uuid are required for connection"
            )

        try:
            UUID(source_uuid, version=4)
            self.__source_uuid = source_uuid
        except ValueError:
            raise ValueError("Invalid source uuid v4 format.")

        try:
            self.__ail = PyAIL(url, api_key, ssl=False)
        except Exception as e:
            raise Exception(e)

    @property
    def json_out(self):
        return self.__json_out

    @json_out.setter
    def json_out(self, json_out):
        """
        Setter for JSON output
            Default : sys.stdout
        Parameters:
            json_out (File): Where to output json
        Raises:
            Exception: If unable to use
        """
        if hasattr(json_out, "write"):
            self.__json_out = json_out
        else:
            raise FileNotFoundError(f"Is {json_out} a file ?")

    @property
    def expected_result(self):
        return self.__expected_result

    @expected_result.setter
    def expected_result(self, exp):
        if exp is not None:
            if hasattr(exp, "read"):
                self.__expected_result = exp
            else:
                raise FileNotFoundError(f"Is {exp} a file ?")

    ########
    # MAIN #
    ########

    def start(self):
        self.__json_out.write("[")
        self.isStarted = True
        if self.__queue:
            threading.Thread(
                target=self.__process_queue,
                daemon=True,
                name="BGP monitor out",
            ).start()

    def stop(self):
        if self.isStarted:
            self.isStarted = False
        closeFile(self.__json_out)
        if self.__expected_result:
            print("Testing result: ")
            with open(self.__json_out.name, "r+") as js:
                print(
                    "Result is as expected"
                    if checkFiles(js, self.__expected_result)
                    else "Result is not as expected"
                )

    def __bgp_conv(self, e):
        """Return a BGPElem as json

        Parameters:
            e (BGPElem)
        """
        data = {
            "bgp:type": e.type,
            "bgp:time": e.time,
            "bgp:peer": e.peer_address,
            "bgp:peer_asn": e.peer_asn,
            "bgp:collector": e._maybe_field("collector"),
        }

        if e.type in ["A", "R", "W"]:  # updateribs
            data["bgp:prefix"] = e._maybe_field("prefix")
            data["bgp:country_code"] = e.country_code
        if e.type in ["A", "R"]:  # updateribs
            data["bgp:as-path"] = e._maybe_field("as-path")
            data["bgp:next-hop"] = e._maybe_field("next-hop")
        elif e.type == "S":  # peer state
            data["bgp:old-state"] = e._maybe_field("old-state")
            data["bgp:new-state"] = e._maybe_field("new-state")

        return data

    def __iteration(self, e):
        # redis save
        r = self.__bgp_conv(e)

        """Send data to redis"""
        if self.isHijack(r):
            if self.ail:
                self.__ail.feed_json_item(
                    str(e), r, self.stream_name, self.__source_uuid
                )
            else:
                print(
                    "\n" + json.dumps(r, sort_keys=True) + ","
                )  # print to stdout
            #                    self.__ail.feed_json_item(str(e), r, "ail_feeder_bgp", self.__source_uuid)

        if self.redis:
            self.redis.xadd(self.__stream_name, r)

        if self.__json_out != sys.stdout:
            self.json_out.write(
                "\n" + json.dumps(r, sort_keys=True, indent=4) + ","
            )

    def __process_queue(self):
        """Iterate over queue to process each bgp element"""
        while self.isStarted or self.__queue.qsize():
            # print("Queue size : " + str(self.__queue.qsize()), file=sys.stderr)
            self.__iteration(self.__queue.get())
            self.__queue.task_done()

    def input_data(self, data):
        """receive bgp elem"""
        if self.__queue:
            self.__queue.put(data)
        else:
            self.__iteration(data)

    def isHijack(self, data) -> bool:
        # Check if data is suspicious
        # Implement an IA ?
        # Currently searching
        return True

    def publish(self, data):
        self.__ail.feed_json_item(
            str(data), data, "ail_feeder_bgp", self.__source_uuid
        )


def checkFiles(f1, f2):
    f1.seek(0, os.SEEK_SET)
    f2.seek(0, os.SEEK_SET)
    json1 = json.load(f1)
    json2 = json.load(f2)
    return json1 == json2


def closeFile(file):
    if file != sys.stdout:
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.truncate()
    file.write("]")
    file.close()
