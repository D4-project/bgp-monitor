import ipaddress
import os
import re
import sys
import json
import threading
from uuid import UUID
import maxminddb
import pycountry
import pybgpstream

from pyail import PyAIL
from queue import Queue
from datetime import datetime

collectors_list = {
    "routeviews": [
        "route-views.amsix",
        "route-views.bdix",
        "route-views.bknix",
        "route-views.chicago",
        "route-views.chile",
        "route-views.eqix",
        "route-views.flix",
        "route-views.fortaleza",
        "route-views.gixa",
        "route-views.gorex",
        "route-views.isc",
        "route-views.jinx",
        "route-views.kixp",
        "route-views.linx",
        "route-views.mwix",
        "route-views.napafrica",
        "route-views.nwax",
        "route-views.ny",
        "route-views.perth",
        "route-views.peru",
        "route-views.phoix",
        "route-views.rio",
        "route-views.saopaulo",
        "route-views.sfmix",
        "route-views.sg",
        "route-views.siex",
        "route-views.soxrs",
        "route-views.sydney",
        "route-views.telxatl",
        "route-views.uaeix",
        "route-views.wide",
        "route-views2",
        "route-views2.saopaulo",
        "route-views3",
        "route-views4",
        "route-views5",
        "route-views6",
    ],
    "ris": [
        "rrc00",
        "rrc01",
        "rrc02",
        "rrc03",
        "rrc04",
        "rrc05",
        "rrc06",
        "rrc07",
        "rrc08",
        "rrc09",
        "rrc10",
        "rrc11",
        "rrc12",
        "rrc13",
        "rrc14",
        "rrc15",
        "rrc16",
        "rrc18",
        "rrc19",
        "rrc20",
        "rrc21",
        "rrc22",
        "rrc23",
        "rrc24",
        "rrc25",
        "rrc26",
    ],
}
project_types = {"ris": "ris-live", "routeviews": "routeviews-stream"}


