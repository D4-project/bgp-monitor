# BGP monitor

## Usage

~~~~shell
usage: feeder.py [-h] [-v] [-cf <country code> [<country code> ...]]
                 [-af <AS number> [<AS number> ...]] [-ip <version>] [-pf]
                 [-cl <prefix> [<prefix> ...]] [--match {exact,less,more,any}]
                 [-p {ris,routeviews}] [-c <collector> [<collector> ...]] [-r]
                 [--from_time <begin>] [--until_time <end>] [--queue] [--noail]
                 [--nocache] [-jo [JSON_OUTPUT]] [--input_data <path>]
                 [--input_record_type {rib,upd}]
                 [--input_file_format {mrt,bmp,ris-live}] [--expected_result [<path>]]

Tool for BGP filtering and feeding

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -cf <country code> [<country code> ...], --country_filter <country code> [<country code> ...]
                        Filter using specified country codes.
  -af <AS number> [<AS number> ...], --asn_filter <AS number> [<AS number> ...]
                        Filter using specified AS number list, skip a record if its as-
                        path doesn't contain one of specified AS numbers
  -ip <version>, --ipversion <version>
                        Filter specific ip address type. ipv4 or ipv6
  -pf, --cidr_filter    Filter using specified cidr list. Keep records that match to
                        one of specified cidr
  -cl <prefix> [<prefix> ...], --cidr_list <prefix> [<prefix> ...]
                        List of cidr. Format: ip/subnet | Example:
                        130.0.192.0/21,130.0.100.0/21
  --match {exact,less,more,any}
                        Type of match -> exact: Exact match | less: Exact match or less
                        specific | more: Exact match or more specific
  -p {ris,routeviews}, --project {ris,routeviews}
                        Project name
  -c <collector> [<collector> ...], --collectors <collector> [<collector> ...]
                        Collectors. For complete list of collectors, see
                        https://bgpstream.caida.org/data
  -r, --record          Retrieve records in the interval --until_time and --from-time
                        arguments (which are required)
  --from_time <begin>   Beginning of the interval. Timestamp format : YYYY-MM-DD
                        hh:mm:ss -> Example: 2022-01-01 10:00:00
  --until_time <end>    Ending of the interval. Timestamp format : YYYY-MM-DD hh:mm:ss
                        -> Example: 2022-01-01 10:10:00
  --queue               Enable queue option. Use lot a of memory
  --noail               Disable ail publish. Disable caching
  --nocache             Disable caching
  -jo [JSON_OUTPUT], --json_output [JSON_OUTPUT]
                        File in which to display JSON output. If not set, default
                        sys.stdout will be used.
  --input_data <path>   Path to a single file instead of broker.
  --input_record_type {rib,upd}
                        Type of records contained in input_data file. Can be ribs (rib)
                        or updates (upd)
  --input_file_format {mrt,bmp,ris-live}
                        input data type format. ris-live avaible for updates only
  --expected_result [<path>], -expected [<path>]
                        Check that the result is the same as the expected result
~~~~

## Installation

1. [libBGPStream](https://bgpstream.caida.org/docs/install/bgpstream) must be installed prior to installing PyBGPStream

2. Install requirements

    ~~~shell
    pip3 install -r requirements.txt
    ~~~

3. Define config file based on etc/ail-feeder-bgp.cfg.sample

### Test your installation

Read [`TESTING.md`](./datasets/TESTING.md) for more informations

## Exemple of Use

Test the stream connection without ail:

~~~shell
python3 feeder.py --noail
~~~

Filter that exact match 84.205.67.0/24 as source AS

~~~shell
python3 feeder.py -pf --cidr_list 84.205.67.0/24 --match exact
~~~

Retrieve records instead of live stream

~~~shell
python3 feeder.py --record --from_time "2022-01-01 10:00:00" --until_time "2022-01-01 10:10:00"
~~~

Specify a project / list of collectors :

~~~shell
python3 feeder.py -p routeviews --collectors route-views.bdix --record --from_time "2022-01-01 10:00:00" --until_time "2022-01-01 10:10:00"
~~~

Use a single file as source instead of a broker:

~~~shell
python3 feeder.py --input_data ../datasets/updates.20220425.1215 --input_file_type upd-file --noail
~~~

You can get archive files here :

- [Routeviews DataSets](<http://archive.routeviews.org/>)
- [RIS RIPE DataSets](<https://data.ris.ripe.net/>)

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
