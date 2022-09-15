# Dedupe-json

Script to avoid duplication of json regarding some fields of the json.

## Requirements

- [redis](https://github.com/redis/redis-py)
- [pyail](https://github.com/ail-project/PyAIL)



## Usage

~~~bash
dacru@dacru:~/git/bgp-monitor/dedupe-json/bin$ python dedupe-json.py -h
usage: dedupe-json.py [-h] -f FIELDS [FIELDS ...] [-ttl TIMETOLIVE]
                      [-v VERBOSE] [-d DEBUG]

options:
  -h, --help            show this help message and exit
  -f FIELDS [FIELDS ...], --fields FIELDS [FIELDS ...]
                        fields to check
  -ttl TIMETOLIVE, --timetolive TIMETOLIVE
                        time to keep key in db
  -v VERBOSE, --verbose VERBOSE
                        more display
  -d DEBUG, --debug DEBUG


~~~



## Use case

To avoid duplicate of bgp json regarding `bgp:prefix` and `bgp:as-path`. If those fields is the same two times during monitoring then the second one will be skipped.

~~~bash
dacru@dacru:~/git/bgp-monitor/bin$ ./monitor.py --verbose | python3 ../dedupe-json/dedupe-json.py -f bgp:prefix bgp:as-path
~~~



## Json input format

It's important for the json to be an unique line and to finish the line with a new line `\n`.

~~~json
{  "bgp:type": "A",  "bgp:time": 1650632262.23,  "bgp:peer": "202.69.160.152",  "bgp:peer_asn": 17639,  "bgp:collector": "None",  "bgp:prefix": "172.225.195.0/24",  "bgp:country_code": "US",  "bgp:as-path": "",  "bgp:next-hop": "2.56.11.1"}

~~~

