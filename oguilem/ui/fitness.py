import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration.fitness import test_config


class OGUILEMFitnessTab(qW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = qW.QVBoxLayout()

        layout.addWidget(qW.QLabel("Local Optimization Algorithm"))

        edit = qW.QTextEdit()
        edit.setPlaceholderText("<LOCAL OPTIMIZER>")
        layout.addWidget(edit)

        layout.addWidget(qW.QLabel("Library of building Blocks (Double-click to add!)"))
        layout.addWidget(qW.QCheckBox("Add all optional Settings (with their default values)"))

        tabs = qW.QTabWidget()
        tabs.addTab(FitnessProvider(edit, config=test_config), "Local Optimizers")
        tabs.addTab(FitnessProvider(edit, config=test_config), "Generic Backends")
        tabs.addTab(FitnessProvider(edit, config=test_config), "Cartesian Backends")
        layout.addWidget(tabs)

        self.setLayout(layout)

    def open_edit(self):
        pass


class InactiveDelegate(qW.QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent: qW.QWidget, option, index) -> qW.QWidget:
        pass


class FitnessProvider(qW.QTableView):
    def __init__(self, line_edit: qW.QTextEdit, config):
        super().__init__()
        self.config = config
        fitness_model = qG.QStandardItemModel()
        fitness_model.setHorizontalHeaderItem(0, qG.QStandardItem("Evaluator"))
        fitness_model.setHorizontalHeaderItem(1, qG.QStandardItem("Description"))
        for entry in self.config:
            fitness_model.appendRow([qG.QStandardItem(entry.name), qG.QStandardItem(entry.desc)])
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
        index = self.selectedIndexes()[0]
        text = self.line_edit.document().toRawText() + str(self.config[index.row()])
        self.line_edit.setText(text)
