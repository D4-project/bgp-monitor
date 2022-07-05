# Definitions

## Autonomous Systems

The Internet is a network of networks, and autonomous systems are the big networks that make up the Internet.  
Every computer that has access to the Internet is linked to an Autonomous System (AS).  

More specifically, an autonomous system (AS) is a large network or group of networks that are all managed, controlled and supervised by a single entity or organization. It can be your Internet Service Provider (ISP), a private society (eg. Google, Facebook, etc), a government etc.  
Each AS are connected to their neighbors called peers, which receives and advertise different [BGP messages](#bgp-messages).  
Also, these connections form a network graph built using [AS Paths](#bgp-as-path).  

---

### Routing policy

Autonomous Systems are connected to their neighbors called peers, which receives and sends different [BGP messages](#bgp-messages).  
A routing policy is also defined for each AS:
- has its own list of [prefixes](#ip-address-prefixes) (IP ranges).
- has a list of its peer AS

---

## IP Address prefixes

While networking, each Autonomous System announce or withdraw ranges of IP addresses.
Also, a range of IP Addresses is defined in CIDR format.

A prefix is a CIDR (Classless Inter-Domain Routing) format.
It is composed as follow as "network/subnet" mask where Network is a normal ipv4 or ipv6 address and Subnet mask is a number between 0 and 32 which is the mask.

For example, 10.10.0.0/24 represents IP addresses 10.10.0.0 to 10.10.0.255

---

## BGP (Border Gateway Protocol)

Border Gateway Protocol (BGP) is a standardized gateway protocol designed to exchange routing and reachability information among [autonomous systems](#autonomous-systems) (AS) on the Internet.

BGP is classified as a path-vector routing protocol and it makes routing decisions based on paths, network policies, or rulesets configured by a network administrator.

### BGP AS Path

In every prefix announcement, an AS-path is specified to know the route to the announced prefix.  
This path is a list of AS numbers.
Also, when a prefix is withdrawn, all AS-paths (or routes) to the prefix are removed

---

## BGP Messages

There are 3 types of BGP messages:

- `Open`:
  - Establish a TCP connection
  - Exchange information such as BGP Version number, AS Number, Hold Down Time value, BGP Identifier
- `Keepalive`:
  If no update or keepalive message is sent for more than 30 second, then the connection is closed.
- `Update`:
  - Announce a new prefix (message can contain an AS-path)
  - Withdraw a prefix
  - Peer State change
  By default, update messages contains peers' IP address, asn, etc
- `Notification`:  
  Used to send error codes
- `Route-Refresh`

---

## References and more sources

For more details, you can consult the following links:

- [EN | CloudFlare](https://www.cloudflare.com/learning/network-layer/what-is-an-autonomous-system/)
- [EN | Wikipedia - CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [EN | Wikipedia - Border Gateway Protocol](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- [FR | Wikipedia - Border Gateway Protocol](https://fr.wikipedia.org/wiki/Border_Gateway_Protocol)
- [FR | Oracle - CIDR](https://docs.oracle.com/cd/E19957-01/820-2982/6nei1phfe/index.html)

---

# Installation

### From source

1. First, you must install [libBGPStream](https://bgpstream.caida.org/docs/install/bgpstream) C library
   Check supported OS before install (eg. Ubuntu 22.04 is not supported)  

2. Clone repo and Install requirements:

```shell
git clone https://github.com/D4-project/bgp-monitor.git
pip3 install -r requirements.txt
```

You can export the path to the repo if you want to execute it from anywhere:

```shell
chmod +x /path/to/repo/bgp-monitor/bin/monitor.py
export PATH=$PATH:/path/to/repo/bgp-monitor/bin/
```

### Database

Therefore, you can install the desired database:

- [kvrocks](https://github.com/apache/incubator-kvrocks)
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
docker build -f docker/{dbname}/Dockerfile -t bgp-monitor-{dbname} . # Generate an other image from the previous
docker run -it bgp-monitor-{dbname}:latest
```

### From DockerHub

You can install generated images from **Dockerhub**:

```shell
docker run -it ustaenes/bgp-monitor:latest
```

:warning: Not yet available :warning:

```shell
docker run -it -P ustaenes/bgp-monitor-kvrocks:latest
```

```shell
docker run -it -P ustaenes/bgp-monitor-questdb:latest
```

```shell
docker run -it -P ustaenes/bgp-monitor-clickhouse:latest
```

---

# Usage

## Examples of command-line usage

**Default** stream testing (No filtering, massive print):

```shell
./monitor.py --verbose
```

**Filter ip addresses** 84.205.67.0 through 84.205.67.255:

```shell
./monitor.py -pf 84.205.67.0/24 --verbose
```

You can **filter many AS numbers and/or prefixes** in `etc/filter_file.cfg.sample` instead of using long command line:

```shell
./monitor.py --filter_file etc/filter_file.cfg.sample --verbose
```

**Retrieve past records** instead of live stream

```shell
./monitor.py --record --start "2022-01-01 10:00:00" --stop "2022-01-01 10:10:00" --verbose
```

Specify a project / list of collectors:

```shell
./monitor.py -p routeviews --collectors route-views.bdix --start "2022-01-01 10:00:00" --stop "2022-01-01 10:10:00" --verbose
```

**Retrieve** records **from single file** as source instead of a broker:

```shell
./monitor.py --input_data ../datasets/updates.20220425.1215 --verbose
```

## Output

BGP records are reformatted and presented as follows:

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

---

# Testing

To test different filters, you can download some datasets here :

- [Routeviews DataSets](<http://archive.routeviews.org/>)
- [RIS RIPE DataSets](<https://data.ris.ripe.net/>)

It will be easier to work with static data instead of ris-live stream:

```shell
./monitor.py --input_data ../datasets/updates.20220425.1215 --verbose
```

Note that you can use options like `--json_out` (to save the output) or `--expected_result` (check if json_out is equal to the specified file)

# How it works?


# License

# Contribution

UML of different classes + class docs + Scheme

# How it's made?
You can check the following UML :
