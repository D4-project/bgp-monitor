
#!/usr/bin/env python
import sys, getopt, pybgpstream, maxminddb, json
from sys import prefix
from termcolor import colored, cprint

country_file = 'mmdb_files/latest.mmdb'
start_time = ""
end_time = ""
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
            
            -c, --country_file      MMDB Geo Open File which specify IP address geolocation per country
                                    If not set, default file will be used''')

def pprint(elem, country):
    print(json.dumps({'type': elem.type, 'peer': elem.peer_address, 'peer_number': elem.peer_asn, 'country': country}))#'fields': elem.fields, 

def main(argv):
    global country_file, start_time, end_time, isRecord
    
    try:
        opts, args = getopt.getopt(argv, "hprc", ["record",'from_time','until_time','country_file','prefixes'])
    except getopt.GetoptError as err:
        cprint('Unrecognized parameter', 'red')
        print_help()
        return

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            return
        if opt in ('-r', '--record'):
            isRecord = True
            if '--until_time' or '--from_time' not in opts:
                cprint('--until_time and --from_time parameters are required when using record mode', 'red')
                print_help()
                return
        if opt in ('-c', '--country_file='):
            country_file = arg
        if opt in ('-p', '--prefix='):
            prefix = arg
        if opt == '--from_time':
            start_time = arg
        if opt == '--until_time':
            end_time = arg

    print(opts)


    # Load AS\Country File
#    f = maxminddb.open_database(country_file)

    if isRecord:
        stream = pybgpstream.BGPStream(project="ris-live", record_type="updates", from_time=start_time, until_time=end_time)
        for record in stream.records:
            pprint(record,3)# f.get(record.fields["prefix"]))
    else:
        # Start live BGP Stream
        stream = pybgpstream.BGPStream(project="ris-live", record_type="updates")
        print("dwwede")
        for elem in stream:
            print("fwef")
            print(elem)# f.get(record.fields["prefix"]))


if __name__ == '__main__':
    main(sys.argv[1:])
