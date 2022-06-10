#!/usr/bin/env python3
"""
Main execution, handle arguments, init each instances
"""

import os
import signal
import bgpout
import argparse
import configparser

from bgpfilter import BGPFilter

os.chdir(os.path.dirname(os.path.abspath(__file__)))
configPath = "../etc/config.cfg"


def asnPrefixFromFile(file):
    """Read prefixes and AS numbers from files

    Args:
        file (File): File that contains as numbers and prefixes

    Returns:
        Dict: Dictionnary with prefix_list, asn_list, match type
    """
    res = {"asn_list": [], "prefix_list": [], "match": "more"}

    for line in file.read().splitlines():
        if len(line) > 0:
            splitted_line = line.split()
            if splitted_line[0] == ">":
                res["prefix_list"].append(splitted_line[1])
            elif splitted_line[0] == "AS":
                res["asn_list"].append(splitted_line[1])
            elif splitted_line[0] == "MATCH":
                res["match"] = splitted_line[1]
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tool for BGP filtering and monitoring",
        allow_abbrev=True,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument(
        "--verbose", action="store_true", help="Print BGP records in console"
    )

    parser.add_argument(
        "--filter_list",
        type=argparse.FileType("r"),
        nargs="?",
        help=(
            "Use separated file to define list of prefixes and/or AS Numbers.\n Check"
            " etc/filter_list.cfg.sample for file format"
        ),
        metavar="<path>",
    )

    parser.add_argument(
        "-jo",
        "--json_output",
        nargs="?",
        type=argparse.FileType("w+"),
        help=(
            "File in which to display JSON output.\n If not set, default sys.stdout"
            " will be used."
        ),
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
        help=(
            "Filter using specified AS number list, skip a record if its AS-source is"
            " not one of specified AS numbers.\n Use _ symbol for negation"
        ),
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
        "--prefix_filter",
        nargs="+",
        help=(
            "Filter using specified prefix list, CIDR format: ip/subnet.\n Example:"
            " 130.0.192.0/21,130.0.100.0/21"
        ),
        metavar="<prefix>",
    )

    parser.add_argument(
        "--match",
        default="more",
        choices=["more", "less", "exact", "any"],
        help=(
            "Type of match ->"
            "exact: Exact match\n"
            "more: Exact match or more specific (Contained by one of the prefixes)\n"
            "less: Exact match or less specific (Contain one of the prefixes).\n"
            "Default: more"
        ),
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
        help=(
            "Collectors. For complete list of collectors, see"
            " https://bgpstream.caida.org/data"
        ),
        metavar="<collector>",
    )

    parser.add_argument(
        "-r",
        "--record",
        action="store_true",
        help=(
            "Retrieve records in the interval --until_time and --f-time arguments"
            " (which are required)"
        ),
    )
    parser.add_argument(
        "--start",
        help=(
            "Beginning of the interval.\n  -> Timestamp format : YYYY-MM-DD hh:mm:ss.\n"
            "     Example: 2022-01-01 10:00:00"
        ),
        metavar="<begin>",
    )
    parser.add_argument(
        "--stop",
        help=(
            "End of the interval.\n  -> Timestamp format : YYYY-MM-DD hh:mm:ss.\n    "
            " Example: 2022-01-01 10:10:00"
        ),
        metavar="<end>",
    )

    parser.add_argument(
        "--queue",
        action="store_true",
        help="Enable queue option. Use a lot of memory",
    )

    parser.add_argument(
        "-id",
        "--input_data",
        type=str,
        help="Retrieve data from a single file instead of a broker.",
        metavar="<path>",
    )

    parser.add_argument(
        "-ir",
        "--input_record_type",
        choices=["upd", "rib"],
        default="upd",
        help=(
            "Type of records contained in input_data file.\n Can be rib (Routing"
            " Information Base) or upd (Updates eg. Anoun/Withdr).\n Default: upd"
        ),
    )

    parser.add_argument(
        "-if",
        "--input_file_format",
        choices=["mrt", "bmp", "ris-live"],
        default="mrt",
        help="input data type format. ris-live is avaible for updates only",
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

    if args.input_data and (
        args.input_file_format is None or args.input_record_type is None
    ):
        parser.error(
            "--input_data requires --input_file_format and --input_record_type."
        )
    if args.expected_result is not None and args.json_output is None:
        parser.error("--expected_result requires --json_output")

    # config
    if os.path.isfile(configPath):
        config = configparser.ConfigParser()
        config.read(configPath)
    else:
        raise FileNotFoundError(f"[-] No conf file found at {configPath}")

    # BGPStream filter
    filter = BGPFilter()

    filter.project = args.project  # ris / routeviews
    filter.collectors = args.collectors  # there are many collectors
    filter.countries_filter = args.country_filter  # Country codes
    filter.ipversion = args.ipversion  # 4 / 6

    filter.record_mode(args.record, args.start, args.stop)
    if args.input_data:
        filter.data_source(
            args.input_record_type, args.input_file_format, args.input_data
        )

    if "geoopen" in config:
        filter.country_file = config["geoopen"]["path"]

    if args.filter_list is not None:
        res = asnPrefixFromFile(args.filter_list)
        filter.prefix_filter = (
            res["prefix_list"] + (args.prefix_filter or []),
            args.match,
        )
        filter.asn_filter = res["asn_list"] + (args.asn_filter or [])
    else:
        filter.asn_filter = args.asn_filter  # asn list
        filter.prefix_filter = (args.prefix_filter, args.match)

    # Output
    bout = bgpout.BGPOut()
    bout.json_out = args.json_output
    bout.expected_result = args.expected_result
    bout.queue = args.queue  # Boolean
    bout.verbose = args.verbose

    filter.out = bout

    # end of program
    def stop(x, y):
        filter.stop()

    signal.signal(signal.SIGINT, stop)
    filter.start()
    filter.stop()
