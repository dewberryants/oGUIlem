from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QStyledItemDelegate, QComboBox
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
        self.model = QStandardItemModel()

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
        if node.opts:
            for opt in node.opts:
                self.appendRow(_NodeItem(opt))
        self.setEditable(False)

    def clone(self) -> '_NodeItem':
        ret = super().clone()
        rows = self.rowCount()
        if rows > 0:
            for n in range(rows):
                ret.appendRow(self.child(n).clone())
        return ret


class CrossOverEditDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.xover_model = QStandardItemModel()
        root = self.xover_model.invisibleRootItem()
        for key in crossovers:
            root.appendRow(_NodeItem(crossovers[key]))

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.currentIndexChanged.connect(self.parent().add_new)
        editor.setFrame(False)
        editor.setModel(self.xover_model)
        editor.setCurrentIndex(-1)
        print(index.model().setItemData(index, {0: ""}))
        return editor

    def setModelData(self, editor, model, index):
        # if editor.currentIndex() != -1:
        #    super().setModelData(editor, model, index)
        # else:
        curr_item = self.xover_model.findItems(editor.currentText())
        index.model().removeRow(index.row())
        if len(curr_item) == 1:
            itm = curr_item[0].clone()
            itm.setEditable(True)
            self.parent().add_item(itm)
        self.parent().add_new()

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
