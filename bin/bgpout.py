
import redis, json, os, sys
from pyail import PyAIL


class BGPOut():
    def __init__(self, redis= None, ail= None) -> None:
        self.__redis = None
        self.__ail = None
        self.__source_uuid = None

        self.redis = redis
        self.ail = ail

    @property
    def json_out(self):
        return self.__json_out

    @property
    def redis(self):
        return self.__redis

    @redis.setter
    def redis(self, r):
        self.__redis = r
        r.ping()
    
    @property
    def expected_result(self):
        return self.__expected_result
    

    def input_data(self, data):
        """Send data to redis"""
        redis.xadd(data) # ?
        # Need to check redis usage again

    def check_bgp(self, data):
        # Check if data is suspicious
        # Implement an IA ?
        # Currently searching
        pass
    
    def publish(self, data):
        self.__ail.feed_json_item(str(data), r, "ail_feeder_bgp", self.__source_uuid)
            
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
            raise ValueError("Ail url, api key, and source_uuid are required for connection")

        try:
            UUID(source_uuid, version=4)
            self.__source_uuid = source_uuid
        except ValueError:
            raise ValueError("Invalid source uuid v4 format.")

        try:
            self.__ail = PyAIL(url, api_key, ssl=False)
        except Exception as e:
            raise Exception(e)

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


    @expected_result.setter
    def expected_result(self, expected_result):
        if expected_result is not None:
            if hasattr(expected_result, "read"):
                self.__expected_result = expected_result
            else:
                raise FileNotFoundError(f"Is {expected_result} a file ?")

    def checkFiles(self, f1, f2):
        f1.seek(0, os.SEEK_SET)
        f2.seek(0, os.SEEK_SET)
        json1 = json.load(f1)
        json2 = json.load(f2)
        return json1 == json2

    def closeFile(self, file):
        if file != sys.stdout:
            print(file.tell())
            file.seek(file.tell() - 1, os.SEEK_SET)
            file.truncate()
        file.write(']')
        file.close()
        
    def _begin(self):
        self.__json_out.write('[')
