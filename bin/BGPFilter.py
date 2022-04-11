import os
import sys
import json
import maxminddb
import pycountry
import pybgpstream

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
        self.__collectors = None
        self.__countries_filter = None

    ###############
    #   GETTERS   #
    ###############

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

    ###############
    #   SETTERS   #
    ###############

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
        """TODO"""
        pass

    @countries_filter.setter
    def countries_filter(self, country_list):
        if country_list is not None:
            for c in country_list:
                pycountry.countries.lookup(c)
            self.__countries_filter = country_list

    @asn_filter.setter
    def asn_filter(self, asn_filter):
        """TODO"""
        return None

    def __setCollectors(self, collectors):
        """TODO"""
        pass

    ###############
    #   PRINTERS  #
    ###############

    def __country_by_prefix(self, p):
        return self.__f_country.get(p.split("/", 1)[0])["country"]["iso_code"]

    def __jprint(self, e):
        res = {
            "type": e.type,
            "time": e.time,
            "peer": e.peer_address,
            "peer_asn": e.peer_asn,
            "collector": e.collector,
        }

        if e.type in ["A", "R", "W"]:  # updateribs
            res["prefix"] = e.fields["prefix"]
            res["country_code"] = self.__country_by_prefix(e.fields["prefix"])
        if e.type in ["A", "R"]:  # updateribs
            res["as-path"] = e.fields["as-path"]
            res["next-hop"] = e.fields["next-hop"]
        elif e.type == "S":  # peer state
            res["old-state"] = e.fields["old-state"]
            res["new-state"] = e.fields["new-state"]

        if (self.__countries_filter is not None) and (
            res["country_code"] not in self.__countries_filter
        ):
            res = {}  # country filter

        r = json.dumps(res)
        self.__json_out.write("" if r == "{}" else (r + ","))

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def start(self):
        """Start retrieving stream/records and filtering them"""
        self.__isStarted = True
        self.__json_out.write("{")

        self.__f_country = maxminddb.open_database(self.__country_file)
        print(f"Loaded Geo Open database : {self.__country_file}")

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
            self.__jprint(elem)

    def stop(self):
        self.__isStarted = False
        self.__json_out.write("}")
        self.close()
