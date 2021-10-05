import PyQt5.QtWidgets as qW

from config import instance as conf


def run_app(argv: list):
    app = qW.QApplication(argv)
    main_window = OGUILEMMainWindow()
    main_window.show()
    app.exec_()


class OGUILEMMainWindow(qW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        size = (qW.qApp.desktop().screenGeometry().width() * 0.6,
                qW.qApp.desktop().screenGeometry().height() * 0.6)
        self.setGeometry(qW.qApp.desktop().screenGeometry().width() * 0.1 / 2,
                         qW.qApp.desktop().screenGeometry().height() * 0.1 / 2,
                         size[0], size[1])

        file_menu = self.menuBar().addMenu("File")
        q_open = qW.QAction("Open...", self)
        q_open.triggered.connect(self.open_file_dialog)
        file_menu.addAction(q_open)
        q_save = qW.QAction("Save...", self)
        file_menu.addAction(q_save)
        file_menu.addSeparator()
        q_exit = qW.QAction("Exit", self)
        q_exit.triggered.connect(qW.qApp.exit)
        file_menu.addAction(q_exit)

        calc_menu = self.menuBar().addMenu("Calculation")
        q_run = qW.QAction("Run...", self)
        calc_menu.addAction(q_run)
        q_out = qW.QAction("Stream output...", self)
        q_out.setEnabled(False)
        calc_menu.addAction(q_out)
        q_abort = qW.QAction("Abort", self)
        q_abort.setEnabled(False)
        calc_menu.addAction(q_abort)

        self.setCentralWidget(OGUILEMCalcWidget())
        self.setWindowTitle("oGUIlem")

    def open_file_dialog(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Open Config...", "", "OGOLEM Config Files (*.ogo)")
        if file_name:
            conf.load_from_file(file_name)


class OGUILEMCalcWidget(qW.QWidget):
    def __init__(self):
        super().__init__()
        layout = qW.QVBoxLayout()
        tabs = qW.QTabWidget()
        tabs.addTab(OGUILEMCalcInfoTab(), "Main")
        tabs.addTab(OGUILEMGeometryTab(), "Geometry")
        tabs.addTab(OGUILEMCalcInfoTab(), "Environment")
        tabs.addTab(OGUILEMCalcInfoTab(), "Advanced")
        tabs.setTabEnabled(2, False)
        tabs.setTabEnabled(3, False)

        layout.addWidget(tabs)
        self.setLayout(layout)


class OGUILEMCalcInfoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.runtype_box = None
        self.crossover_box = None
        self.mutation_box = None
        self.fitness_box = None
        self.init_ui()

    def init_ui(self):
        columns = qW.QHBoxLayout()

        layout_left = qW.QVBoxLayout()
        layout_left.addWidget(self.construct_runtype_group())
        layout_left.addWidget(self.construct_ga_group())
        layout_left.addWidget(self.construct_fitness_group())
        layout_left.addSpacerItem(qW.QSpacerItem(0, 1, vPolicy=qW.QSizePolicy.Expanding))
        columns.addLayout(layout_left)

        layout_right = qW.QVBoxLayout()
        layout_right.addWidget(self.construct_general_group())
        layout_right.addWidget(self.construct_sanity_group())
        layout_right.addSpacerItem(qW.QSpacerItem(0, 1, vPolicy=qW.QSizePolicy.Expanding))
        columns.addLayout(layout_right)

        self.setLayout(columns)

    def construct_runtype_group(self):
        runtype_group = qW.QGroupBox("Run Type")
        runtype_group.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        runtype_layout = qW.QFormLayout()
        self.runtype_box = OGUILEMRunTypeBox()
        runtype_layout.addWidget(self.runtype_box)
        runtype_group.setLayout(runtype_layout)
        return runtype_group

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

    def construct_fitness_group(self):
        group_fit = qW.QGroupBox("Fitness Function")
        group_fit.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        fit_layout = qW.QFormLayout()
        self.fitness_box = OGUILEMFitnessBox()
        fit_layout.addWidget(self.fitness_box)
        group_fit.setLayout(fit_layout)
        return group_fit

    def construct_general_group(self):
        group_general = qW.QGroupBox("General Settings")
        group_general.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        layout_gen = qW.QGridLayout()
        layout_gen.addWidget(qW.QLabel("Pool Size"), 0, 0)
        layout_gen.addWidget(SmartLineEdit(conf.options.values["PoolSize"]), 0, 1)
        layout_gen.addWidget(qW.QLabel("Global Optimization Iterations"), 1, 0)
        layout_gen.addWidget(qW.QLineEdit(), 1, 1)
        layout_gen.addWidget(qW.QLabel("Cell Size"), 2, 0)
        triple_layout = qW.QHBoxLayout()
        triple_layout.addWidget(qW.QLineEdit())
        triple_layout.addWidget(qW.QLineEdit())
        triple_layout.addWidget(qW.QLineEdit())
        layout_gen.addLayout(triple_layout, 2, 1)
        group_general.setLayout(layout_gen)
        return group_general

    def construct_sanity_group(self):
        group_sanity = qW.QGroupBox("Sanity Checks")
        group_sanity.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        layout_sanity = qW.QVBoxLayout()

        layout_upper = qW.QHBoxLayout()

        group_cd = qW.QGroupBox("Collision Detection")
        layout_cd = qW.QFormLayout()
        layout_cd.addWidget(qW.QCheckBox("Pre-Fitness"))
        layout_cd.addWidget(qW.QCheckBox("Post-Fitness"))
        group_cd.setLayout(layout_cd)

        layout_upper.addWidget(group_cd)

        group_dd = qW.QGroupBox("Dissociation Detection")
        layout_dd = qW.QFormLayout()
        layout_dd.addWidget(qW.QCheckBox("Pre-Fitness"))
        layout_dd.addWidget(qW.QCheckBox("Post-Fitness"))
        group_dd.setLayout(layout_dd)

        layout_upper.addWidget(group_dd)

        layout_sanity.addLayout(layout_upper)

        layout_lower = qW.QHBoxLayout()

        layout_lower.addWidget(qW.QLabel("Bond Detection Blow Factor"))
        layout_lower.addWidget(qW.QLineEdit())

        layout_sanity.addLayout(layout_lower)

        group_sanity.setLayout(layout_sanity)
        return group_sanity


class OGUILEMGeometryTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

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


class OGUILEMRunTypeBox(qW.QComboBox):
    def __init__(self):
        super().__init__()
        self.setModel(conf.runtype.get_model())
        conf.set_runtype(self.get_current_id())

    def get_current_id(self):
        return self.model().item(self.currentIndex()).id


class QHLine(qW.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(qW.QFrame.HLine)
        self.setFrameShadow(qW.QFrame.Sunken)


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


class OGUILEMFitnessBox(qW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = qW.QGridLayout()
        self.edit = qW.QLineEdit()
        self.edit.setReadOnly(True)
        layout.addWidget(self.edit, 1, 0)
        self.btn = qW.QPushButton("Edit...")
        self.btn.clicked.connect(self.open_edit)
        layout.addWidget(self.btn, 1, 1)
        self.setLayout(layout)

    def open_edit(self):
        pass


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


class SmartLineEdit(qW.QLineEdit):
    def __init__(self, connected_value):
        super().__init__()
        self.connected_value = connected_value
        self.connected_value.changed.connect(self.update_text)
        self.update_text()

    def update_text(self):
        self.setText(str(self.connected_value))

    def update_value(self, edit):
        self.connected_value.set(edit)
        self.setText(str(self.connected_value))
