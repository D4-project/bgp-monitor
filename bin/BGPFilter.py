import os
import re
import sys
import json
import threading
import maxminddb
import pycountry
import pybgpstream

from datetime import datetime
from queue import Queue
from pytz import country_names


class BGPFilter:
    """BGP stream filter"""

    def __init__(self):
        self.__json_out = sys.stdout
        self.__isStarted = False
        self.__isRecord = False
        self.__start_time = ""
        self.__end_time = ""
        self.__f_country_path = "mmdb_files/latest.mmdb"
        self.__collectors = None
        self.__countries_filter = None
        self.__asn_filter = None
        self.__cidr_filter = None
        self.__cidr_match_type_filter = None
        self.__queue = Queue()

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
            Exception: If start == end or not defined
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
                raise ValueError("Invalid record mode interval. Beginning must ")

            self.__start_time = start
            self.__end_time = end

    @json_out.setter
    def json_out(self, json_out):
        """
        Setter for JSON output
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
                less: Exact match or less specific
                more: Exact match or more specific
                any
            CIDR (string):  Format: ip/subnet | Example: 130.0.192.0/21
        """
        if isCIDR:
            if cidr_list is None or len(cidr_list) == 0:
                raise Exception("Please specify one or more prefixes when filtering by prefix")
            if match_type not in ["exact", "less", "more", "any"]:
                raise ValueError(
                    "Match type must be specified and one of ['exact', 'less', 'more', 'any']"
                )
            for c in cidr_list:
                if not re.match(r"^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))$", c):
                    raise Exception(f"Invalid CIDR format : {c}")
            self.__cidr_match_type_filter = "prefix-" + match_type
            self.__cidr_filter = cidr_list

    @countries_filter.setter
    def countries_filter(self, country_list):
        """
        Filter using specified country.
            Keep records that the origin of their prefix is contained in country_list.

        Parameters:
            country_list (list): List of country codes
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
            asn_list (list): List of 5 digit AS numbers

        Raises:
            Exception: If an item is not a 5 digit number
        """
        if asn_list is not None and len(asn_list) >= 1:
            for a in asn_list:
                if not re.match("^[0-9]{5}$", a):
                    raise Exception(f"Invalid AS number format : {a}. Must be a 5 digit number.")
            self.__asn_filter = " and path (" + "|".join(asn_list) + ")"
        else:
            self.__asn_filter = ""

    def __setCollectors(self, collectors):
        pass

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

    def __check_filters(self, country_code):
        return not (self.__countries_filter is not None and country_code not in self.__countries_filter)

    def __jprint(self, e):
        """Print a BGPElem to json output file

        Parameters:
            e (BGPElem)
        """

        country_code = self.__country_by_prefix(e._maybe_field("prefix"))
        if not self.__check_filters(country_code):
            return

        res = {
            "type": e.type,
            "time": e.time,
            "peer": e.peer_address,
            "peer_asn": e.peer_asn,
            "collector": e.collector,
        }

        if e.type in ["A", "R", "W"]:  # updateribs
            res["prefix"] = e._maybe_field("prefix")
            res["country_code"] = country_code
        if e.type in ["A", "R"]:  # updateribs
            res["as-path"] = e._maybe_field("as-path")
            res["next-hop"] = e._maybe_field("next-hop")
        elif e.type == "S":  # peer state
            res["old-state"] = e._maybe_field("old-state")
            res["new-state"] = e._maybe_field("new-state")

        self.__json_out.write(json.dumps(res) + ",")

    def __print_queue(self):
        while self.__isStarted or self.__queue.qsize():
            self.__jprint(self.__queue.get())
            self.__queue.task_done()

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def start(self):
        """Start retrieving stream/records and filtering them
        Load Geo Open database
        Start stream with args
        Print each record as JSON format
        """
        self.__isStarted = True
        self.__json_out.write('{"data":[')

        self.__f_country = maxminddb.open_database(self.__f_country_path)
        print(f"Loaded Geo Open database : {self.__f_country_path}")

        if self.__isRecord:
            self._stream = pybgpstream.BGPStream(
                collectors=["route-views.sg", "route-views.eqix"],
                from_time=self.start_time,
                until_time=self.end_time,
                filter="type updates and elemtype announcements withdrawals" + self.__asn_filter,
            )
        else:
            print("Loading live stream ...")
            self._stream = pybgpstream.BGPStream(
                project="ris-live",
                collectors=["rrc00"],
                filter="type updates and elemtype announcements withdrawals" + self.__asn_filter,
            )
        if self.__cidr_match_type_filter is not None:
            self._stream._maybe_add_filter(self.__cidr_match_type_filter, None, self.__cidr_filter)
        print("Starting stream")

        threading.Thread(target=self.__print_queue, daemon=True, name="BGPFilter output").start()

        for elem in self._stream:
            self.__queue.put(elem)

    def stop(self):
        """
        Stop BGPStream
            Close JSON output file
        """
        if self.__isStarted:
            self.__isStarted = False
            self.__queue.join()

            print(self.__queue.qsize())
            print("Finishing queue ...")
            if self.__json_out != sys.stdout:
                with open(self.__json_out.name, "a+") as f:
                    f.seek(f.tell() - 1, os.SEEK_SET)
                    f.truncate()
                    f.write("]}")
                    f.seek(0, os.SEEK_SET)
                    js = json.load(f)
                    f.seek(0, os.SEEK_SET)
                    f.truncate()
                    f.write(json.dumps(js, sort_keys=True, indent=4))
            print("Stream ended")
            exit(0)
