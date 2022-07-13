import urllib.request as urllib_request
import json
import pybgpstream
import time

'''
COLLECTORS_URL = "http://bgpstream.caida.org/broker/meta/collectors"
# We only care about the two major projects
PROJECTS = ('routeviews', 'ris')


# Query the BGPStream broker and identify the collectors that are available
def get_collectors():
    """Query the BGPStream broker and identify the collectors that are available"""
    data = json.load(urllib_request.urlopen(COLLECTORS_URL))
    result = dict((x, []) for x in PROJECTS)
    for coll in data['data']['collectors']:
        p = data['data']['collectors'][coll]['project']
        if p in PROJECTS:
            result[p].append(coll)
    return result

PROJECT_TYPES = {"ris": "ris-live", "routeviews": "routeviews-stream"}
PROJECTS = [i for i in PROJECT_TYPES.keys()]
COLLECTORS_URL = "http://bgpstream.caida.org/broker/meta/collectors"
COLLECTORS = get_collectors()
'''

if __name__ == '__main__':
    
    stream = pybgpstream.BGPStream(
        from_time=int(time.time()),
        record_type="updates",
        project="ris-live")
    cpt = 0
    tmp = None

    for e in stream:
        tmp = e
        cpt+=1
        if e.status != 'valid': print(e)
        if cpt%100000 == 0: print(f"Counter : {cpt} - Time {e.time}")
    