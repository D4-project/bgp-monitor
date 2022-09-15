# BGP monitor

## Usage

```shell
usage: monitor.py [-h] [-v] [--verbose] [--filter_list [<path>]] [--config <path>] [-jo [<path>]] [-cf <country code> [<country code> ...]] [-af <AS number> [<AS number> ...]] [-ip <version>] [-pf <prefix> [<prefix> ...]]
                  [--match {more,less,exact,any}] [-p {ris,routeviews}] [-c <collector> [<collector> ...]] [-r] [--start <begin>] [--stop <end>] [--queue] [-id <path>] [-ir {upd,rib}] [-if {mrt,bmp,ris-live}] [--expected_result [<path>]]

Tool for BGP filtering and monitoring

options:
  -h, --help            show this help message and exit
  -v, --version         show program\'s version number and exit
  --verbose             Print BGP records in console
  --filter_list [<path>]
                        Use separated file to define list of prefixes and/or AS Numbers.
                         Check etc/filter_list.cfg.sample for file format
  --config <path>       Use different config file
  -jo [<path>], --json_output [<path>]
                        File in which to display JSON output.
                         If not set, default sys.stdout will be used.
  -cf <country code> [<country code> ...], --country_filter <country code> [<country code> ...]
                        Filter using specified country codes.
  -af <AS number> [<AS number> ...], --asn_filter <AS number> [<AS number> ...]
                        Filter using specified AS number list, skip a record if its AS-source is not one of specified AS numbers.
                         Use _ symbol for negation
  -ip <version>, --ipversion <version>
                        Filter specific ip address type. ipv4 or ipv6
  -pf <prefix> [<prefix> ...], --prefix_filter <prefix> [<prefix> ...]
                        Filter using specified prefix list, CIDR format: ip/subnet.
                         Example: 130.0.192.0/21,130.0.100.0/21
  --match {more,less,exact,any}
                        Type of match ->exact: Exact match
                        more: Exact match or more specific (Contained by one of the prefixes)
                        less: Exact match or less specific (Contain one of the prefixes).
                        Default: more
  -p {ris,routeviews}, --project {ris,routeviews}
                        Project name
  -c <collector> [<collector> ...], --collectors <collector> [<collector> ...]
                        Collectors. For complete list of collectors, see https://bgpstream.caida.org/data
  -r, --record          Retrieve records in the interval --until_time and --f-time arguments (which are required)
  --start <begin>       Beginning of the interval.
                          -> Timestamp format : YYYY-MM-DD hh:mm:ss.
                             Example: 2022-01-01 10:00:00
  --stop <end>          End of the interval.
                          -> Timestamp format : YYYY-MM-DD hh:mm:ss.
                             Example: 2022-01-01 10:10:00
  --queue               Enable queue option. Use a lot of memory
  -id <path>, --input_data <path>
                        Retrieve data from a single file instead of a broker.
  -ir {upd,rib}, --input_record_type {upd,rib}
                        Type of records contained in input_data file.
                         Can be rib (Routing Information Base) or upd (Updates eg. Anoun/Withdr).
                         Default: upd
  -if {mrt,bmp,ris-live}, --input_file_format {mrt,bmp,ris-live}
                        input data type format. ris-live is avaible for updates only
  --expected_result [<path>], -expected [<path>]
                        Check that the result is the same as the expected result
```

---

## Installation

### From source

1. First, you must install the following C libraries :

