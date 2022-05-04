#!/usr/bin/env python

import os
import signal
import argparse
import configparser
import sys
import BGPFilter
import bgpout

configPath = "../etc/ail-feeder-bgp.cfg"

if __name__ == "__main__":

    # args
    parser = argparse.ArgumentParser(
        description="Tool for BGP filtering and feeding", allow_abbrev=True
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0"
    )

    parser.add_argument(
        "-cf",
        "--country_filter",
        nargs="+",
        help="Filter using specified country codes.",
        metavar="<country code>",
    )
    parser.add_argument(
        "-af",
        "--asn_filter",
        nargs="+",
        help="Filter using specified AS number list, skip a record if its as-path doesn't contain one of specified AS numbers",
        metavar="<AS number>",
    )

    parser.add_argument(
        "-ip",
        "--ipversion",
        choices=["4", "6"],
        help="Filter specific ip address type. ipv4 or ipv6",
        metavar="<version>",
    )

    parser.add_argument(
        "-pf",
        "--cidr_filter",
        action="store_true",
        help="Filter using specified cidr list. Keep records that match to one of specified cidr",
    )
    parser.add_argument(
        "-cl",
        "--cidr_list",
        nargs="+",
        help="List of cidr. Format: ip/subnet | Example: 130.0.192.0/21,130.0.100.0/21",
        metavar="<prefix>",
    )
    parser.add_argument(
        "--match",
        choices=["exact", "less", "more", "any"],
        help="Type of match -> exact: Exact match | less: Exact match or less specific | more: Exact match or more specific",
    )

    parser.add_argument(
        "-p",
        "--project",
        default="ris",
        choices=["ris", "routeviews"],
        help="Project name",
    )
    parser.add_argument(
        "-c",
        "--collectors",
        nargs="+",
        help="Collectors. For complete list of collectors, see https://bgpstream.caida.org/data",
        metavar="<collector>",
    )

    parser.add_argument(
        "-r",
        "--record",
        action="store_true",
        help="Retrieve records in the interval --until_time and --from-time arguments (which are required)",
    )
    parser.add_argument(
        "--from_time",
        help="Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00",
        metavar="<begin>",
    )
    parser.add_argument(
        "--until_time",
        help="Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00",
        metavar="<end>",
    )

    parser.add_argument(
        "--queue",
        action="store_true",
        help="Enable queue option. Use lot a of memory",
    )

    parser.add_argument(
        "--noail",
        action="store_true",
        help="Disable ail publish. Disable caching",
    )

    parser.add_argument(
        "--nocache", action="store_true", help="Disable caching"
    )

    parser.add_argument(
        "-jo",
        "--json_output",
        nargs="?",
        default=sys.stdout,
        type=argparse.FileType("w+"),
        help="File in which to display JSON output. If not set, default sys.stdout will be used.",
    )

    parser.add_argument(
        "--input_data",
        type=str,
        help="Path to a single file instead of broker.",
        metavar="<path>",
    )

    parser.add_argument(
        "--input_record_type",
        choices=["rib", "upd"],
        help="Type of records contained in input_data file. Can be ribs (rib) or updates (upd)",
    )

    parser.add_argument(
        "--input_file_format",
        choices=["mrt", "bmp", "ris-live"],
        default="mrt",
        help="input data type format. ris-live avaible for updates only",
    )

    parser.add_argument(
        "--expected_result",
        "-expected",
        nargs="?",
        type=argparse.FileType("r"),
        metavar="<path>",
        help="Check that the result is the same as the expected result",
    )

    args = parser.parse_args()
    if args.record and (args.from_time is None or args.until_time is None):
        parser.error("--record requires --from_time and --until_time.")

    if args.cidr_filter and (args.match is None or args.cidr_list is None):
        parser.error("--cidr_filter requires --match and --cidr_list.")

    if args.input_data and (
        args.input_file_format is None or args.input_record_type is None
    ):
        parser.error(
            "--input_data requires --input_file_format and --input_record_type."
        )

    if args.json_output == sys.stdout and args.expected_result is not None:
        parser.error("--expected_result requires --json_output")

    # config
    if os.path.isfile(configPath):
        config = configparser.ConfigParser()
        config.read(configPath)
    else:
        raise FileNotFoundError("[-] No conf file found")

    # filter
    filter = BGPFilter.BGPFilter()

    filter.project = args.project  # ris / routeviews
    filter.collectors = args.collectors  # there's many collectors
    filter.countries_filter = args.country_filter  # Country codes
    filter.asn_filter = args.asn_filter  # asn list
    filter.ipversion = args.ipversion  # 4 / 6
    filter.queue = args.queue  # Boolean
    filter.cidr_filter(
        args.cidr_filter, args.match, args.cidr_list
    )  # List of cidr + specficity
    filter.record_mode(
        args.record, args.from_time, args.until_time
    )  # Timestamp for begin and end
    if args.input_data:
        filter.data_source(
            args.input_record_type, args.input_file_format, args.input_data
        )

    # GeoOpen DB
    if "geoopen" in config:
        filter.country_file = config["geoopen"]["path"]

    bout = bgpout.BGPOut()
    bout.json_out = args.json_output
    bout.expected_result = args.expected_result
    bout.nocache = args.nocache

    # redis
    if not args.nocache:
        bout.redis = (
            (
                config["redis"]["host"],
                config["redis"]["port"],
                config["redis"]["db"],
            )
            if "redis" in config
            else ("localhost", 6379, 0)
        )

    # ail
    if not args.no_ail and "ail" in config:
        try:
            bout.ail = (
                config["ail"]["url"],
                config["ail"]["apikey"],
                config["general"]["uuid"],
            )
        except:
            print("Ail won't be used")
    filter.out = bout

    # end of program
    def stop(x, y):
        filter.stop()

    signal.signal(signal.SIGINT, stop)
    filter.start()
    filter.stop()
