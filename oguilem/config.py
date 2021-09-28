from PyQt5.QtGui import QStandardItemModel, QStandardItem
from resources import runtypes, crossovers


class OGUILEMConfig:
    def __init__(self):
        self.runtype = OGUILEMRunTypeConfig()
        self.crossover = OGUILEMXOverConfig()

    def set_runtype(self, id):
        self.runtype.set_runtype(id)


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
            self.model.appendRow(item.clone())


class _NodeItem(QStandardItem):
    def __init__(self, node):
        super().__init__()
        if node.id:
            self.id = node.id
        if node.name:
            self.setText(node.name)
        if node.descr:
            self.setToolTip(node.descr)
        if node.opts:
            for opt in node.opts:
                self.appendRow(_NodeItem(opt))
        self.setEditable(False)

    def clone(self):
        ret = super().clone()
        rows = self.rowCount()
        if rows > 0:
            for n in range(rows):
                ret.appendRow(self.child(n).clone())
        return ret


instance = OGUILEMConfig()