- [libBGPStream](https://bgpstream.caida.org/docs/install/bgpstream)
   Check supported OS before install (eg. Ubuntu 22.04 is not supported)  

- [libMaxMindDB](https://github.com/maxmind/libmaxminddb#on-ubuntu-via-ppa)

2. Clone repo and Install required python packages:

```shell
git clone https://github.com/D4-project/bgp-monitor.git
pip3 install -r requirements.txt
```

You can export the path to the repo if you want to execute it from anywhere:

```shell
chmod +x /path/to/repo/bgp-monitor/bin/monitor.py
export PATH=$PATH:/path/to/repo/bgp-monitor/bin/
```

3. Database

Therefore, you can install the desired database:

- [kvrocks](https://github.com/apache/incubator-kvrocks) :warning: Doesn't work
- [Questdb](https://github.com/questdb/questdb)
- [Clickhouse](https://clickhouse.com/docs/en/quick-start)

Don't forget to uncomment the corresponding lines in the [config file](./etc/config.cfg)

---

## Docker install

### From source

You can run bgp-monitor without database and run your own instance separately :

```shell
git clone https://github.com/D4-project/bgp-monitor.git
docker build -f docker/Dockerfile -t bgp-monitor . # Build bgp-monitor image
```

#### Database

You run an other docker image with pre-installed database (require bgp-monitor:latest / previous step) :

```shell
docker build -f docker/{dbname}/Dockerfile -t bgp-monitor:{dbname} . # Generate an other image from the previous
docker run -it bgp-monitor:{dbname}
```

Available dbname :

- kvrocks :warning: Doesn't work
- clickhouse
- quest

### From DockerHub

You can install generated images from **Dockerhub**:

```shell
docker run -it ustaenes/bgp-monitor:latest
```

:warning: Doesn't work
```shell
docker run -it -P ustaenes/bgp-monitor:kvrocks
```

```shell
docker run -it -P ustaenes/bgp-monitor:quest
```

```shell
docker run -it -P ustaenes/bgp-monitor:clickhouse
```

### BGP Messages by country
If you are interested about getting a handy dashboard

```shell
cd path/to/bgp-monitor/docker/grafana_dashboard
docker-compose up -d
```

You can then access to Grafana dashboard at [http://localhost:3000](http://localhost:3000)

---

## Usage

### Examples of command-line usage

**Default** stream testing (No filtering, massive print):

```shell
monitor.py --verbose
```

**Filter ip addresses** 84.205.67.0 through 84.205.67.255:

```shell
monitor.py -pf 84.205.67.0/24 --verbose
```

You can **filter many AS numbers and/or prefixes** in `etc/filter_file.cfg.sample` instead of using long command line:

```shell
monitor.py --filter_file etc/filter_file.cfg.sample --verbose
```

**Retrieve past records** instead of live stream

```shell
monitor.py --record --start "2022-01-01 10:00:00" --stop "2022-01-01 10:10:00" --verbose
```

Specify a project / list of collectors:

```shell
monitor.py -p routeviews --collectors route-views.bdix --start "2022-01-01 10:00:00" --stop "2022-01-01 10:10:00" --verbose
```

**Retrieve** records **from single file** as source instead of a broker:

```shell
monitor.py --input_data ../datasets/updates.20220425.1215 --verbose
```

### Testing

To test different filters, you can download some datasets here :

- [Routeviews DataSets](<http://archive.routeviews.org/>)
- [RIS RIPE DataSets](<https://data.ris.ripe.net/>)

It will be easier to work with static data instead of ris-live stream:

```shell
monitor.py --input_data ../datasets/updates.20220425.1215 --verbose
```

Note that you can use options like `--json_out` (to save the output) or `--expected_result` (check if json_out is equal to the specified file)

## Output

- `type`
  - R: RIB table entry
  - A: prefix announcement
  - W: prefix withdrawal
  - S: peer state change
- `time` : Timestamp
- `peer_address` : The IP address of the peer that this element was received from.
- `peer_asn`: The ASN of the peer that this element was received from.
- `collector`: The name of the collector that generated this element.
- `prefix` : The prefix of the source ASN that this element was generated from. [A and W types]
- `country_code`: The country of the source ASN that this element was generated from. [A and W types]
- `next-hop`: The next-hop IP address [A type]
- `as-path`: String list separated by spaces of AS numbers, ordered by the near peer ASN to the source ASN. Therefore, Source ASN is at the end of the string. [A type]
- `source`: Source AS in the as-path (also last AS number)

## Example of json output

```json
{
    "as-path": "25160 2914 5511 8697 8376",
    "collector": "rrc03",
    "communities": [
        "2914:3200",
        "2914:420",
        "2914:2202",
        "25160:22010",
        "2914:1201"
    ],
    "country_code": "JO",
    "next-hop": "80.249.210.85",
    "peer_address": "80.249.210.85",
    "peer_asn": 25160,
    "prefix": "149.200.178.0/24",
    "project": "ris-live",
    "router": null,
    "router_ip": null,
    "source": "8376",
    "time": 1663080130.13,
    "type": "A"
}
```

See [BGPElem](https://bgpstream.caida.org/docs/api/pybgpstream/_pybgpstream.html#bgpelem) for more details.

---

## More informations

- [BGPStream Filtering](<https://github.com/CAIDA/libbgpstream/blob/master/FILTERING>)
- [BGPStream python library](<https://bgpstream.caida.org/docs/api/pybgpstream>)
- [Data sources](<https://bgpstream.caida.org/data>)
- [Geo Open Databases](<https://data.public.lu/en/datasets/geo-open-ip-address-geolocation-per-country-in-mmdb-format/>)
- Wikipedia [EN](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- Wikipedia [FR](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)

# Contribution

This repository is open to any contribution.

## Add your own Database
To process data in you own way, here are the steps:
1. Copy SampleDatabase.py and implement it in your own way
    It must be in the `Databases` folder
2. To load and use it, you must then add your class name to `etc/config.cfg`
3. Be careful used technologies and implementation are important for performances