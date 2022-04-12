#!/usr/bin/env python

import signal
import sys
import atexit
import argparse
import bin.BGPFilter


if __name__ == "__main__":
    global country_file, start_time, end_time, isRecord

    parser = argparse.ArgumentParser(description="Tool for BGP filtering")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument(
        "-r",
        "--record",
        action="store_true",
        help="Retrieve records in the interval --until_time and --from-time arguments (which are required)",
    )
    parser.add_argument(
        "--from_time",
        type=str,
        help="Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00",
    )
    parser.add_argument(
        "--until_time",
        type=str,
        help="Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00",
    )
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
        "-pf",
        "--cidr_filter",
        type=str,
        help="Filter using specified cidr. Keep records that exactly match to specified cidr. Format: ip/subnet | Example: 130.0.192.0/21",
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

    args = parser.parse_args()
    print(args)

    filter = bin.BGPFilter.BGPFilter()
    filter.json_out = args.json_output_file
    filter.countries_filter = args.country_filter
    filter.asn_filter = args.asn_filter
    filter.cidr_filter = args.cidr_filter
    filter.set_record_mode(args.record, args.from_time, args.until_time)

    def stop(x, y):
        filter.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    filter.start()
