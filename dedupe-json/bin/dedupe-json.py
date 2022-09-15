import json
import redis
import sys
import argparse
import hashlib

red = redis.Redis(host='localhost', port=6379, charset="utf-8", db=5)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fields", nargs="+", help="fields to check", required=True)
parser.add_argument("-ttl", "--timetolive", help="time to keep key in db")
args = parser.parse_args()

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
                print(js)
