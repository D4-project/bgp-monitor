import json
import os
import sys

import maxminddb
import pybgpstream
import pycountry
from pytz import country_names


class BGPFilter:
    """BGP stream filter"""

    def __init__(self):
        self.__json_out = sys.stdout
        self.__isStarted = False
        self.__isRecord = False
        self.__start_time = ""
        self.__end_time = ""
        self.__country_file = "mmdb_files/latest.mmdb"
        self.__collectors = []
        self.__countries_filter = []

    @property
    def start_time(self):
        return self.__start_time

    @property
    def end_time(self):
        return self.__end_time

    @property
    def isRecord(self):
        return self.__isRecord

    @property
    def json_out(self):
        return self.__json_out

    @property
    def country_file(self):
        return self.__country_file

    @property
    def countries_filter(self):
        return self.__countries_filter

    @property
    def cidr_filter(self):
        return None

    @property
    def asn_filter(self):
        return None

    def set_record_mode(self, isRecord, start, end):
        """
        Define if record mode or live stream.
        start and begin will not be modified if isRecord == false
        Args:
            isRecord (bool)
            start (string): Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00
            end (string): Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00

        Raises:
            Exception: If start == end or not define
        """
        self.__isRecord = isRecord
        if isRecord:
            if not (start != end != ""):
                # Check using a regex ?
                raise Exception(
                    "--until_time and --from_time parameters are required when using record mode"
                )
            else:
                self.__start_time = start
                self.__end_time = end

    @json_out.setter
    def json_out(self, json_out):
        """Setter for JSON output

        Default : sys.stdout

        Parameters:
            json_output_file (File): Where to output json
        Raises:
            Exception: If unable to use
        """
        if hasattr(json_out, "write"):
            self.__json_out = json_out
        else:
            raise FileNotFoundError(f"Is {json_out} a file ?")

    @country_file.setter
    def country_file(self, country_file):
        """Define country mmdb file

        Parameters:
            country_file (String): Path to current Geo Open MaxMindDB File
        """
        if not os.path.isfile(country_file):
            raise FileNotFoundError
        self._country_file = country_file

    @cidr_filter.setter
    def cidr(self, CIDR):
        pass

    @countries_filter.setter
    def countries(self, country_list):
        for c in country_list:
            pycountry.countries.lookup(c)
        self.__countries = country_list

    @asn_filter.setter
    def asn_filter(self, asn_filter):
        return None

    def __setCollectors(self, collectors):
        pass

    def __pprint(self, e):
        print("type : " + e.type)
        self.__json_out.write(
            json.dumps(
                {
                    "time": e.time,
                    "type": e.type,
                    "peer": e.peer_address,
                    "peer_asnumber": e.peer_asn,
                    "prefix": e._maybe_field("prefix"),
                    "country_code": self.__getCountryByPrefix(e.fields["prefix"]),
                }
            )
        )
        # print(e.fields)

    def __getCountryByPrefix(self, p):
        return self.__f_country.get(p.split("/", 1)[0])["country"]["iso_code"]
        return "" if not p else self.__f_country.get(p.split("/", 1)[0])["country"]["iso_code"]

    def start(self):
        """Start retrieving stream/records and filtering them"""
        self.__isStarted = True
        self.__json_out.write("{")

        self.__f_country = maxminddb.open_database(self.__country_file)
        print(f"Loaded MMDB country by ip file : {self.__country_file}")

        if self.__isRecord:
            print("Loading records ...")
            self.stream = pybgpstream.BGPStream(
                collectors=["route-views.sg", "route-views.eqix"],
                record_type="updates",
                from_time=self.start_time,
                until_time=self.end_time,
            )
        else:
            print("Loading live stream ...")
            self.stream = pybgpstream.BGPStream(
                project="ris-live",
                collectors=self.__collectors,
                record_type="updates",
            )

        print("Let's go")
        for elem in self.stream:
            self.__pprint(elem)

    def stop(self):
        self.__isStarted = False
        self.__json_out.write("}")
        self.close()
