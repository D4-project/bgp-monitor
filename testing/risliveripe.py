"""
Subscribe to a RIS Live stream and output every message to stdout.

IMPORTANT: this example requires 'websocket-client' for Python 2 or 3.

If you use the 'websockets' package instead (Python 3 only) you will need to change the code because it has a somewhat different API.
"""
import json
from time import time
import websocket

from sseclient import SSEClient

cpt = 0
ot = time()

"""
ws = websocket.WebSocket()
ws.connect("wss://ris-live.ripe.net/v1/ws/?client=py-example-1")
params = {
    "moreSpecific": True,
    "host": "",
    "socketOptions": {
        "includeRaw": True
    }
}
ws.send(json.dumps({
	"type": "ris_subscribe",
	"data": params
}))



for data in ws:
    cpt+=1
    if cpt %10000 ==0:
        nt = time()
        print(f"Counter : {cpt} - {nt - ot}s")
        ot = nt
"""

messages = SSEClient(
    "https://ris-live.ripe.net/v1/stream/?format=sse&client=cli-example-2"
)
for msg in messages:
    if cpt % 10000 == 0:
        nt = time()
        print(f"Counter : {cpt} - {nt - ot}s")
        print(msg)
        ot = nt
    cpt += 1

    print(msg)
