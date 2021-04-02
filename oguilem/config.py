from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QStyledItemDelegate, QComboBox
from resources import runtypes


class OGUILEMConfig:
    def __init__(self):
        self.runtype = OGUILEMRunTypeConfig()
        self.crossover = OGUILEMXOverConfig()

    def set_runtype(self, id):
        self.runtype.set_runtype(id)


class OGUILEMRunTypeConfig:
    def __init__(self):
        self.id = None
        self.model = None

    def set_runtype(self, id):
        self.id = id

    def get_model(self):
        if self.model is None:
            model = QStandardItemModel()
            parent = model.invisibleRootItem()
            for key in runtypes:
                parent.appendRow(_NodeItem(runtypes[key]))
            self.model = model
        return self.model


class OGUILEMXOverConfig:
    def __init__(self):
        self.model = QStandardItemModel()
        root = self.model.invisibleRootItem()
        itm1 = QStandardItem("Editable")
        itm2 = QStandardItem("Non-Editable")
        itm2.setEditable(False)
        itm2.appendRow(QStandardItem("Child"))
        root.appendRow(itm1)
        root.appendRow(itm2)

    def get_model(self):
        return self.model

    def from_model(self, model):
        self.model = model


class _NodeItem(QStandardItem):
    def __init__(self, node):
        super().__init__()
        if node.id:
            self.id = node.id
        if node.name:
            self.setText(node.name)
        if node.descr:
            self.setToolTip(node.descr)
        self.setEditable(False)


class SmartNodeDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setFrame(False)
        return editor

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
