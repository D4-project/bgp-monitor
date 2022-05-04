import threading
from uuid import UUID
import redis
import json
import os
import sys
from pyail import PyAIL


class BGPOut:
    def __init__(self, redis=None, ail=None) -> None:
        self.__redis = None
        self.__ail = None
        self.__source_uuid = None
        self.__expected_result = None

        self.redis = redis
        self.ail = ail

    #######################
    #   GETTERS/SETTERS   #
    #######################

    @property
    def redis(self):
        return self.__redis

    @redis.setter
    def redis(self, host, port, db):
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
    def expected_result(self, expected_result):
        if expected_result is not None:
            if hasattr(expected_result, "read"):
                self.__expected_result = expected_result
            else:
                raise FileNotFoundError(f"Is {expected_result} a file ?")

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

        if self.__no_ail:
            pass
            # print('\n' + json.dumps(r,sort_keys=True)+ ',') # print to stdout
        else:
            #            if not self.nocaching: # Check if record already exist
            #                if self.__redis.exists(f"event:{key}"):
            #                        print("record already exist : " + key)
            #                else:
            #                    self.__redis.set(f"event:{key}", key)
            #                    self.__redis.expire(f"event:{key}", self.__cache_expire)
            #                    self.__ail.feed_json_item(str(e), r, "ail_feeder_bgp", self.__source_uuid)
            #            else:
            #                self.__ail.feed_json_item(str(e), r, "ail_feeder_bgp", self.__source_uuid)
            pass
        if self.__json_out != sys.stdout:
            pass
            # self.json_out.write('\n' + json.dumps(r,sort_keys=True,indent=4)+ ',')

    def __process_queue(self):
        """Iterate over queue to process each bgp element"""
        while self.__isStarted or self.__queue.qsize():
            pass
            # self.__iteration(self.__queue.get())
            # self.__queue.task_done()

    #            print("Queue size : " + str(self.__queue.qsize()), file=sys.stderr)
    #            threading.Thread(target=self.__print_queue, daemon=True, name="BGPFilter output").start()

    def input_data(self, data):
        """receive bgp elem"""
        if self.redis:
            self.redis.xadd(data)
            """Send data to redis"""
            # redis.xadd(data)
            # Need to check redis usage again
        else:
            self.__iteration(data)

    def check_bgp(self, data):
        # Check if data is suspicious
        # Implement an IA ?
        # Currently searching
        pass

    def publish(self, data):
        self.__ail.feed_json_item(
            str(data), data, "ail_feeder_bgp", self.__source_uuid
        )

    """
    @property
    def queue(self):
        return self.__queue
    @queue.setter
    def queue(self, bool):
        if bool:
            self.__queue = Queue()
        else :
            self.__queue = None
    """


def checkFiles(f1, f2):
    f1.seek(0, os.SEEK_SET)
    f2.seek(0, os.SEEK_SET)
    json1 = json.load(f1)
    json2 = json.load(f2)
    return json1 == json2


def closeFile(file):
    if file != sys.stdout:
        print(file.tell())
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.truncate()
    file.write("]")
    file.close()

    # Algorithm :


"""
def process(data):
    if queue
        if queue.add(data)
    else
        iterate(data)


def threaded:
    while not end:
        iterate(data.get())

def iterate(data):
    if redis:
        update_redis(data.count) #asn/cidr count eg last seend

    if isSuspicious(data):
        if ail
            publish
"""
