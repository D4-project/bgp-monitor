import os
import json
import redis
import sys
import argparse
import hashlib
import configparser
from pyail import PyAIL

## Config
pathConf = '../etc/dedupe.cfg'

if os.path.isfile(pathConf):
    config = configparser.ConfigParser()
    config.read(pathConf)
else:
    print("[-] No conf file found")
    exit(-1)

if 'general' in config:
    uuid = config['general']['uuid']
else:
    uuid = '7c27e84a-e03d-4a5f-b584-b978167f9748'
if 'ail' in config:
    ail_url = config['ail']['url']
    ail_key = config['ail']['apikey']

if 'redis' in config:
    red = redis.Redis(host=config['redis']['host'], port=config['redis']['port'], db=config['redis']['db'])
else:
    red = redis.Redis(host='localhost', port=6379, db=5)


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fields", nargs="+", help="fields to check", required=True)
parser.add_argument("-ttl", "--timetolive", help="time to keep key in db")
parser.add_argument("-v", "--verbose", help="more display", action='store_true')
parser.add_argument("-d", "--debug", help="debug mode", action='store_true')
args = parser.parse_args()

verbose = args.verbose
debug = args.debug

## Ail
if not debug:
    try:
        pyail = PyAIL(ail_url, ail_key, ssl=False)
    except Exception as e:
        # print(e)
        print("\n\n[-] Error during creation of AIL instance")
        sys.exit(0)

buff = ''
data = ''
while True:
    # get json
    buff += sys.stdin.read(1)
    if buff.endswith('\n'):
        data = buff[:-1]
        buff = ''

        data = data.replace('\'', '\"')

        if data:
            try:
                js = json.loads(data)
            except Exception:
                continue

            list_field = ""
            for field in args.fields:
                if field in js.keys():
                    list_field += str(js[field])

            sha1 = hashlib.sha1(list_field.encode()).hexdigest()

            if not red.exists(f"json_duplicate:{sha1}"):
                red.set(f"json_duplicate:{sha1}", 1)
                if args.timetolive:
                    red.expire(f"json_duplicate:{sha1}", int(args.timetolive))

                if verbose or debug:
                    print(js)

                if not debug:
                    meta_dict = {}
                    source = 'bgp_monitor'
                    source_uuid = uuid
                    pyail.feed_json_item(js, meta_dict, source, source_uuid, 'utf-8')