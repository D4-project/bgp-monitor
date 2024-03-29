"""
Ingest all records, queue, reformat, send, publish, save them.
"""

__all__ = ["BGPOut"]

import os
import sys
import json
from typing import TextIO
from Databases.database import BGPDatabases
from bgpgraph import BGPGraph


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


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
        self.databases = BGPDatabases({})
        self.graph = BGPGraph()

    #######################
    #   GETTERS/SETTERS   #
    #######################

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

    def stop(self):
        """
        - Set state as stopped
        - Close file output
        - Check if result is as expected
        """
        if self.isStarted:
            self.isStarted = False
            self.databases.stop()
            self.closeFile(self.__json_out)
            if self.__expected_result:
                print("Testing result: ")
                with open(self.__json_out.name, "r+") as js:
                    print(
                        "Result is as expected"
                        if checkFiles(js, self.__expected_result)
                        else "Result is not as expected"
                    )

    def iteration(self, e):
        """Iterate over queue to process each bgp element"""
        # self.redis.xadd()

        if self.verbose:
            print(json.dumps(e, sort_keys=True, cls=SetEncoder) + "\n", flush=True)
        if self.json_out:
            self.json_out.write(
                json.dumps(e, sort_keys=True, indent=4, cls=SetEncoder) + ",\n"
            )
        self.graph.update(e)
        self.databases.save(e)

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
