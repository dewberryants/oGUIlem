import re

import PyQt5.QtCore as qC
import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.configuration.utils import BuildingBlockHelper, ConnectedValue
from oguilem.resources import globopt
from oguilem.ui.widgets import InactiveDelegate, SmartLineEdit


class OGUILEMGeneticAlgoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = qW.QTabWidget()
        self.accept_fitness = AcceptableFitnessLayout()
        self.init_ui()

    def init_ui(self):
        layout = qW.QVBoxLayout()
        columns = qW.QHBoxLayout()

        layout_left = qW.QVBoxLayout()

        crossover_display = ConnectedDisplay(conf.globopt.crossover,
                                             "<Choose a crossover operator by double-clicking in the list below!>")
        mutation_display = ConnectedDisplay(conf.globopt.mutation,
                                            "<Choose a mutation operator by double-clicking in the list below!>")

        layout_left.addWidget(qW.QLabel("Crossover Operator"))
        layout_left.addWidget(crossover_display)
        layout_left.addWidget(qW.QLabel("Mutation Operator"))
        layout_left.addWidget(mutation_display)

        layout_right = qW.QVBoxLayout()

        group3 = qW.QGroupBox("General GA Settings")
        group3.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        layout2 = qW.QVBoxLayout()

        layout3 = qW.QGridLayout()
        layout3.addWidget(qW.QLabel("Crossover Probability"), 0, 0)
        layout3.addWidget(SmartLineEdit(conf.options.values["CrossoverPossibility"], True), 0, 1)
        layout3.addWidget(qW.QLabel("Mutation Probability"), 1, 0)
        layout3.addWidget(SmartLineEdit(conf.options.values["MutationPossibility"], True), 1, 1)

        layout2.addLayout(layout3)
        layout2.addLayout(self.accept_fitness)
        group3.setLayout(layout2)
        layout_right.addWidget(group3)

        columns.addLayout(layout_left)
        columns.addLayout(layout_right)

        layout.addLayout(columns)

        checkbox = qW.QCheckBox("Add all optional Settings (with their default values)")
        layout.addWidget(qW.QLabel("Library of Operators"))
        layout.addWidget(checkbox)
        mutations, crossovers = globopt
        self.tabs.addTab(BlockProvider(crossover_display, crossovers, checkbox, "Crossover", "CROSSOVER",
                                       mutation_display), "Crossovers")
        self.tabs.addTab(BlockProvider(mutation_display, mutations, checkbox, "Mutation", "MUTATION",
                                       crossover_display), "Mutations")
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def showEvent(self, a0) -> None:
        widget = self.tabs.widget(0)
        widget.horizontalHeader().reset()
        widget.verticalHeader().reset()


class AcceptableFitnessLayout(qW.QGridLayout):
    def __init__(self):
        super().__init__()
        self.connected_value = conf.options.values["AcceptableFitness"]
        self.connected_value.changed.connect(self.update_from_config)
        self.connected_value.update_requested.connect(self.update_to_config)
        self.connected_value.error.connect(self.error_box)
        self.line_edit = qW.QLineEdit()
        self.line_edit.setEnabled(False)
        self.line_edit.setAlignment(qC.Qt.AlignRight)
        self.line_edit.setSizePolicy(qW.QSizePolicy.Minimum, qW.QSizePolicy.Minimum)
        self.checkbox = qW.QCheckBox("Acceptable Fitness")
        self.checkbox.clicked.connect(lambda: self.line_edit.setEnabled(not self.line_edit.isEnabled()))
        self.addWidget(self.checkbox, 0, 0)
        self.addWidget(self.line_edit, 0, 1)
        self.update_from_config()

    def update_from_config(self):
        if self.connected_value.value != conf.options.defaults["AcceptableFitness"]:
            self.checkbox.setCheckState(qC.Qt.Checked)
            self.line_edit.setText(str(self.connected_value))
            self.line_edit.setEnabled(True)
        else:
            self.checkbox.setCheckState(qC.Qt.Unchecked)
            self.line_edit.setText("-42.0")
            self.line_edit.setEnabled(False)

    def update_to_config(self):
        if self.checkbox.isChecked():
            self.connected_value.set(self.line_edit.text())
        else:
            self.connected_value.set(conf.options.defaults["AcceptableFitness"])

    def error_box(self):
        error_dialog = qW.QMessageBox()
        error_dialog.setStandardButtons(qW.QMessageBox.Ok)
        error_dialog.setText("Value Error! '%s' is not of type '%s'!" % (self.text(), str(self.connected_value.type)))
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()