class BGPFilter:
    """BGP stream filter"""

    def __init__(self):
        self.__isStarted = False
        self.__isRecord = False
        self.__start_time = ""
        self.__end_time = ""
        self.__f_country_path = "../mmdb_files/latest.mmdb"
        self.__countries_filter = None
        self.__asn_filter = None
        self.__ipversion = ""
        self.__cidr_filter = None
        self.__cidr_match_type_filter = None
        self.__queue = Queue()
        self.__project = list(project_types.keys())[0]
        self.__collectors = None
        self.__redis = None
        self.__ail = None
        self.__no_ail = False
        self.__source_uuid = None
        self.__cache_expire = 86400
        self.nocaching = False
        self.__data_source = {"source_type": "broker"}
        self.__expected_result = None

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
    def country_file(self):
        return self.__f_country_path

    @property
    def countries_filter(self):
        return self.__countries_filter

    @property
    def cidr_filter(self):
        return self.__cidr_filter

    @property
    def asn_filter(self):
        return self.__asn_filter

    @property
    def collectors(self):
        return self.__collectors

    @property
    def json_out(self):
        return self.__json_out

    @property
    def project(self):
        return self.__project

    @property
    def redis_db(self):
        return self.__redis

    @property
    def ail(self):
        return self.__ail

    @property
    def no_ail(self):
        return self.__no_ail

    @property
    def cache_expire(self):
        return self.__cache_expire

    @property
    def ipversion(self):
        return self.__ipversion

    @property
    def expected_result(self):
        return self.__expected_result

    @property
    def queue(self):
        return self.__queue

    ###############
    #   SETTERS   #
    ###############

    def set_record_mode(self, isRecord, start, end):
        """
        Define record mode or live stream.
            start and end will not be modified if isRecord is False
        Args:
            isRecord (bool)
            start (string): Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00
            end (string): Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00

        Raises:
            ValueError: If start > end
                        If start or end not defined
                        If invalid date format
        """
        self.__isRecord = isRecord
        if isRecord:
            if start is None or end is None:
                raise ValueError("Record mode requires the from_time and until_time arguments")
            try:
                st = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                en = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError("Invalid record mode date format. Must be %Y-%m-%d %H:%M:%S")
            if st > en:
                raise ValueError("Invalid record mode interval. Beginning must precede the end")

            self.__start_time = start
            self.__end_time = end

    def data_source(self, record_type, file_format, file_path):
        """
        Use single file as data source

        Args:
            record_type (str): rib or upd
            file_format (str): mrt, bmp or ris-live
            file_path (str): path to archive file

        Raises:
            FileNotFoundError
            ValueError
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError
        if record_type not in ["rib", "upd"]:
            raise ValueError("Input file type must be rib or upd")
        if record_type == "rib" and file_format in ["mrt", "bmp"]:
            raise ValueError("Accepted input format types for rib : mrt, bmp")
        elif record_type == "upd" and file_format not in ["mrt", "bmp", "ris-live"]:
            raise ValueError("Accepted input format types for upd : mrt, bmp or ris-live")

        self.__data_source = {"source_type": record_type, "file_format": file_format, "file_path": file_path}

    @country_file.setter
    def country_file(self, country_file_path):
        """
        Setter for the GeoOpen country mmdb file

        Parameters:
            country_file_path (String): Path to Geo Open MaxMindDB File
        """
        if not os.path.isfile(country_file_path):
            raise FileNotFoundError
        self.__f_country_path = country_file_path

    def set_cidr_filter(self, isCIDR, match_type, cidr_list):
        """
        CIDR filter option
            Keep records that match to one of specified cidr.

        Parameters:
            match_type: Type of match
                exact: Exact match
                less: Exact match or less specific (contained by)
                more: Exact match or more specific (contains)
                any: less and more
            CIDR (string):  Format: ip/subnet | Example: 130.0.192.0/21
        """
        if isCIDR:
            if cidr_list is None or len(cidr_list) == 0:
                raise Exception("Please specify one or more prefixes when filtering by prefix")
            if match_type not in ["exact", "less", "more", "any"]:
                raise ValueError("Match type must be specified and one of ['exact', 'less', 'more', 'any']")
            for c in cidr_list:
                ipaddress.ip_network(c)
            self.__cidr_match_type_filter = "prefix-" + match_type
            self.__cidr_filter = cidr_list

    @countries_filter.setter
    def countries_filter(self, country_list):
        """
        Filter using specified country.
            Keep records that the origin of their prefix is contained in country_list.

        Parameters:
            country_list (list): List of country codes

        Raises:
            LookupError: If an element in country_list is not valid.
        """
        if country_list is not None:
            for c in country_list:
                pycountry.countries.lookup(c)
        self.__countries_filter = country_list

    @asn_filter.setter
    def asn_filter(self, asn_list):
        """Filter using specified AS number list
            Skip a record if its as-path doesn't contain one of specified AS numbers

        Args:
            asn_list (list): List of AS numbers
        """
        self.__asn_filter = ""
        f_list = []
        not_f_list = []
        if asn_list is not None and len(asn_list) >= 1:
            for i in asn_list:
                if re.match("_[0-9]+", i):
                    not_f_list.append(i.replace("_", ""))
                else:
                    f_list.append(i)

            if len(f_list) >= 1:
                self.__asn_filter += " and path (_" + "_|_".join(f_list) + "_)"
            if len(not_f_list) >= 1:
                self.__asn_filter = " and path !(_" + "_|_".join(not_f_list) + "_)"

            print(self.__asn_filter)

    @collectors.setter
    def collectors(self, collectors):
        if collectors is not None:
            for c in collectors:
                if c not in collectors_list[self.__project]:
                    raise ValueError("Invalid collector name.")
            self.__collectors = collectors

    @project.setter
    def project(self, project):
        """
        Args:
            project (string): ris or routesviews
        """
        if self.__collectors != project and project in project_types.keys():
            self.__project = project
            self.__collectors = None
        else:
            raise ValueError(f"Invalid project name. Valid projects list : {project_types.keys()}")

    @redis_db.setter
    def redis_db(self, r):
        r.ping()
        self.__redis = r

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

    @no_ail.setter
    def no_ail(self, val):
        self.__no_ail = val

    @cache_expire.setter
    def cache_expire(self, val):
        if val >= 0:
            self.__cache_expire = val

    @queue.setter
    def queue(self, bool):
        if bool:
            self.__queue = Queue()
        else:
            self.__queue = None

    @ipversion.setter
    def ipversion(self, version):
        self.__ipversion = " and ipversion " + version if version in ["4", "6"] else ""

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

    ###############
    #   PRINTERS  #
    ###############

    def __country_by_prefix(self, p):
        """
        Parameters:
            p (prefix): CIDR format. Example: 130.0.192.0/21

        Returns:
            string: country code of the given prefix. None if not found in GeoOpen database
        """
        if p is None:
            return None
        else:
            r = self.__f_country.get(p.split("/", 1)[0])
            return r["country"]["iso_code"] if r is not None else None

    def __bgp_conv(self, e):
        """Return a BGPElem as json

        Parameters:
            e (BGPElem)
        """
        country_code = self.__country_by_prefix(e._maybe_field("prefix"))
        if self.__countries_filter is not None and country_code not in self.__countries_filter:
            return None

        data = {
            "bgp:type": e.type,
            "bgp:time": e.time,
            "bgp:peer": e.peer_address,
            "bgp:peer_asn": e.peer_asn,
            "bgp:collector": e._maybe_field("collector"),
        }

        if e.type in ["A", "R", "W"]:  # updateribs
            data["bgp:prefix"] = e._maybe_field("prefix")
            data["bgp:country_code"] = country_code
        if e.type in ["A", "R"]:  # updateribs
            data["bgp:as-path"] = e._maybe_field("as-path")
            data["bgp:next-hop"] = e._maybe_field("next-hop")
        elif e.type == "S":  # peer state
            data["bgp:old-state"] = e._maybe_field("old-state")
            data["bgp:new-state"] = e._maybe_field("new-state")

        return data

    def __iteration(self, e):
        # redis save
        key = str(e)
        r = self.__bgp_conv(e)

        if r is None:
            return

        if self.__no_ail:
            print("\n" + json.dumps(r, sort_keys=True) + ",")  # print to stdout
        else:
            if not self.nocaching:  # Check if record already exist
                if self.__redis.exists(f"event:{key}"):
                    print("record already exist : " + key)
                else:
                    self.__redis.set(f"event:{key}", key)
                    self.__redis.expire(f"event:{key}", self.__cache_expire)
                    self.__ail.feed_json_item(str(e), r, "ail_feeder_bgp", self.__source_uuid)
            else:
                self.__ail.feed_json_item(str(e), r, "ail_feeder_bgp", self.__source_uuid)

        if self.__json_out != sys.stdout:
            self.json_out.write("\n" + json.dumps(r, sort_keys=True, indent=4) + ",")

    def send_data(self):

        pass

    def __print_queue(self):
        """Iterate over queue to process each bgp element"""
        while self.__isStarted or self.__queue.qsize():
            self.__iteration(self.__queue.get())
            self.__queue.task_done()

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def start(self):
        """
        Start retrieving stream/records and filtering them
        - Load Geo Open database
        - Start stream with args
        - Print each record as JSON format
        """
        self.__isStarted = True
        self.__f_country = maxminddb.open_database(self.__f_country_path)
        print(f"Loaded Geo Open database : {self.__f_country_path}")
        print("Loading stream ...")

        self._stream = pybgpstream.BGPStream(
            from_time=(self.start_time if self.__isRecord else None),
            until_time=(self.end_time if self.__isRecord else None),
            data_interface=("broker" if self.__data_source["source_type"] == "broker" else "singlefile"),
            record_type="updates",
            filter="elemtype announcements withdrawals" + self.__asn_filter + self.__ipversion,
        )

        if self.__cidr_match_type_filter is not None:
            self._stream._maybe_add_filter(self.__cidr_match_type_filter, None, self.__cidr_filter)

        print("Starting")
        self.__json_out.write("[")

        if self.__data_source["source_type"] != "broker":
            self._stream.set_data_interface_option(
                "singlefile", self.__data_source["source_type"] + "-file", self.__data_source["file_path"]
            )
            self._stream.set_data_interface_option(
                "singlefile", self.__data_source["source_type"] + "-type", self.__data_source["file_format"]
            )
        else:
            project = self.__project if self.__isRecord else project_types[self.__project]
            self._stream._maybe_add_filter("project", project, None)
            self._stream._maybe_add_filter("collectors", None, self.__collectors)

        if self.__queue:
            threading.Thread(target=self.__print_queue, daemon=True, name="BGPFilter output").start()
            for elem in self._stream:
                self.__queue.put(elem)
                print("Queue size : " + str(self.__queue.qsize()), file=sys.stderr)

        else:
            for elem in self._stream:
                self.__iteration(elem)

    def stop(self):
        """
        Stop BGPStream
            Close JSON output file
        """
        if self.__isStarted:
            self.__isStarted = False
            print("Finishing queue ...")
            self.__queue.join()
            jout = self.__json_out.name
            closeFile(self.__json_out)

            if self.__expected_result is not None:
                f1 = open(jout)
                if checkFiles(f1, self.__expected_result):
                    print("The filtered result is as expected")
                else:
                    print("The filtered result is not as expected")

            print("Stream ended")
            exit(0)


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
