import re
from typing import List, Dict

from oguilem.configuration.utils import ConnectedValue


class OGUILEMFitnessFunctionConfiguration:
    def __init__(self):
        self.tags: Dict[str] = dict()
        self.current: ConnectedValue = ConnectedValue("")

    def parse_backend_tags(self, list_blocks: List[List[str]]):
        for block in list_blocks:
            block_tag = ""
            block_back = ""
            for line in block:
                tmp = line.strip()
                if tmp.startswith("BackendTag="):
                    block_tag = tmp[11:]
                elif tmp.startswith("Backend="):
                    block_back = tmp[8:]
            if block_tag != "" and block_back != "":
                self.tags[block_tag] = block_back
            else:
                raise IOError("There seems to be a problem with one of the backend definition tags!")

    def parse_locopt_algo(self, string: str):
        for key in self.tags:
            string = re.sub(key, self.tags[key], string)
        self.current.set(string)

    def get_finished_config(self) -> str:
        self.current.request_update()
        return "\nLocOptAlgo=" + self.current.value
