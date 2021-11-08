import PyQt5.QtWidgets as qW

from oguilem.configuration import conf


class OGUILEMGeneticAlgoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def construct_ga_group(self):
        group_ga = qW.QGroupBox("Genetic Algorithm")
        group_ga.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        operators = qW.QFormLayout()
        self.crossover_box = OGUILEMCrossOverBox()
        operators.addWidget(self.crossover_box)
        self.mutation_box = OGUILEMMutationsBox()
        operators.addWidget(self.mutation_box)
        group_ga.setLayout(operators)
        return group_ga

    def init_ui(self):
        layout = qW.QVBoxLayout()

        info_row = qW.QHBoxLayout()
        btn1 = qW.QPushButton("Add...")
        btn2 = qW.QPushButton("Remove")
        btn1.setStyleSheet("min-width: 60px; max-width:80px")
        btn2.setStyleSheet("min-width: 60px; max-width:80px")
        info_row.addWidget(btn1)
        info_row.addWidget(btn2)
        info_row.addSpacerItem(qW.QSpacerItem(1, 0, qW.QSizePolicy.Expanding))
        info_row.addWidget(qW.QLabel("Total Entities:"))
        line_edit = qW.QLineEdit()
        line_edit.setReadOnly(True)
        line_edit.setStyleSheet("min-width: 40px; max-width:40px")
        info_row.addWidget(line_edit)
        layout.addLayout(info_row)

        table_view = qW.QTableView()
        layout.addWidget(table_view)

        self.setLayout(layout)


class OGUILEMCrossOverBox(qW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = qW.QGridLayout()
        layout.addWidget(qW.QLabel("Crossover operators:"), 0, 0)
        self.edit = qW.QLineEdit()
        self.edit.setReadOnly(True)
        layout.addWidget(self.edit, 1, 0)
        self.btn = qW.QPushButton("Edit...")
        self.btn.clicked.connect(self.open_edit)
        layout.addWidget(self.btn, 1, 1)
        self.setLayout(layout)

    def open_edit(self):
        popup = OGUILEMConfigEditDialog(self, conf.crossover, "Edit Crossovers...")
        popup.exec()


class OGUILEMMutationsBox(qW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = qW.QGridLayout()
        layout.addWidget(qW.QLabel("Mutation operators:"), 0, 0)
        self.edit = qW.QLineEdit()
        self.edit.setReadOnly(True)
        layout.addWidget(self.edit, 1, 0)
        self.btn = qW.QPushButton("Edit...")
        self.btn.clicked.connect(self.open_edit)
        layout.addWidget(self.btn, 1, 1)
        self.setLayout(layout)

    def open_edit(self):
        popup = OGUILEMConfigEditDialog(self, conf.mutation, "Edit Mutations...")
        popup.exec()


class OGUILEMConfigEditDialog(qW.QDialog):
    def __init__(self, parent, config, title):
        super().__init__(parent)
        self.config = config
        self.tree = qW.QTreeView()
        self.tree.setModel(self.config.get_model())
        layout = qW.QVBoxLayout()
        line1_layout = qW.QHBoxLayout()
        self.combo_box = qW.QComboBox()
        self.combo_box.setModel(self.config.get_choices())
        line1_layout.addWidget(self.combo_box)
        plus_button = qW.QPushButton("+")
        plus_button.setStyleSheet("min-width: 30px; max-width:30px")
        plus_button.clicked.connect(self.add_entry)
        minus_button = qW.QPushButton("-")
        minus_button.setStyleSheet("min-width: 30px; max-width:30px")
        minus_button.clicked.connect(lambda: self.remove_entry(self.tree.selectedIndexes()))
        line1_layout.addWidget(plus_button)
        line1_layout.addWidget(minus_button)
        layout.addLayout(line1_layout)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.setWindowTitle(title)

    def add_entry(self):
        self.config.add_choice_to_model(self.combo_box.currentIndex())

    def remove_entry(self, indices):
        rows = set()
        for index in indices:
            rows.add(index.row())
        for row in rows:
            self.tree.model().removeRow(row)
            break
