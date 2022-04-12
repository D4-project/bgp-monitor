# BGP-filter

BGP filter based on prefixes/network with country lookup

## Usage

~~~~shell
usage: bgp-filter.py [-h] [-v] [-r] [--from_time FROM_TIME] [--until_time UNTIL_TIME] [--country_file [COUNTRY_FILE]] [-jf [JSON_OUTPUT_FILE]] [-pf CIDR_FILTER] [-cf COUNTRY_FILTER [COUNTRY_FILTER ...]]
                     [-af ASN_FILTER [ASN_FILTER ...]]

Tool for BGP filtering

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program\'s version number and exit
  -r, --record          Retrieve records in the interval --until_time and --from-time arguments (which are required)
  --from_time FROM_TIME
                        Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00
  --until_time UNTIL_TIME
                        Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00
  --country_file [COUNTRY_FILE]
                        MMDB Geo Open File which specify IP address geolocation per country. If not set, default file will be used
  -jf [JSON_OUTPUT_FILE], --json_output_file [JSON_OUTPUT_FILE]
                        File in which to display JSON output. If not set, default sys.stdout will be used
  -pf CIDR_FILTER, --cidr_filter CIDR_FILTER
                        Filter using specified cidr. Keep records that exactly match to specified cidr. Format: ip/subnet | Example: 130.0.192.0/21
  -cf COUNTRY_FILTER [COUNTRY_FILTER ...], --country_filter COUNTRY_FILTER [COUNTRY_FILTER ...]
                        Filter using specified country codes.
  -af ASN_FILTER [ASN_FILTER ...], --asn_filter ASN_FILTER [ASN_FILTER ...]
                        Filter using specified AS number list, skip a record if its as-path doesn't contain one of specified AS numbers
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
- [ ] collector/project options ?
- [X] Output more data results
- [X] Correct interrupt of the program (CTRL + C -> clean json ending)
- [X] Generate requirements.txt

## Exemple of Use

## Requirements

- [MaxMindDB Library](https://github.com/maxmind/MaxMind-DB-Reader-python)

## Installation

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
}
~~~~

See [BGPElem](https://bgpstream.caida.org/docs/api/pybgpstream/_pybgpstream.html#bgpelem) for more details.

## Sources

- Wikipedia [EN](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- Wikipedia [FR](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)
- [BGPStream Filtering] (<https://github.com/CAIDA/libbgpstream/blob/master/FILTERING>)
- [BGPStream python library] (https://bgpstream.caida.org/docs/api/pybgpstream)
