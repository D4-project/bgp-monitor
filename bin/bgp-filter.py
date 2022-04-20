#!/usr/bin/env python

import signal
import sys
import argparse
import configparser

from yaml import parse
from secrets import choice
import bin.BGPFilter


if __name__ == "__main__":

    # config
    config = configparser.ConfigParser()
    config.read("../etc/ail-feeder-bgp.cfg")

    # args
    parser = argparse.ArgumentParser(description="Tool for BGP filtering")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")

    parser.add_argument(
        "--country_file",
        nargs="?",
        default="mmdb_files/latest.mmdb",
        help="MMDB Geo Open File which specify IP address geolocation per country. If not set, default file will be used",
    )
    parser.add_argument(
        "-jf",
        "--json_output_file",
        nargs="?",
        default=sys.stdout,
        type=argparse.FileType("w+"),
        help="File in which to display JSON output. If not set, default sys.stdout will be used",
    )

    parser.add_argument(
        "-cf", "--country_filter", nargs="+", help="Filter using specified country codes."
    )
    parser.add_argument(
        "-af",
        "--asn_filter",
        nargs="+",
        help="Filter using specified AS number list, skip a record if its as-path doesn't contain one of specified AS numbers",
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
    )
    parser.add_argument(
        "--match",
        choices=["exact", "less", "more", "any"],
        help="Type of match -> exact: Exact match | less: Exact match or less specific | more: Exact match or more specific",
    )

    parser.add_argument(
        "-p", "--project", default="ris", choices=["ris", "routeviews"], help="Project name"
    )
    parser.add_argument(
        "-c",
        "--collectors",
        nargs="+",
        help="Collectors. For complete list of collectors, see https://bgpstream.caida.org/data",
    )

    parser.add_argument(
        "-r",
        "--record",
        action="store_true",
        help="Retrieve records in the interval --until_time and --from-time arguments (which are required)",
    )

    parser.add_argument(
        "--until_time",
        help="Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00",
    )
    parser.add_argument(
        "--from_time",
        help="Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00",
    )

    args = parser.parse_args()
    if args.record and (args.from_time is None or args.until_time is None):
        parser.error("--record requires --from_time and --until_time.")

    if args.cidr_filter and (args.match is None or args.match is None):
        parser.error("--cidr_filter requires --match and --cidr_list.")

    filter = bin.BGPFilter.BGPFilter()
    filter.json_out = args.json_output_file
    filter.countries_filter = args.country_filter
    filter.asn_filter = args.asn_filter
    filter.set_cidr_filter(args.cidr_filter, args.match, args.cidr_list)

    filter.project = args.project
    filter.collectors = args.collectors
    filter.set_record_mode(args.record, args.from_time, args.until_time)

    def stop(x, y):
        filter.stop()

    signal.signal(signal.SIGINT, stop)
    filter.start()
    filter.stop()
