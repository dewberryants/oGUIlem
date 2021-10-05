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


def _parse_mutations():
    tree = parse(pr.resource_stream("resources", "mutations.xml"))
    ret = dict()
    for node in tree.getroot():
        try:
            id = node.attrib["id"]
        except KeyError:
            raise IOError("Could not parse mutations.xml because one of the mutation tags was missing"
                          + " the 'id' attribute.")
        ret[id] = _Node(node)
    return ret


def _parse_general():
    tree = parse(pr.resource_stream("resources", "general.xml"))
    ret = dict()
    for node in tree.getroot():
        try:
            id = node.attrib["key"]
            default = node.attrib["default"]
        except KeyError:
            raise IOError("Could not parse general.xml because one of the settings tags was missing"
                          + " the 'default' attribute.")
        ret[id] = default
    return ret


class _Node:
    def __init__(self, node):
        self.id = ""
        self.name = ""
        self.user_defined = False
        self.descr = ""
        if "id" in node.attrib:
            self.id = node.attrib["id"]
        if "name" in node.attrib:
            self.name = node.attrib["name"]
        if "user" in node.attrib:
            self.user_defined = True
        if node.text:
            self.descr = node.text.strip()
        self.opts = list()
        for opt in node:
            self.opts.append(_Node(opt))


crossovers = _parse_crossovers()
runtypes = _parse_runtypes()
mutations = _parse_mutations()
options = _parse_general()

__all__ = [crossovers, runtypes, mutations, options]
