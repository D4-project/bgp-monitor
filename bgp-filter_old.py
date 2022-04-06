
#!/usr/bin/env python
import sys, getopt, pybgpstream, maxminddb, json
from sys import prefix
from termcolor import cprint

country_file = 'mmdb_files/latest.mmdb'
json_out = ''
start_time = ''
end_time = ''
isRecord = False


def print_help():
    cprint('''Usage: bgp-filter.py [-h] [-p PREFIX] [-r --until_time=TIMESTAMP --from_time=TIMESTAMP] [-c COUNTRYFILEDB]''', 'green')
    print('''
        Optional arguments:
            -h, --help              Show this help message and exit

            -p, --prefix            Filter using specified prefix

            -r, --record            Retrieve records in the interval --until_time and --from-time arguments (which are required)            
            --from_time             Beginning of the interval.  Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00
            --until_time            Ending of the interval.     Timestamp format : YYYY-MM-DD hh:mm:ss

            --country_file          MMDB Geo Open File which specify IP address geolocation per country
                                    If not set, default file will be used

            --json_output_file      File in which to display JSON output
                                    If not set, default sys.stdout will be used''')


def pprint(e, f, f_json):
    f_json.write(json.dumps({'time':e.time, 'type': e.type, 'peer': e.peer_address, 'peer_number': e.peer_asn, 'prefix': e._maybe_field('prefix'), 'country': f.get(e._maybe_field('prefix').split("/",1)[0])}))
    #print(e.fields)


def main(argv):
    global country_file, start_time, end_time, isRecord

    try:
        opts, args = getopt.getopt(argv, "hpr", ["record",'from_time=','until_time=','country_file=','prefix=','json_output_file='])
    except getopt.GetoptError as err:
        cprint('Unrecognized parameter', 'red')
        print_help()
        return

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            return
        elif opt in ('-r', '--record'):
            isRecord = True
        elif opt == '--country_file':
            country_file = arg
        elif opt in ('-p', '--prefix='):
            prefix = arg
        elif opt == '--from_time':
            start_time = arg
        elif opt == '--until_time':
            end_time = arg
        elif opt == '--json_output_file':
            json_out = arg

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


if __name__ == '__main__':
    main(sys.argv[1:])
