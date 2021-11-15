import re

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from oguilem.configuration.fitness import OGUILEMFitnessFunctionConfiguration
from oguilem.configuration.geometry import OGUILEMGeometryConfig
from oguilem.configuration.utils import ConnectedValue
from oguilem.resources import runtypes, crossovers, mutations, options


class OGUILEMConfig:
    def __init__(self):
        self.runtype = OGUILEMRunTypeConfig()
        self.crossover = OGUILEMXOverConfig()
        self.mutation = OGUILEMMutationConfig()
        self.options = OGUILEMGeneralConfig()
        self.geometry = OGUILEMGeometryConfig()
        self.fitness = OGUILEMFitnessFunctionConfiguration()

    def set_runtype(self, id):
        self.runtype.set_runtype(id)

    def load_from_file(self, file):
        self.options.set_to_default()
        with open(file, "r") as conf_file:
            content = conf_file.readlines()
            # Find geometry block and split off
            iter_content = iter(content)
            geo_block = list()
            backend_defs = list()

            # Separate off blocks
            start, end = -1, -1
            for n, line in enumerate(iter_content):
                # Geometry Block
                if line.strip().startswith("<GEOMETRY>"):
                    start = n
                    try:
                        geo_line = next(iter_content).strip()
                    except StopIteration:
                        raise RuntimeError("Config ends after <GEOMETRY> tag!?")
                    while not geo_line.startswith("</GEOMETRY>"):
                        geo_block.append(geo_line)
                        try:
                            geo_line = next(iter_content).strip()
                        except StopIteration:
                            raise RuntimeError("Dangling <GEOMETRY> tag in configuration!")
                    end = start + len(geo_block) + 2
                    content = content[:start] + content[end:]
                # Any Backend Definitions
                if line.strip().startswith("<CLUSTERBACKEND>"):
                    back_block = list()
                    start = n
                    try:
                        back_line = next(iter_content).strip()
                    except StopIteration:
                        raise RuntimeError("Config ends after <CLUSTERBACKEND> tag!?")
                    while not back_line.startswith("</CLUSTERBACKEND>"):
                        back_block.append(back_line)
                        try:
                            back_line = next(iter_content).strip()
                        except StopIteration:
                            raise RuntimeError("Dangling <CLUSTERBACKEND> tag in configuration!")
                    end = start + len(back_block) + 2
                    backend_defs.append(back_block)
                    content = content[:start] + content[end:]

            # Parse them
            self.geometry.parse_from_block(geo_block)
            self.fitness.parse_backend_tags(backend_defs)

            # Deal with the rest
            for line in content:
                if line.strip().strip("LocOptAlgo="):
                    self.fitness.parse_locopt_algo(line.strip()[11:])
                else:
                    for key in self.options.values:
                        type = self.options.values[key].type
                        if re.match(key + "=", line.strip()):
                            value, index = parse_value(line.strip()[len(key) + 1:], type)
                            if value is not None:
                                print("Option {:>30} set to: {:>30}".format(key, str(value)))
                                self.options.values[key].set(value, index)
                            else:
                                print("ERROR: Could not set Option %s. Set to default instead!" % key)
                                self.options.values[key].set(self.options.defaults[key])


def parse_value(line, type):
    value = None
    index = -1
    work = line.strip()
    if type is str:
        value = work
    elif type is int:
        value = int(work)
    elif type is float:
        value = float(work)
    elif type is bool:
        value = work.lower() == "true"
    elif type is list:
        tmp = work.split(";")
        value = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
    return value, index


class OGUILEMRunTypeConfig:
    def __init__(self):
        self.id = None
        self.model = QStandardItemModel()
        parent = self.model.invisibleRootItem()
        for key in runtypes:
            parent.appendRow(_NodeItem(runtypes[key]))

    def set_runtype(self, id):
        self.id = id

    def get_model(self):
        return self.model


class OGUILEMXOverConfig:
    def __init__(self):
        self.choices = QStandardItemModel()
        parent = self.choices.invisibleRootItem()
        for key in crossovers:
            parent.appendRow(_NodeItem(crossovers[key]))
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderItem(0, QStandardItem(""))
        self.model.setHorizontalHeaderItem(1, QStandardItem(""))

    def get_model(self):
        return self.model

    def from_model(self, model):
        self.model = model

    def get_choices(self):
        return self.choices

    def add_choice_to_model(self, index):
        item = self.choices.item(index, 0)
        if item is not None and item.__class__ is _NodeItem:
            self.model.appendRow([item.clone(), _EmptyItem()])


class OGUILEMMutationConfig:
    def __init__(self):
        self.choices = QStandardItemModel()
        parent = self.choices.invisibleRootItem()
        for key in mutations:
            parent.appendRow(_NodeItem(mutations[key]))
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderItem(0, QStandardItem(""))
        self.model.setHorizontalHeaderItem(1, QStandardItem(""))

    def get_model(self):
        return self.model

    def from_model(self, model):
        self.model = model

    def get_choices(self):
        return self.choices

    def add_choice_to_model(self, index):
        item = self.choices.item(index, 0)
        if item is not None and item.__class__ is _NodeItem:
            self.model.appendRow([item.clone(), _EmptyItem()])


class OGUILEMGeneralConfig:
    def __init__(self):
        self.defaults = dict()
        self.values = dict()
        for key in options:
            type, default = options[key]
            if type == "str":
                self.defaults[key] = default
            elif type == "int":
                self.defaults[key] = int(default)
            elif type == "float":
                self.defaults[key] = float(default)
            elif type == "bool":
                self.defaults[key] = (default.lower() == "true")
            elif type == "3;float":
                default = default.strip().split(";")
                self.defaults[key] = [float(default[0]), float(default[1]), float(default[2])]
            else:
                raise IOError("Could not parse xml key %s in general configs!" % key)
            self.values[key] = ConnectedValue(self.defaults[key])

    def set_to_default(self):
        for key in options:
            self.values[key].set(self.defaults[key])


class _NodeItem(QStandardItem):
    def __init__(self, node, ignore_opts=False):
        super().__init__()
        self.choices = None
        if node.id:
            self.id = node.id
        if node.name:
            self.setText(node.name)
        if node.descr:
            self.setToolTip(node.descr)
        if node.opts and not ignore_opts:
            for opt in node.opts:
                if len(opt.opts) >= 1:
                    choices = QStandardItemModel()
                    for opt_opt in opt.opts:
                        opt_item = _NodeItem(opt_opt, ignore_opts=True)
                        if opt_opt.user_defined:
                            opt_item.setEditable(True)
                        choices.appendRow(opt_item)
                    item = _NodeItem(opt, ignore_opts=True)
                    item.choices = choices
                    self.appendRow([item, choices.item(0, 0).clone()])
                else:
                    opt_item = _NodeItem(opt)
                    if opt.user_defined:
                        opt_item.setEditable(True)
                    self.appendRow([opt_item, _EmptyItem()])
        self.setEditable(False)

    def clone(self):
        ret = super().clone()
        rows = self.rowCount()
        if rows > 0:
            for n in range(rows):
                ret.appendRow([self.child(n, 0).clone(), self.child(n, 1).clone()])
        return ret


class _EmptyItem(QStandardItem):
    def __init__(self):
        super().__init__("")
        self.setEditable(False)
