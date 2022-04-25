# Ail BGP feeder

## Usage

~~~~shell
usage: feeder.py [-h] [-v] [-cf COUNTRY_FILTER [COUNTRY_FILTER ...]] [-af ASN_FILTER [ASN_FILTER ...]] [-pf] [-cl CIDR_LIST [CIDR_LIST ...]] [--match {exact,less,more,any}] [-p {ris,routeviews}]
                 [-c COLLECTORS [COLLECTORS ...]] [-r] [--until_time UNTIL_TIME] [--from_time FROM_TIME] [--nocache]

Tool for BGP filtering and feeding

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program s version number and exit

  -cf COUNTRY_FILTER [COUNTRY_FILTER ...], --country_filter COUNTRY_FILTER [COUNTRY_FILTER ...]
                        Filter using specified country codes.

  -af ASN_FILTER [ASN_FILTER ...], --asn_filter ASN_FILTER [ASN_FILTER ...]
                        Filter using specified AS number list, skip a record if its as-path doesn t contain one of specified AS numbers

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

  --nocache             Disable caching
  --nocache             Disable caching
  --json_output [JSON_OUTPUT]
                        File in which to display JSON output. If not set, default sys.stdout will be used
~~~~

## Exemple of Use

Test the stream connection

~~~shell
python3 feeder.py --noail
~~~

Filter that exact match 84.205.67.0/24 as source AS

~~~shell
python3 feeder.py -pf --cidr_list 84.205.67.0/24--match exact
~~~

Retrieve records instead of live stream

~~~shell
python3 feeder.py --record --from_time "2022-01-01 10:00:00" --until_time "2022-01-01 10:10:00"
~~~

Specify a project / list of collectors :

~~~shell
python3 feeder.py -p routeviews --collectors route-views.bdix --from_time "2022-01-01 10:00:00" --until_time "2022-01-01 10:10:00"
~~~

## Installation

1. [libBGPStream](https://bgpstream.caida.org/docs/install/bgpstream) must be installed prior to installing PyBGPStream

2. Install requirements

~~~shell
pip3 install -r requirements.txt
~~~

3. Define config file based on etc/ail-feeder-bgp.cfg.sample

## Output

- `data`: base64 encoded value of the gziped data
- `data-sha256`: SHA256 value of the uncompress data
- `meta`:
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
- `source`: name of the ail feeder module
- `source-uuid`: UUID of the feeder
- `default-encoding`: "UTF-8"

## Example of ail output

~~~~json
{
    "data": "H4sIAEmmYmIC/03LQQ6CYAxE4RNZOwPtL915Ae9gAiQkRoioqzm87vQtvt17beP1OeksZHh2ZHbG8G96LPvhtrwnXdb7P0lkE91RbT5VXzVzbAWh0cgwDGF+ZC9apAEG6fd/AHzF6ohyAAAA",
    "data-sha256": "accdfaff0df1d797c4c82346bf5c352c15bc729ef6f0227ae65d13f69236b08c",
    "meta": {
        "bgp:type": "A",
        "bgp:time": 1650632262.23,
        "bgp:peer": "202.69.160.152",
        "bgp:peer_asn": 17639,
        "bgp:collector": "None",
        "bgp:prefix": "172.225.195.0/24",
        "bgp:country_code": "US",
        "bgp:as-path": "",
        "bgp:next-hop": "2.56.11.1"
    },
    "source": "ail_feeder_bgp",
    "source_uuid": "c48f8f2e-85b0-406e-9841-9155b2e39779",
    "default_encoding": "UTF-8"
}

~~~~

See [BGPElem](https://bgpstream.caida.org/docs/api/pybgpstream/_pybgpstream.html#bgpelem) for more details.

## More informations

- Wikipedia [EN](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- Wikipedia [FR](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)
- [BGPStream Filtering](<https://github.com/CAIDA/libbgpstream/blob/master/FILTERING>)
- [BGPStream python library](<https://bgpstream.caida.org/docs/api/pybgpstream>)
- [Data sources](<https://bgpstream.caida.org/data>)
- [Geo Open Databases](<https://data.public.lu/en/datasets/geo-open-ip-address-geolocation-per-country-in-mmdb-format/>)
