#!/usr/bin/env python
import sys, getopt, pybgpstream, maxminddb, json
from sys import prefix
from termcolor import cprint
import argparse

country_file = "mmdb_files/latest.mmdb"
json_out = ""
start_time = ""
end_time = ""
isRecord = False


def pprint(e, f, f_json):
    f_json.write(
        json.dumps(
            {
                "time": e.time,
                "type": e.type,
                "peer": e.peer_address,
                "peer_number": e.peer_asn,
                "prefix": e._maybe_field("prefix"),
                "country": f.get(e._maybe_field("prefix").split("/", 1)[0]),
            }
        )
    )
    # print(e.fields)


def main(argv):
    global country_file, start_time, end_time, isRecord

    parser = argparse.ArgumentParser(description="Tool for BGP filtering")
    parser.add_argument(
        "-p", "--prefix", action="store_true", help="Filter using specified prefix"
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
    )
    parser.add_argument(
        "--until_time",
        help="Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00",
    )
    parser.add_argument(
        "--country_file",
        nargs="?",
        default="mmdb_files/latest.mmdb",
        help="MMDB Geo Open File which specify IP address geolocation per country. If not set, default file will be used",
    )
    parser.add_argument(
        "--json_output_file",
        nargs="?",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="File in which to display JSON output. If not set, default sys.stdout will be used",
    )

    args = parser.parse_args()
    print(args)


"""
    if isRecord:
        if not (start_time != end_time != ''):
            cprint('--until_time and --from_time parameters are required when using record mode', 'red')
            print_help()
            return

    f_country = maxminddb.open_database(country_file)
    print(f'Loaded MMDB country by ip file : {country_file}')

    try:
        f_json = open(json_out, 'w')
    except:
        f_json = sys.stdout


    if isRecord:
        print('Loading records ...')
        stream = pybgpstream.BGPStream(collectors=["route-views.sg", "route-views.eqix"], record_type="updates", from_time=start_time, until_time=end_time)
    else:
        print('Loading live stream ...')
        stream = pybgpstream.BGPStream(project="ris-live", collectors=[], record_type="updates")

    for elem in stream:
        pprint(elem,f_country,f_json)


"""
if __name__ == "__main__":
    main(sys.argv[1:])
