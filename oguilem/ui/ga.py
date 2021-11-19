import re

import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.configuration.utils import BuildingBlockHelper, ConnectedValue
from oguilem.resources import globopt
from oguilem.ui.widgets import InactiveDelegate


class OGUILEMGeneticAlgoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = qW.QTabWidget()
        self.init_ui()

    def init_ui(self):
        columns = qW.QHBoxLayout()

        layout_left = qW.QVBoxLayout()

        checkbox = qW.QCheckBox("Add all optional Settings (with their default values)")
        crossover_display = ConnectedDisplay(conf.globopt.crossover, "<Choose a crossover operator by double-clicking>")
        mutation_display = ConnectedDisplay(conf.globopt.mutation, "<Choose a mutation operator by double-clicking>")

        layout_left.addWidget(qW.QLabel("Crossover Operator"))
        layout_left.addWidget(crossover_display)
        layout_left.addWidget(qW.QLabel("Mutation Operator"))
        layout_left.addWidget(mutation_display)
        layout_left.addWidget(qW.QLabel("Library of Operators"))
        layout_left.addWidget(checkbox)

        mutations, crossovers = globopt
        self.tabs.addTab(BlockProvider(crossover_display, crossovers, checkbox, "Crossover", "CROSSOVER"), "Crossovers")
        self.tabs.addTab(BlockProvider(mutation_display, mutations, checkbox, "Mutation", "MUTATION"), "Mutations")
        layout_left.addWidget(self.tabs)

        layout_right = qW.QVBoxLayout()

        group3 = qW.QGroupBox("General GA Settings")
        layout3 = qW.QVBoxLayout()
        layout3.addWidget(qW.QCheckBox("Test"))
        group3.setLayout(layout3)
        layout_right.addWidget(group3)

        columns.addLayout(layout_left)
        columns.addLayout(layout_right)
        self.setLayout(columns)

    def showEvent(self, a0) -> None:
        widget = self.tabs.widget(0)
        widget.horizontalHeader().reset()
        widget.verticalHeader().reset()


class ConnectedDisplay(qW.QTextEdit):
    def __init__(self, value: ConnectedValue, placeholder_text: str):
        super().__init__()
        self.value = value
        self.value.changed.connect(self.update_from_config)
        self.textChanged.connect(self.update_to_config)
        self.setPlaceholderText(placeholder_text)
        self.setLineWrapMode(qW.QTextEdit.NoWrap)
        self.setMaximumHeight(2 * self.fontMetrics().height() + self.fontMetrics().lineSpacing())
        self.setSizePolicy(qW.QSizePolicy.Minimum, qW.QSizePolicy.Preferred)

    def update_from_config(self):
        self.document().setPlainText(self.value.get())

    def update_to_config(self):
        # Set directly to circumvent signal cascade
        self.value.value = self.document().toPlainText()


class BlockProvider(qW.QTableView):
    def __init__(self, line_edit: qW.QTextEdit, config, checkbox: qW.QCheckBox, column_header="0", help_tag="0"):
        super().__init__()
        self.config = BuildingBlockHelper(config)
        self.checkbox = checkbox
        self.setWordWrap(True)
        self.setCornerButtonEnabled(False)
        self.setSelectionMode(qW.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(qW.QAbstractItemView.SelectRows)
        self.setItemDelegate(InactiveDelegate())
        self.line_edit: qW.QTextEdit = line_edit
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
            error_dialog = qW.QMessageBox()
            error_dialog.setStandardButtons(qW.QMessageBox.Yes | qW.QMessageBox.Cancel)
            error_dialog.setDefaultButton(qW.QMessageBox.Cancel)
            error_dialog.setText("No sensible space for this. Append in new line?")
            x = None
            # Check the corresponding tags and replace (seems a little smarter)
            pattern = r'<span style=" color:#ff0000;">&lt;' + self.help_tag + '&gt;</span>'
            if not re.search(pattern, text):
                x = error_dialog.exec_()
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
