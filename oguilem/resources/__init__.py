import re
from xml.etree.ElementTree import parse

import pkg_resources as pr


def _parse_globopt():
    tree = parse(pr.resource_stream("oguilem.resources", "globopt.xml"))
    mutations = dict()
    crossovers = dict()
    for node in tree.getroot():
        try:
            key = node.attrib["id"]
        except KeyError:
            raise IOError("Could not parse globopt.xml because one of the xover tags was missing"
                          + " the 'id' attribute.")
        if node.tag == "mutation":
            mutations[key] = _Node(node)
        elif node.tag == "crossover":
            crossovers[key] = _Node(node)
        else:
            raise IOError("Could not parse fitness.xml because one of the tag identifiers was invalid: '%s'" % node.tag)
    return mutations, crossovers


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


def _parse_presets():
    sets = list()
    tree = parse(pr.resource_stream("oguilem.resources", "presets.xml"))
    for node in tree.getroot():
        try:
            name = node.attrib["name"]
        except KeyError:
            raise IOError("Could not parse presets.xml because one of the tags was missing the 'name' attribute.")
        try:
            file = node.attrib["file"]
        except KeyError:
            raise IOError("Could not parse presets.xml because one of the tags was missing the 'file' attribute.")
        descr = ""
        if node.text:
            descr = node.text
        path = pr.resource_filename("oguilem.resources.presets", file)
        sets.append((name, descr, path))
    return sets


class _Node:
    def __init__(self, node):
        self.id = ""
        self.name = ""
        self.required = False
        self.descr = ""
        self.user_defined = False
        self.label = None
        self.divider = ","
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
        if "divider" in node.attrib:
            self.divider = node.attrib["divider"]
        if node.text:
            tmp = re.sub(r"\n\s+", " ", node.text.strip())
            self.descr = tmp
        self.opts = list()
        for opt in node:
            self.opts.append(_Node(opt))


globopt = _parse_globopt()
options = _parse_general()
fitness = _parse_fitness()
presets = _parse_presets()
icon = pr.resource_filename("oguilem.resources", "ogo.ico")

__all__ = [globopt, options, fitness, presets, icon]
