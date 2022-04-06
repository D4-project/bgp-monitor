# bgp-filter
BGP filter based on prefixes/network with country lookup

# Usage
~~~~shell
Usage: bgp-filter.py [-h] [-p PREFIX] [-r --until_time=TIMESTAMP --from_time=TIMESTAMP] [--country_file=COUNTRYFILEDB]
                                            [--json_output_file=JSONFILE]
  Optional arguments:
      -h, --help              Show this help message and exit
      -p, --prefix            Filter using specified prefix
      -r, --record            Retrieve records in the interval --until_time and --from-time arguments (which are required)            
      --from_time             Beginning of the interval.  Timestamp format : YYYY-MM-DD hh:mm:ss -> Example: 2022-01-01 10:00:00
      --until_time            Ending of the interval.     Timestamp format : YYYY-MM-DD hh:mm:ss
      --country_file          MMDB Geo Open File which specify IP address geolocation per country
                              If not set, default file will be used
      --json_output_file      File in which to display JSON output
                              If not set, default sys.stdout will be used
~~~~

# TODO

- [X] Initial script based on stream retrieve or records
- [X] Country lookup using [geo open file](https://data.public.lu/en/datasets/geo-open-ip-address-geolocation-per-country-in-mmdb-format/)
- [X] Save json output file option
- [ ] Add .gitignore
- [ ] Use argparse
- [ ] Create lib to centralize filtering
- [ ] Add test cases
- [ ] Output more data results
- [ ] Correct intterupt of the program (not just CTRL + C)
- [ ] CIDR block, ASN, country, etc... based filter
- [ ] collector/project options ?
- [ ] Generate requirements.txt

# Requirements
- [MaxMindDB Library](https://github.com/maxmind/MaxMind-DB-Reader-python) 

# Installation


# Output
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

# Licence

# Sources
