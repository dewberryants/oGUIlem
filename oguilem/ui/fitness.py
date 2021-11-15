import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.resources import fitness


class OGUILEMFitnessTab(qW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = qW.QVBoxLayout()

        layout.addWidget(qW.QLabel("Local Optimization Algorithm"))

        edit = FitnessDisplay()
        edit.setPlaceholderText("<LOCAL OPTIMIZER>")
        layout.addWidget(edit)

        layout.addWidget(qW.QLabel("Library of building Blocks (Double-click to add!)"))
        checkbox = qW.QCheckBox("Add all optional Settings (with their default values)")
        layout.addWidget(checkbox)

        tabs = qW.QTabWidget()
        locopt, generics, calcs = fitness
        tabs.addTab(FitnessBlockProvider(edit, locopt, checkbox), "Local Optimizers")
        tabs.addTab(FitnessBlockProvider(edit, generics, checkbox), "Generic Backends")
        tabs.addTab(FitnessBlockProvider(edit, calcs, checkbox), "Cartesian Backends")
        layout.addWidget(tabs)

        self.setLayout(layout)

    def open_edit(self):
        pass


class FitnessDisplay(qW.QTextEdit):
    def __init__(self):
        super().__init__()
        conf.fitness.current.changed.connect(self.update_from_config)
        self.textChanged.connect(self.update_to_config)

    def update_from_config(self):
        self.document().setPlainText(conf.fitness.current.get())

    def update_to_config(self):
        # Set directly to circumvent signal cascade
        conf.fitness.current.value = self.document().toPlainText()


class InactiveDelegate(qW.QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent: qW.QWidget, option, index) -> qW.QWidget:
        pass


class FitnessBlockProvider(qW.QTableView):
    def __init__(self, line_edit: qW.QTextEdit, config, checkbox: qW.QCheckBox):
        super().__init__()
        self.config = FitnessListHelper(config)
        self.checkbox = checkbox
        fitness_model = qG.QStandardItemModel()
        fitness_model.setHorizontalHeaderItem(0, qG.QStandardItem("Evaluator"))
        fitness_model.setHorizontalHeaderItem(1, qG.QStandardItem("Description"))
        for entry in self.config.table:
            fitness_model.appendRow([qG.QStandardItem(entry[0]), qG.QStandardItem(entry[1])])
        self.setModel(fitness_model)
        self.horizontalHeader().setSectionResizeMode(qW.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(qW.QHeaderView.ResizeToContents)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setWordWrap(True)
        self.setCornerButtonEnabled(False)
        self.setSelectionMode(qW.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(qW.QAbstractItemView.SelectRows)
        self.setItemDelegate(InactiveDelegate())
        self.line_edit: qW.QTextEdit = line_edit

    def mouseDoubleClickEvent(self, e: qG.QMouseEvent) -> None:
        index = self.selectedIndexes()[0].row()
        text = ""
        if len(self.line_edit.document().toPlainText()) > 0:
            text = self.line_edit.document().toHtml()
        text += self.config.get(index, self.checkbox.isChecked())
        self.line_edit.setText(text)


class FitnessListHelper:
    def __init__(self, config):
        self.table = list()
        # Config is a dict of _Node items
        for key in config:
            label = key if config[key].label is None else config[key.label]
            required = label
            optional = ""
            for item in config[key].opts:
                item_label = item.id if item.label is None else item.label
                if item.required:
                    descr = item.descr.replace("<", "&lt;").replace(">", "&gt;")
                    required += item_label + "<font color=\"red\">" + descr + "</font>" + ","
                else:
                    optional += item_label + item.descr + ","
            if len(required) > 0 and required[-1] == ",":
                required = required[:-1]
            if len(optional) > 0 and optional[-1] == ",":
                optional = optional[:-1]
            self.table.append((config[key].name, config[key].descr, required, optional))

    def get(self, index: int, optionals=False) -> str:
        if optionals:
            text = self.table[index][2]
            if len(self.table[index][3]) > 0:
                text += "," + self.table[index][3]
            return text
        else:
            return self.table[index][2]
