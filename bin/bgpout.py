"""
Ingest all records, queue, reformat, send, publish, save them.
"""

__all__ = ["BGPOut"]

import os
import sys
import json
import threading
from queue import Queue
from pybgpstream import BGPElem
from typing import TextIO


class BGPOut:
    """
    BGP Output
    - Ingest records, convert them to json, print to console and/or write them to files.
    - Save all records in database.
    - Can store bgp records in queue before processing them if desired.
    """

    def __init__(self) -> None:
        self.__expected_result = None
        self.__json_out = None
        self.verbose: bool = False
        """print to console"""
        self.isQueue: bool = False
        """Enable queue, can prevent from blocking BGPStream"""
        self.isStarted: bool = False
        """Is the stream started or not"""

    #######################
    #   GETTERS/SETTERS   #
    #######################

    @property
    def isQueue(self) -> bool:
        """Are the records queued, can prevent from blocking BGPStream"""
        return self.__queue is not None

    @isQueue.setter
    def isQueue(self, isQueue):
        self.__queue = Queue() if isQueue else None

    @property
    def json_out(self) -> TextIO:
        """
        (File): Print JSON in it

        Raises:
            Exception: If unable write/read in it
        """
        return self.__json_out

    @json_out.setter
    def json_out(self, json_out):
        """
        Setter for JSON output
        Parameters:
            json_out (File): Where to output json

        Raises:
            Exception: If unable write/read in it
        """
        if hasattr(json_out, "write"):
            self.__json_out = json_out

    @property
    def expected_result(self) -> TextIO:
        """Expected result when execution end"""
        return self.__expected_result

    @expected_result.setter
    def expected_result(self, exp):
        if exp is not None:
            if hasattr(exp, "read"):
                self.__expected_result = exp
            else:
                raise FileNotFoundError(f"Is {exp} a file ?")

    ########
    # MAIN #
    ########

    def start(self):
        """
        Start output

        - Init json output if specified
        - Start queue if enabled
        """
        if self.__json_out:
            self.__json_out.write("[")
        self.isStarted = True
        if self.__queue:
            threading.Thread(
                target=self.__process_queue,
                daemon=True,
                name="BGP monitor out",
            ).start()

    def stop(self):
        """
        - Set state as stopped
        - Close file output
        - Check if result is as expected
        """
        if self.isStarted:
            self.isStarted = False
            self.closeFile(self.__json_out)
            if self.__expected_result:
                print("Testing result: ")
                with open(self.__json_out.name, "r+") as js:
                    print(
                        "Result is as expected"
                        if checkFiles(js, self.__expected_result)
                        else "Result is not as expected"
                    )

    def __bgp_conv(self, e: BGPElem) -> dict:
        """Return a `BGPElem` formatted in json

        Parameters:
            e (BGPElem)
        """
        data = {
            "bgp:type": e.type,
            "bgp:time": e.time,
            "bgp:peer": e.peer_address,
            "bgp:peer_asn": e.peer_asn,
            "bgp:collector": e._maybe_field("collector") or "",
        }

        if e.type in ["A", "R", "W"]:  # updateribs
            data["bgp:prefix"] = e._maybe_field("prefix") or ""
            data["bgp:country_code"] = e.country_code
        if e.type in ["A", "R"]:  # updateribs
            data["bgp:as-path"] = e._maybe_field("as-path") or ""
            data["bgp:as-source"] = data["bgp:as-path"].split()[-1] or ""
            data["bgp:next-hop"] = e._maybe_field("next-hop") or ""
        elif e.type == "S":  # peer state
            data["bgp:old-state"] = e._maybe_field("old-state") or ""
            data["bgp:new-state"] = e._maybe_field("new-state") or ""

        return data

    def __iteration(self, e):
        if e.type not in ["A", "R"]:
            return
        r = self.__bgp_conv(e)

        if self.verbose:
            print("\n" + json.dumps(r, sort_keys=True) + ",")
        if self.__json_out:
            self.json_out.write("\n" + json.dumps(r, sort_keys=True, indent=4) + ",")

    def __process_queue(self):
        """Iterate over queue to process each bgp element"""
        while self.isStarted or self.__queue.qsize():
            # print("Queue size : " + str(self.__queue.qsize()), file=sys.stderr)
            self.__iteration(self.__queue.get())
            self.__queue.task_done()

    def input_data(self, data: BGPElem) -> None:
        """
        Input BGP element

        - Put it in queue if enable
        - Else process it immediatly
        Args:
            data (`BGPElem`)
        """
        self.__queue.put(data) if self.__queue else self.__iteration(data)

    def closeFile(self, file):
        """Close a JSON file

        Args:
            file (File): The file to close
        """
        if file == sys.stdout or file is None:
            return
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.truncate()
        file.write("]")
        file.close()


def checkFiles(f1, f2) -> bool:
    """
    Check if two json files are equal

    Args:
        f1, f2 (File): json files
    """

    f1.seek(0, os.SEEK_SET)
    f2.seek(0, os.SEEK_SET)
    json1 = json.load(f1)
    json2 = json.load(f2)
    return json1 == json2
