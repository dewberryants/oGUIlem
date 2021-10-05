import re

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from resources import runtypes, crossovers, mutations, options


class OGUILEMConfig:
    def __init__(self):
        self.runtype = OGUILEMRunTypeConfig()
        self.crossover = OGUILEMXOverConfig()
        self.mutation = OGUILEMMutationConfig()
        self.options = OGUILEMGeneralConfig()

    def set_runtype(self, id):
        self.runtype.set_runtype(id)

    def load_from_file(self, file):
        with open(file, "r") as conf_file:
            content = conf_file.readlines()
            ps = 0
            for line in content:
                if re.search("PoolSize", line):
                    ps = int(re.search(r"[0-9]+", line)[0])
            self.options.values["PoolSize"].set(ps)


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
                self.defaults[key] = bool(default)
            elif type == "3;float":
                default = default.strip().split(";")
                self.defaults[key] = (float(default[0]), float(default[1]), float(default[2]))
            else:
                raise IOError("Could not parse xml key %s in general configs!" % key)
        for key in self.defaults:
            self.values[key] = ConnectedValue(self.defaults[key])


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


class ConnectedValue(QObject):
    changed = pyqtSignal()

    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = type(value)

    def get(self):
        return self.value

    def set(self, value, index=-1):
        if self.type is list and index > 0:
            self.value[index] = value
        elif self.type is tuple and index > 0:
            tmp = list(self.value)
            tmp[index] = value
            self.value[index] = tuple(tmp)
        elif type(value) is self.type:
            self.value = value
        else:
            raise ValueError("Could not set connected value!")
        self.changed.emit()

    def __str__(self):
        return str(self.value)


instance = OGUILEMConfig()
