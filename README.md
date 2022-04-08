# BGP-filter

BGP filter based on prefixes/network with country lookup

## Usage

~~~~shell
usage: bgp-filter.py [-h] [-v] [-r] [--from_time FROM_TIME] [--until_time UNTIL_TIME] [--country_file [COUNTRY_FILE]] [--json_output_file [JSON_OUTPUT_FILE]] [-p]
                     [-c COUNTRY_F [COUNTRY_F ...]]

Tool for BGP filtering

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -r, --record          Retrieve records in the interval --until_time and --from-time arguments (which are required)
  --from_time FROM_TIME
                        Beginning of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00
  --until_time UNTIL_TIME
                        Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:10:00
  --country_file [COUNTRY_FILE]
                        MMDB Geo Open File which specify IP address geolocation per country. If not set, default file will be used
  --json_output_file [JSON_OUTPUT_FILE]
                        File in which to display JSON output. If not set, default sys.stdout will be used
  -p, --cidr_f          Filter using specified cidr
  -c COUNTRY_F [COUNTRY_F ...], --country_f COUNTRY_F [COUNTRY_F ...]
                        Filter using specified country codes
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
- [ ] Correct interrupt of the program (not just CTRL + C)
- [ ] Generate requirements.txt

## Requirements

- [MaxMindDB Library](https://github.com/maxmind/MaxMind-DB-Reader-python)

## Installation

## Output

- `time` : ...
- `type` : ...
- `peer` : ...
- `peer_number` : ...
- `prefix` : ...
- `country` : ...

~~~~json
{
'time':,
'type': ,
'peer': ,
'peer_number': ,
'prefix': ,
'country': 'US'
}
~~~~

## Sources

- Wikipedia [EN](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- Wikipedia [FR](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)
