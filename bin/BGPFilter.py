import ipaddress
from multiprocessing.connection import wait
import os
import re
import sys
import json
import threading
from time import sleep
from uuid import UUID
import maxminddb
import pycountry
import pybgpstream

from pyail import PyAIL
from queue import Queue
from urllib import request
from datetime import datetime
from pytz import country_names

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
        self.__cidr_filter = None
        self.__cidr_match_type_filter = None
        self.__queue = Queue()
        self.__project = list(project_types.keys())[0]
        self.__collectors = None
        self.__redis = None
        self.__ail = None
        self.__source_uuid = None

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
    def project(self):
        return self.__project

    @property
    def redis_db(self):
        return self.__redis

    @property
    def ail(self):
        return self.__ail

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
                raise ValueError("Invalid record mode interval. Beginning must ")

            self.__start_time = start
            self.__end_time = end

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
                ipaddress.ip_network(c)
                # if not re.match(r"^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))$", c):
                #    raise Exception(f"Invalid CIDR format : {c}")
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
        return

    def __bgp_json(self, e):
        """Return a BGPElem as json

        Parameters:
            e (BGPElem)
        """
        country_code = self.__country_by_prefix(e._maybe_field("prefix"))
        if self.__countries_filter is not None and country_code not in self.__countries_filter:
            return

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

        return json.dumps(data, sort_keys=True, indent=4)

    def __redis_save(self):
        """
        Save a bgp elem to redis
        """
        pass

    def __print_queue(self):
        """Iterate over queue to process each bgp element"""
        while self.__isStarted or self.__queue.qsize():
            e = self.__queue.get()
            self.__ail.feed_json_item(
                str(e.time) + str(e.peer_asn), self.__bgp_json(e), "ail_feeder_bgp", self.__source_uuid
            )
            print(self.__queue.qsize())
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

        self.__f_country = maxminddb.open_database(self.__f_country_path)
        print(f"Loaded Geo Open database : {self.__f_country_path}")
        print(f"Loading {project_types[self.__project]} live stream ...")

        self._stream = pybgpstream.BGPStream(
            project=(self.__project if self.__isRecord else project_types[self.__project]),
            collectors=self.__collectors,
            from_time=(self.start_time if self.__isRecord else None),
            until_time=(self.end_time if self.__isRecord else None),
            record_type="updates",
            filter="elemtype announcements withdrawals" + self.__asn_filter,
        )

        if self.__cidr_match_type_filter is not None:
            self._stream._maybe_add_filter(self.__cidr_match_type_filter, None, self.__cidr_filter)

        threading.Thread(target=self.__print_queue, daemon=True, name="BGPFilter output").start()

        print("Starting")
        for elem in self._stream:
            self.__queue.put(elem)

    def stop(self):
        """
        Stop BGPStream
            Close JSON output file
        """
        if self.__isStarted:
            print("Finishing queue ...")
            self.__isStarted = False
            self.__queue.join()
            print("Stream ended")
            exit(0)
