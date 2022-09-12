# Dedupe-json

Script to avoid duplication of json regarding some fields of the json.

## Requirements

- [redis](https://github.com/redis/redis-py)



## Usage

~~~bash
dacru@dacru:~/git/bgp-monitor/dedupe-json/bin$ python dedupe-json.py -h
usage: dedupe-json.py [-h] -f FIELDS [FIELDS ...]

options:
  -h, --help            show this help message and exit
  -f FIELDS [FIELDS ...], --fields FIELDS [FIELDS ...]
                        fields to check

~~~



## Use case

To avoid duplicate of bgp json regarding `bgp:prefix` and `bgp:as-path`. If those fields is the same two times during monitoring then the second one will be skipped.

~~~bash
dacru@dacru:~/git/bgp-monitor/bin$ ./monitor.py --verbose | python3 dedupe-json.py -f bgp:prefix bgp:as-path
~~~

