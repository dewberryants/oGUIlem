from xml.etree.ElementTree import parse

import pkg_resources as pr


def _parse_crossovers():
    tree = parse(pr.resource_stream("resources", "crossover.xml"))
    ret = dict()
    for node in tree.getroot():
        try:
            id = node.attrib["id"]
        except KeyError:
            raise IOError("Could not parse crossover.xml because one of the xover tags was missing"
                          + " the 'id' attribute.")
        ret[id] = _Node(node)
    return ret


def _parse_runtypes():
    tree = parse(pr.resource_stream("resources", "runtypes.xml"))
    ret = dict()
    for node in tree.getroot():
        try:
            id = node.attrib["id"]
        except KeyError:
            raise IOError("Could not parse runtypes.xml because one of the runtype tags was missing"
                          + " the 'id' attribute.")
        ret[id] = _Node(node)
    return ret


class _Node:
    def __init__(self, node):
        self.id = "none"
        self.name = ""
        if "id" in node.attrib:
            self.id = node.attrib["id"]
        if "name" in node.attrib:
            self.name = node.attrib["name"]
        self.descr = node.text.strip()
        self.opts = list()
        for opt in node:
            self.opts.append(_Node(opt))


crossovers = _parse_crossovers()
runtypes = _parse_runtypes()

__all__ = [crossovers, runtypes]
