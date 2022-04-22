#!/usr/bin/env python

import os
import signal
import argparse
import configparser
import redis
from yaml import parse
from secrets import choice
import BGPFilter

configPath = "../etc/ail-feeder-bgp.cfg"

if __name__ == "__main__":

    # args
    parser = argparse.ArgumentParser(description="Tool for BGP filtering and feeding")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")

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
    
    parser.add_argument('--nocache', action='store_true', help='Disable caching')

    args = parser.parse_args()
    if args.record and (args.from_time is None or args.until_time is None):
        parser.error("--record requires --from_time and --until_time.")

    if args.cidr_filter and (args.match is None or args.match is None):
        parser.error("--cidr_filter requires --match and --cidr_list.")

    filter = BGPFilter.BGPFilter()
    filter.countries_filter = args.country_filter
    filter.asn_filter = args.asn_filter
    filter.set_cidr_filter(args.cidr_filter, args.match, args.cidr_list)

    filter.project = args.project
    filter.collectors = args.collectors
    filter.set_record_mode(args.record, args.from_time, args.until_time)

    # config
    if os.path.isfile(configPath):
        config = configparser.ConfigParser()
        config.read(configPath)
    else:
        raise FileNotFoundError("[-] No conf file found")

    filter.nocache = args.nocache
    if not filter.nocache:
        # redis
        host, port, db = (
            (config["redis"]["host"], config["redis"]["port"], config["redis"]["db"])
            if "redis" in config
            else ("localhost", 6379, 0)
        )
        filter.redis_db = redis.Redis(host=host, port=port, db=db)

    if "cache" in config:
        filter.cache_expire = int(config["cache"]["expire"])
    elif not args.nocache:
        filter.cache_expire = 86400

    # ail
    if "ail" in config:
        filter.ail = (config["ail"]["url"], config["ail"]["apikey"], config["general"]["uuid"])

    if 'geoopen' in config:
        filter.country_file = config['geoopen']['path']

    def stop(x, y):
        filter.stop()

    signal.signal(signal.SIGINT, stop)
    filter.start()
    filter.stop()
