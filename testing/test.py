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

import pybgpstream
import time

if __name__ == "__main__":

    stream = pybgpstream.BGPStream(project="ris-live", record_type="updates",filter="elemtype announcements withdrawals")
    # stream.stream.set_live_mode()
    # stream.set_data_interface_option('broker', 'url', 'https://broker.bgpstream.caida.org/v2')
    cpt = 0 
    tmp = None
    ot = time.time()

    for e in stream:

        if not stream.started:
            print(f"tmp: {tmp}")
            print(f"e: {e}")
        tmp = e
        cpt += 1
        if cpt % 100000 == 0:
            nt = time.time()
            print(f"Counter : {cpt} - Time {e.time} - {nt - ot}s")
            ot = nt