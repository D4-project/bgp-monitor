#!/usr/bin/env python
import sys
import argparse



if __name__ == "__main__":
    global country_file, start_time, end_time, isRecord

    parser = argparse.ArgumentParser(description="Tool for BGP filtering")
    parser.add_argument(
        "-p", "--prefix", action="store_true", help="Filter using specified prefix"
    )
    parser.add_argument('-v','--version',action='version', version='%(prog)s 1.0')
    parser.add_argument(
        "-r",
        "--record",
        action="store_true",
        help="Retrieve records in the interval --until_time and --from-time arguments (which are required)",
    )
    parser.add_argument(
        "--from_time",
        nargs=1,
        help="Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00",
    )
    parser.add_argument(
        "--until_time",
        nargs=1,
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