class ConnectedDisplay(qW.QTextEdit):
    def __init__(self, value: ConnectedValue, placeholder_text: str):
        super().__init__()
        self.value = value
        self.value.changed.connect(self.update_from_config)
        self.value.update_requested.connect(self.update_to_config)
        self.value.error.connect(self.error_box)
        self.document().contentsChanged.connect(conf.file_manager.signal_modification)
        self.setPlaceholderText(placeholder_text)
        self.setLineWrapMode(qW.QTextEdit.NoWrap)
        self.setMaximumHeight(2 * self.fontMetrics().height() + self.fontMetrics().lineSpacing())
        self.setSizePolicy(qW.QSizePolicy.Minimum, qW.QSizePolicy.Preferred)

    def update_from_config(self):
        self.document().setPlainText(self.value.get())

    def update_to_config(self):
        text = self.document().toPlainText()
        if "\n" in text:
            self.value.error.emit()
        self.value.set(text)

    def error_box(self):
        error_dialog = qW.QMessageBox()
        error_dialog.setStandardButtons(qW.QMessageBox.Ok)
        error_dialog.setText("Mutation and Crossover Algorithm String must be exactly one line!")
        error_dialog.exec()


class BlockProvider(qW.QTableView):
    def __init__(self, line_edit: qW.QTextEdit, config, checkbox: qW.QCheckBox, column_header="0", help_tag="0",
                 line_edit2=None):
        super().__init__()
        self.config = BuildingBlockHelper(config)
        self.checkbox = checkbox
        self.setWordWrap(True)
        self.setCornerButtonEnabled(False)
        self.setSelectionMode(qW.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(qW.QAbstractItemView.SelectRows)
        self.setItemDelegate(InactiveDelegate())
        self.line_edit: qW.QTextEdit = line_edit
        self.line_edit2 = line_edit2
        self.column_header = column_header
        self.help_tag = help_tag
        self.init_model()
        self.verticalHeader().setSectionResizeMode(qW.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(0, qW.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, qW.QHeaderView.Stretch)

    def init_model(self) -> None:
        model = qG.QStandardItemModel()
        model.setHorizontalHeaderItem(0, qG.QStandardItem(self.column_header))
        model.setHorizontalHeaderItem(1, qG.QStandardItem("Description"))
        self.setModel(model)
        for entry in self.config.table:
            model.appendRow([qG.QStandardItem(entry[0]), qG.QStandardItem(entry[1])])

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self.horizontalHeader().reset()
        self.verticalHeader().reset()

    def mouseDoubleClickEvent(self, e: qG.QMouseEvent) -> None:
        index = self.selectedIndexes()[0].row()
        if len(self.line_edit.document().toPlainText()) > 0:
            text = self.line_edit.document().toHtml()
            text2 = "" if not self.line_edit2 else self.line_edit2.document().toHtml()
            error_dialog = qW.QMessageBox()
            error_dialog.setStandardButtons(qW.QMessageBox.Yes | qW.QMessageBox.Cancel)
            error_dialog.setDefaultButton(qW.QMessageBox.Cancel)
            error_dialog.setText("No sensible space for this. Append in new line?")
            x = None
            # Check the corresponding tags and replace (seems a little smarter)
            pattern = r'<span style=" color:#ff0000;">&lt;' + self.help_tag + '&gt;</span>'
            match1 = re.search(pattern, text)
            match2 = re.search(pattern, text2)
            if not match1 and not match2:
                x = error_dialog.exec_()
            if x is not None:
                # No fitting tag was found, so we either append or do nothing.
                if x == 16384:
                    text += self.config.get(index, self.checkbox.isChecked())
                else:
                    return
            else:
                if match1:
                    # A fitting tag was found. Replace and we're happy.
                    text = re.sub(pattern, self.config.get(index, self.checkbox.isChecked()), text, 1)
                    self.line_edit.setText(text)
                elif match2:
                    text2 = re.sub(pattern, self.config.get(index, self.checkbox.isChecked()), text2, 1)
                    self.line_edit2.setText(text2)
        else:
            text = self.config.get(index, self.checkbox.isChecked())
            self.line_edit.setText(text)
