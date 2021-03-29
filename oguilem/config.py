import xml.etree.ElementTree as ET

import pkg_resources as pr


class OGUILEMConfig:
    def __init__(self):
        self.runtypes = None

    def get_runtypes(self):
        if self.runtypes is None:
            self.init_runtypes()
        return self.runtypes

    def init_runtypes(self):
        tree = ET.parse(pr.resource_stream("resources", "runtypes.xml"))
        self.runtypes = list(parse_runtypes(tree.getroot()))


def parse_runtypes(root):
    for child in root:
        yield OGUILEMRunType(child.attrib["name"], child.text.strip())


class OGUILEMRunType:
    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
