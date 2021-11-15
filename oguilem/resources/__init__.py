import re
from xml.etree.ElementTree import parse

import pkg_resources as pr


def _parse_crossovers():
    tree = parse(pr.resource_stream("oguilem.resources", "crossover.xml"))
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
    tree = parse(pr.resource_stream("oguilem.resources", "runtypes.xml"))
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
    tree = parse(pr.resource_stream("oguilem.resources", "mutations.xml"))
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
    tree = parse(pr.resource_stream("oguilem.resources", "general.xml"))
    ret = dict()
    for node in tree.getroot():
        try:
            id = node.attrib["key"]
            type = node.attrib["type"]
            default = node.attrib["default"]
        except KeyError:
            raise IOError("Could not parse general.xml because one of the settings tags was missing"
                          + " the 'default' attribute.")
        ret[id] = (type, default)
    return ret


def _parse_fitness():
    tree = parse(pr.resource_stream("oguilem.resources", "fitness.xml"))
    locopts = dict()
    generics = dict()
    calcs = dict()
    for node in tree.getroot():
        try:
            key = node.attrib["id"]
        except KeyError:
            raise IOError("Could not parse fitness.xml because one of the tags was missing the 'id' attribute.")
        if node.tag == "locopt":
            locopts[key] = _Node(node)
        elif node.tag == "generic":
            generics[key] = _Node(node)
        elif node.tag == "calculator":
            calcs[key] = _Node(node)
        else:
            raise IOError("Could not parse fitness.xml because one of the tag identifiers was invalid: '%s'" % node.tag)
    return locopts, generics, calcs


class _Node:
    def __init__(self, node):
        self.id = ""
        self.name = ""
        self.required = False
        self.descr = ""
        self.user_defined = False
        self.label = None
        if "id" in node.attrib:
            self.id = node.attrib["id"]
        if "name" in node.attrib:
            self.name = node.attrib["name"]
        if "user" in node.attrib:
            self.user_defined = True
        if "required" in node.attrib:
            self.required = node.attrib["required"].strip().lower() == "true"
        if "label" in node.attrib:
            self.label = node.attrib["label"]
        if node.text:
            tmp = re.sub(r"\n\s+", " ", node.text.strip())
            self.descr = tmp
        self.opts = list()
        for opt in node:
            self.opts.append(_Node(opt))


crossovers = _parse_crossovers()
runtypes = _parse_runtypes()
mutations = _parse_mutations()
options = _parse_general()
fitness = _parse_fitness()

__all__ = [crossovers, runtypes, mutations, options, fitness]
