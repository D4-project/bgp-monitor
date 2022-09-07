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

from inspect import getmembers
import pickle
import pprint
import dill
import pybgpstream
import time

if __name__ == "__main__":

    stream = pybgpstream.BGPStream(
        until_time=0, record_type="updates", project="ris-live"
    )

    print(stream.__dict__)
    for e in stream:
        #        for el in getmembers(e.record.rec.rec):
        print(e.record.rec)
        # dill.dumps(e)
        # dill.detect.trace(True)
        # dill.detect.baditems(e)
        #        with open("bruh.bin","wb") as f:
        #            myvar = pickle.dump(e, f)

        exit(0)
