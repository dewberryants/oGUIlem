import re

import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.configuration.utils import BuildingBlockHelper
from oguilem.resources import fitness
from oguilem.ui.widgets import InactiveDelegate


class OGUILEMFitnessTab(qW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = qW.QVBoxLayout()

        layout.addWidget(qW.QLabel("Local Optimization Algorithm"))

        edit = FitnessDisplay()
        edit.setPlaceholderText("<Choose a local optimizer by double-clicking in the list below!>")
        layout.addWidget(edit)

        layout.addWidget(qW.QLabel("Library of building Blocks"))
        checkbox = qW.QCheckBox("Add all optional Settings (with their default values)")
        layout.addWidget(checkbox)

        tabs = qW.QTabWidget()
        locopt, generics, calcs = fitness
        tabs.addTab(FitnessBlockProvider(edit, locopt, checkbox, tabs), "Local Optimizers")
        tabs.addTab(FitnessBlockProvider(edit, generics, checkbox, tabs), "Generic Backends")
        tabs.addTab(FitnessBlockProvider(edit, calcs, checkbox, tabs), "Cartesian Backends")
        layout.addWidget(tabs)
        self.tabs = tabs
        self.setLayout(layout)

    def showEvent(self, a0) -> None:
        widget = self.tabs.widget(0)
        widget.horizontalHeader().reset()
        widget.verticalHeader().reset()


class FitnessDisplay(qW.QTextEdit):
    def __init__(self):
        super().__init__()
        conf.fitness.current.changed.connect(self.update_from_config)
        self.textChanged.connect(self.update_to_config)
        self.setLineWrapMode(qW.QTextEdit.NoWrap)
        self.setMaximumHeight(2 * self.fontMetrics().height() + self.fontMetrics().lineSpacing())
        self.setSizePolicy(qW.QSizePolicy.Minimum, qW.QSizePolicy.Preferred)

    def update_from_config(self):
        self.document().setPlainText(conf.fitness.current.get())

    def update_to_config(self):
        # Set directly to circumvent signal cascade
        conf.fitness.current.value = self.document().toPlainText()


class FitnessBlockProvider(qW.QTableView):
    def __init__(self, line_edit: qW.QTextEdit, config, checkbox: qW.QCheckBox, tabs: qW.QTabWidget):
        super().__init__()
        self.config = BuildingBlockHelper(config)
        self.checkbox = checkbox
        self.tabs = tabs
        self.setWordWrap(True)
        self.setCornerButtonEnabled(False)
        self.setSelectionMode(qW.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(qW.QAbstractItemView.SelectRows)
        self.setItemDelegate(InactiveDelegate())
        self.line_edit: qW.QTextEdit = line_edit
        fitness_model = qG.QStandardItemModel()
        fitness_model.setHorizontalHeaderItem(0, qG.QStandardItem("Evaluator"))
        fitness_model.setHorizontalHeaderItem(1, qG.QStandardItem("Description"))
        for entry in self.config.table:
            fitness_model.appendRow([qG.QStandardItem(entry[0]), qG.QStandardItem(entry[1])])
        self.setModel(fitness_model)
        self.verticalHeader().setSectionResizeMode(qW.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(0, qW.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, qW.QHeaderView.Stretch)

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self.horizontalHeader().reset()
        self.verticalHeader().reset()

    def mouseDoubleClickEvent(self, e: qG.QMouseEvent) -> None:
        index = self.selectedIndexes()[0].row()
        if len(self.line_edit.document().toPlainText()) > 0:
            text = self.line_edit.document().toHtml()
            error_dialog = qW.QMessageBox()
            error_dialog.setStandardButtons(qW.QMessageBox.Yes | qW.QMessageBox.Cancel)
            error_dialog.setDefaultButton(qW.QMessageBox.Cancel)
            error_dialog.setText("No sensible space for this. Append in new line?")
            x = None
            # Check the corresponding tags and replace (seems a little smarter)
            if self.tabs.currentIndex() == 0:
                pattern = r'<span style=" color:#ff0000;">&lt;LOCAL OPTIMIZER&gt;</span>'
                if not re.search(pattern, text):
                    x = error_dialog.exec_()
            elif self.tabs.currentIndex() == 1:
                pattern = r'<span style=" color:#ff0000;">&lt;GENERIC BACKEND&gt;</span>'
                if not re.search(pattern, text):
                    x = error_dialog.exec_()
            elif self.tabs.currentIndex() == 2:
                pattern = r'<span style=" color:#ff0000;">&lt;CALCULATOR BACKEND&gt;</span>'
                if not re.search(pattern, text):
                    x = error_dialog.exec_()
            else:
                raise IOError("Bad Index in FitnessBox. This is a bug!")
            if x is not None:
                # No fitting tag was found, so we either append or do nothing.
                if x == 16384:
                    text += self.config.get(index, self.checkbox.isChecked())
                else:
                    return
            else:
                # A fitting tag was found. Replace and we're happy.
                text = re.sub(pattern, self.config.get(index, self.checkbox.isChecked()), text, 1)
        else:
            text = self.config.get(index, self.checkbox.isChecked())
        self.line_edit.setText(text)
