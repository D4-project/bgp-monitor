# BGP-filter

BGP filter based on prefixes/network with country lookup

## Usage

~~~~shell
usage: bgp-filter.py [-h] [-v] [-r] [--from_time FROM_TIME] [--until_time UNTIL_TIME] [--country_file [COUNTRY_FILE]] [-jf [JSON_OUTPUT_FILE]] [-pf] [-cf COUNTRY_F [COUNTRY_F ...]] [-af ASN_F [ASN_F ...]]

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
  -pf, --cidr_f         Filter using specified cidr
  -cf COUNTRY_F [COUNTRY_F ...], --country_f COUNTRY_F [COUNTRY_F ...]
                        Filter using specified country codes
  -af ASN_F [ASN_F ...], --asn_f ASN_F [ASN_F ...]
                        Filter using specified AS numbers
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
- [ ] CIDR block, ASN, country, etc... filtering options
- [ ] collector/project options ?
- [X] Output more data results
- [X] Correct interrupt of the program (CTRL + C -> clean json ending)
- [ ] Generate requirements.txt

## Exemple of Use

## Requirements

- [MaxMindDB Library](https://github.com/maxmind/MaxMind-DB-Reader-python)

## Installation

## Output

- `type` : ...
- `time` : ...
- `peer` : ...
- `peer_asn`: ...
- `prefix` : ...
- `country` : ...
- `collector`:
- `country_code`:
- `as-path`: List separated by spaces of AS numbers, ordered by
- `next-hop`: "202.79.197.159"

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

## Sources

- Wikipedia [EN](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- Wikipedia [FR](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)
- [BGPStream] (<https://github.com/CAIDA/libbgpstream/blob/master/FILTERING>)
