# BGP-filter

## Usage

~~~~shell
usage: bgp-filter.py [-h] [-v] [--country_file [COUNTRY_FILE]] [-jf [JSON_OUTPUT_FILE]] [-cf COUNTRY_FILTER [COUNTRY_FILTER ...]]
                     [-af ASN_FILTER [ASN_FILTER ...]] [-pf] [-cl CIDR_LIST [CIDR_LIST ...]] [--match {exact,less,more,any}] [-p {ris,routeviews}]
                     [-c COLLECTORS [COLLECTORS ...]] [-r] [--until_time UNTIL_TIME] [--from_time FROM_TIME]

Tool for BGP filtering

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program\'s version number and exit

  --country_file [COUNTRY_FILE]
                        MMDB Geo Open File which specify IP address geolocation per country. If not set, default file will be used
  -jf [JSON_OUTPUT_FILE], --json_output_file [JSON_OUTPUT_FILE]
                        File in which to display JSON output. If not set, default sys.stdout will be used

  -cf COUNTRY_FILTER [COUNTRY_FILTER ...], --country_filter COUNTRY_FILTER [COUNTRY_FILTER ...]
                        Filter using specified country codes.
  -af ASN_FILTER [ASN_FILTER ...], --asn_filter ASN_FILTER [ASN_FILTER ...]
                        Filter using specified AS number list, skip a record if its as-path doesn\'t contain one of specified AS numbers

  -pf, --cidr_filter    Filter using specified cidr list. Keep records that match to one of specified cidr
  -cl CIDR_LIST [CIDR_LIST ...], --cidr_list CIDR_LIST [CIDR_LIST ...]
                        List of cidr. Format: ip/subnet | Example: 130.0.192.0/21,130.0.100.0/21
  --match {exact,less,more,any}
                        Type of match -> exact: Exact match | less: Exact match or less specific | more: Exact match or more specific

  -p {ris,routeviews}, --project {ris,routeviews}
                        Project name
  -c COLLECTORS [COLLECTORS ...], --collectors COLLECTORS [COLLECTORS ...]
                        Collectors. For complete list of collectors, see https://bgpstream.caida.org/data

  -r, --record          Retrieve records in the interval --until_time and --from-time arguments (which are required)
  --until_time UNTIL_TIME
                        Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00
  --from_time FROM_TIME
                        Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00

~~~~

## TODO

- [X] Initial script based on stream retrieve or records
- [X] Country lookup using [geo open file](https://data.public.lu/en/datasets/geo-open-ip-address-geolocation-per-country-in-mmdb-format/)
- [X] Save json output file option
- [X] Add .gitignore
- [X] Use argparse
- [X] Create lib to centralize filtering
- [ ] Add test cases
- [X] Reformat code using [black](https://black.readthedocs.io/en/stable/getting_started.html)
- [X] Auto reformat using [pre-commit](https://pre-commit.com/)
- [X] CIDR block, ASN, country, etc... filtering options
- [X] collector/project options ?
- [X] Output more data results
- [X] Correct interrupt of the program (CTRL + C -> clean json ending)
- [X] Generate requirements.txt

## Exemple of Use

Filter that exact match 84.205.67.0/24 or 41.244.223.0/24 as source AS

~~~shell
python3 bgp-filter.py -pf --cidr_list 84.205.67.0/24 41.244.223.0/24 --match exact -jf res.json
~~~

Retrieve records instead of live stream

~~~shell
python3 bgp-filter.py --record --from_time "2022-01-01 10:00:00" --until_time "2022-01-01 10:10:00"
~~~

Specify a project / list of collectors :

~~~shell
python3 bgp-filter.py -p routeviews --collectors route-views.bdix --from_time "2022-01-01 10:00:00" --until_time "2022-01-01 10:10:00"
~~~~

Output result to result.json

~~~shell
python3 bgp-filter.py -jf result.json`
~~~

If you wan't a human readable result, don't forget to reformat your file :

~~~shell
cat result.json | python3 -mjson.tool > clean_result.json
~~~

## Installation

1. [libBGPStream](https://bgpstream.caida.org/docs/install/bgpstream) must be installed prior to installing PyBGPStream

2. Install requirements
~~~shell
pip3 install -r requirements.txt
~~~

## Output

- `type`
  - R: RIB table entry
  - A: prefix announcement
  - W: prefix withdrawal
  - S: peer state change
- `time` : Timestamp
- `peer` : The IP address of the peer that this element was received from.
- `peer_asn`: The ASN of the peer that this element was received from.
- `collector`: The name of the collector that generated this element.
- `prefix` : The prefix of the source ASN that this element was generated from. [A and W types]
- `country_code`: The country of the source ASN that this element was generated from. [A and W types]
- `next-hop`: The next-hop IP address [A type]
- `as-path`: String list separated by spaces of AS numbers, ordered by the near peer ASN to the source ASN. Therefore, Source ASN is at the end of the string. [A type]

## Example of data output

~~~~json
{"data":[
  {
    "type": "A",
    "time": 1438415400.0,
    "peer": "202.79.197.159",
    "peer_asn": 24482,
    "collector": "route-views.sg",
    "prefix": "216.205.248.0/22",
    "country_code": "US",
    "as-path": "24482 6453 3356 20374 20374 20374 20374 20374",
    "next-hop": "202.79.197.159"
  },
  ...
]
~~~~

See [BGPElem](https://bgpstream.caida.org/docs/api/pybgpstream/_pybgpstream.html#bgpelem) for more details.

## Sources

- Wikipedia [EN](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- Wikipedia [FR](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)
- [BGPStream Filtering](<https://github.com/CAIDA/libbgpstream/blob/master/FILTERING>)
- [BGPStream python library](<https://bgpstream.caida.org/docs/api/pybgpstream>)
- [Data sources](<https://bgpstream.caida.org/data>)
