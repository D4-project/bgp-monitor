"""
Contains a whole class and methods that retrieves bgp records filtered by prefixes,
 as numbers, countries, etc ...
"""

__all__ = ["BGPFilter"]

import os
import re
import sys
import time
import json
import bgpout
import datetime
import ipaddress
import maxminddb
import pycountry
import pybgpstream
import urllib.request
from typing import List, Tuple


def get_collectors():
    """Query the BGPStream broker and identify the collectors that are available"""
    data = json.load(urllib.request.urlopen(COLLECTORS_URL))
    result = dict((x, []) for x in PROJECTS)
    for coll in data["data"]["collectors"]:
        p = data["data"]["collectors"][coll]["project"]
        if p in PROJECTS:
            result[p].append(coll)
    return result


PROJECT_TYPES = {"ris": "ris-live", "routeviews": "routeviews-stream"}
PROJECTS = [i for i in PROJECT_TYPES.keys()]
COLLECTORS_URL = "https://broker.bgpstream.caida.org/v2/meta/collectors"
COLLECTORS = get_collectors()


class BGPFilter:
    """
    BGP stream filter
    """

    def __init__(self):
        self.__isRecord = False
        self.__start_time = ""
        self.__end_time = ""
        self.__asn_filter = None
        self.__ipversion = ""
        self.__prefix_filter = None
        self.__asn_list = None
        self.__prefix_match_type_filter = None
        self.__project = PROJECTS[0]
        self.__collectors = None
        self.__data_source = {"source_type": "broker"}
        self.out: bgpout.BGPOut = None
        """`bgpout.BGPOut()` instance that will receive all records"""
        # multiprocessing.set_start_method("fork")
        # self.queue = faster_fifo.Queue()
        # self.process = multiprocessing.Process(
        # target=self.process, args=(self.queue,
        # ), daemon=True)

    ###############
    #   GETTERS   #
    ###############

    @property
    def isRecord(self) -> bool:
        """Retrieve in past or in live mode.
        see `BGPFilter.record_mode()`"""
        return self.__isRecord

    @property
    def start_time(self) -> str:
        """Start of the interval for record mode.
        see `BGPFilter.record_mode()`"""
        return self.__start_time

    @property
    def end_time(self) -> str:
        """End of the interval for record mode.
        see `BGPFilter.record_mode()`"""
        return self.__end_time

    @property
    def prefix_filter(self) -> List[str]:
        """List of prefixes (CIDR format) to filter"""
        return self.__prefix_filter

    @property
    def asn_filter(self) -> List[str]:
        """List of AS numbers"""
        return self.__asn_list

    @property
    def collectors(self) -> List[str]:
        """List of collectors to list"""
        return self.__collectors

    @property
    def project(self) -> str:
        """Accepted project : `ris` or `routeviews`"""
        return self.__project

    @property
    def ipversion(self) -> str:
        """
        Formatted string for ip version filtering.

        Accepted versions : `4` or `6`
        """
        return self.__ipversion

    ###############
    #   SETTERS   #
    ###############

    def record_mode(self, isRecord, start, end):
        """
        Define if retrieve from an interval or live stream
            start and end won't be modified if isRecord is False

        Args:
            - isRecord (bool) : record or live mode
            - start (string): Beginning of the interval.

                Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00

            - end (string): End of the interval.

                Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00

        Raises:
            - ValueError: Start > End
            - ValueError: Start or end not defined
            - ValueError: Invalid date format
        """
        self.__isRecord = isRecord
        if isRecord:
            if start is None or end is None:
                raise ValueError(
                    "Record mode requires the from_time and until_time arguments"
                )
            try:
                st = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                en = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(
                    "Invalid record mode date format. Must be %Y-%m-%d %H:%M:%S"
                )
            if st > en:
                raise ValueError(
                    "Invalid record mode interval. Beginning must precede the end"
                )

            self.__start_time = start
            self.__end_time = end
        else:
            self.__start_time = int(time.time())
            self.__end_time = 0

    def data_source(self, record_type: str, file_format: str, file_path: str):
        """
        Use single file as data source

        Args:
            record_type (str): Type of records stored in the file (rib or upd)
            file_format (str): Format of the file (mrt, bmp or ris-live)
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
            raise ValueError(
                "Accepted input format types for upd : mrt, bmp or ris-live"
            )
        self.__data_source = {
            "source_type": record_type,
            "file_format": file_format,
            "file_path": file_path,
        }

    @prefix_filter.setter
    def prefix_filter(self, values: Tuple[List[str], str]):
        """
        Prefix filter option
            Keep records that match to one of specified prefixes (cidr format).

        Args:
            prefix_list (List[string]):  Format: ip/subnet | Example: 130.0.192.0/21
            match_type (string): Type of match
                exact: Exact match
                less: Exact match or less specific (contained by)
                more: Exact match or more specific (contains)
                any: less and more
        """
        try:
            cidr_list, match_type = values
        except ValueError:
            raise ValueError(
                "match type and prefixes list are required for filtering by prefixes"
            )
        if cidr_list is not None:
            if len(cidr_list) == 0:
                # "Please specify one or more prefixes when filtering by prefix"
                return
            if match_type not in ["exact", "less", "more", "any"]:
                raise ValueError(
                    "Match type must be specified and one of ['exact', 'less', 'more',"
                    " 'any']"
                )
            for c in cidr_list:
                ipaddress.ip_network(c)
            self.__prefix_match_type_filter = match_type
            self.__prefix_filter = cidr_list

    @asn_filter.setter
    def asn_filter(self, asn_list):
        """Filter using specified AS number list
            Skip a record if its source-AS is not one of specified AS numbers
            Use _ symbol for negation

        Args:
            asn_list (list): List of AS numbers
        """
        self.__asn_filter = ""
        f_list = []
        not_f_list = []
        if asn_list is not None and len(asn_list) >= 1:
            self.__asn_list = []
            for i in asn_list:
                if re.match("_[0-9]+", i):
                    not_f_list.append(i.replace("_", ""))
                    self.__asn_list.append(i)
                elif re.match("[0-9]+", i):
                    f_list.append(i)
                    self.__asn_list.append(i)

            if len(f_list) >= 1:
                self.__asn_filter += " and path (_" + "|_".join(f_list) + ")$"
            if len(not_f_list) >= 1:
                self.__asn_filter = " and path !(_" + "|_".join(not_f_list) + ")$"

    @collectors.setter
    def collectors(self, collectors):
        if collectors is not None:
            for c in collectors:
                if c not in COLLECTORS[self.__project]:
                    raise ValueError("Collector isn't available or isn't valid.")
            self.__collectors = collectors

    @project.setter
    def project(self, project: str):
        """
        Args:
            project (string): ris or routesviews
        """
        if self.__collectors != project and project in PROJECT_TYPES.keys():
            self.__project = project
            self.__collectors = None
        else:
            raise ValueError(
                f"Invalid project name. Valid projects list : {PROJECT_TYPES.keys()}"
            )

    @ipversion.setter
    def ipversion(self, version):
        """Set string for filter field

        Args:
            version (Integer): Possible values ["4" or "6"]
        """
        self.__ipversion = " and ipversion " + version if version in ["4", "6"] else ""

    ###############
    #             #
    ###############

    @property
    def country_file(self) -> str:
        """Path to the Geo Open MaxMindDB File"""
        return self.__f_country_path

    @property
    def countries_filter(self) -> List[str]:
        """
        List of country codes to filter

        Filter using specified country.
            Keep records that the origin of their prefix is contained in country_list.

        Args:
            country_list (List[str]): List of country codes

        Raises:
            LookupError: If an element in country_list is not valid.
        """
        return self.__countries_filter

    @countries_filter.setter
    def countries_filter(self, country_list: List[str]):
        """
        Filter using specified country.
            Keep records that the origin of their prefix is contained in country_list.

        Args:
            country_list (List[str]): List of country codes

        Raises:
            LookupError: If an element in country_list is not valid.
        """
        if country_list is not None:
            for c in country_list:
                pycountry.countries.lookup(c)
        self.__countries_filter = country_list

    @country_file.setter
    def country_file(self, country_file_path: str):
        """
        Setter for the GeoOpen country mmdb file

        Args:
            country_file_path (String): Path to Geo Open MaxMindDB File
        """
        if not os.path.isfile(country_file_path):
            raise FileNotFoundError
        self.__f_country_path = country_file_path

        self.__f_country_path = "../mmdb_files/latest.mmdb"
        self.__countries_filter = None

        self.__f_country = maxminddb.open_database(
            self.__f_country_path, maxminddb.MODE_MMAP_EXT
        )
        print(f"Loaded Geo Open database : {self.__f_country_path}")

    def __check_country(self, e):
        """
        Args:
            e (bgp dict)


        Returns:
            boolean: if e.["country code"] is in self.__countries_filter list
        """
        return not (
            self.__countries_filter is not None
            and e["country_code"] not in self.__countries_filter
        )

    def __country_by_prefix(self, p):
        """
        Parameters:
            p (prefix): CIDR format. Example: 130.0.192.0/21

        Returns:
            string: country code of the given prefix.
                None if not found in GeoOpen database
        """
        if p is None:
            return None
        else:
            r = self.__f_country.get(p.split("/", 1)[0])
            return None if r is None else r["country"]["iso_code"]

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def _build_stream(self):
        """Build the stream with the used filters

        Returns:
            (BGPStream)
        """
        self._stream = pybgpstream.BGPStream(
            from_time=self.start_time,
            until_time=self.end_time,
            data_interface=(
                "broker"
                if self.__data_source["source_type"] == "broker"
                else "singlefile"
            ),
            record_type="updates",
            filter="elemtype announcements withdrawals"
            + self.__asn_filter
            + self.__ipversion,
        )

        if self.__prefix_match_type_filter is not None:
            self._stream._maybe_add_filter(
                "prefix-" + self.__prefix_match_type_filter, None, self.__prefix_filter
            )

        if self.__data_source["source_type"] != "broker":
            self._stream.set_data_interface_option(
                "singlefile",
                self.__data_source["source_type"] + "-file",
                self.__data_source["file_path"],
            )
            self._stream.set_data_interface_option(
                "singlefile",
                self.__data_source["source_type"] + "-type",
                self.__data_source["file_format"],
            )
        else:
            project = (
                self.__project if self.__isRecord else PROJECT_TYPES[self.__project]
            )
            self._stream._maybe_add_filter("project", project, None)
            self._stream._maybe_add_filter("collector", None, self.__collectors)

        if self.__isRecord:
            self._stream.stream.set_live_mode()
        return self._stream

    def cpt_update(self):
        """For debugging. Print time each 100000 elem"""
        if not hasattr(self, "timer"):
            self.timer = {"cpt": 0, "tmp": None, "ft": time.time(), "ot": time.time()}
        self.timer["cpt"] += 1
        if self.timer["cpt"] % 100000 == 0:
            self.timer["nt"] = time.time()
            print(
                f'Counter : {self.timer["cpt"]} '
                '- Time {self.timer["nt"] - self.timer["ft"]} '
                '- {self.timer["nt"] - self.timer["ot"]}s',
                file=sys.stderr,
            )
            # sys.stderr.write(f"Queue size : {self.queue.qsize()}")
            self.timer["ot"] = self.timer["nt"]

    def start(self):
        """
        Start retrieving stream/records and filtering them
        - Load Geo Open database
        - Start stream with args
        - Print each record as JSON format
        """

        print("Loading stream...")
        self._build_stream()
        print("Starting")
        self.isStarted = True

        for e in self._stream:
            self.cpt_update()

            msg = {
                "type": e.type,
                "time": e.time,
                "peer_address": e.peer_address,
                "peer_asn": e.peer_asn,
                "collector": e.collector,
                "record_type": e.record_type,
                "project": e.project,
                "router": e.router,
                "router_ip": e.router_ip,
            }
            msg |= e.fields
            msg["country_code"] = self.__country_by_prefix(msg["prefix"])
            msg["source"] = msg["as-path"].split()[-1] if "as-path" in msg else None

            self.out.iteration(msg)

    def stop(self):
        """
        Close JSON output file and stop BGPStream
        """
        print("Stream ended")
        self.out.stop()
        exit(0)
