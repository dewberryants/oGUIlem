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


class OGUILEMCalcWidget(qW.QWidget):
    def __init__(self):
        super().__init__()
        layout = qW.QVBoxLayout()
        tabs = qW.QTabWidget()
        tabs.addTab(OGUILEMCalcInfoTab(), "Main")
        tabs.addTab(OGUILEMCalcInfoTab(), "Geometry")
        tabs.addTab(OGUILEMCalcInfoTab(), "Environment")
        tabs.addTab(OGUILEMCalcInfoTab(), "Advanced")
        tabs.setTabEnabled(1, False)
        tabs.setTabEnabled(2, False)
        tabs.setTabEnabled(3, False)

        layout.addWidget(tabs)
        self.setLayout(layout)


class OGUILEMCalcInfoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        columns = qW.QHBoxLayout()

        layout1 = qW.QVBoxLayout()

        runtype = qW.QFormLayout()
        runtype.addWidget(qW.QLabel("Runtype"))
        runtype_box = OGUILEMRunTypeBox()
        runtype.addWidget(runtype_box)

        layout1.addLayout(runtype)
        layout1.addWidget(QHLine())

        operators = qW.QFormLayout()
        operators.addWidget(qW.QLabel("Genetic Algorithm"))
        operators.addWidget(OGUILEMCrossOverBox())
        operators.addWidget(qW.QLabel("Mutation operators:"))
        operators.addWidget(qW.QListView())

        layout1.addLayout(operators)
        layout1.addWidget(QHLine())

        locopt = qW.QFormLayout()
        locopt.addWidget(qW.QLabel("Fitness Function"))
        locopt.addWidget(qW.QListView())

        layout1.addLayout(locopt)

        columns.addLayout(layout1)

        layout2 = qW.QFormLayout()
        layout2.addWidget(qW.QLabel("General Settings"))
        layout2.addWidget(qW.QCheckBox("Flag 1"))
        layout2.addWidget(qW.QCheckBox("Flag 2"))
        layout2.addWidget(qW.QCheckBox("Flag 3"))
        layout2.addWidget(qW.QCheckBox("Flag 4"))
        layout2.addWidget(qW.QCheckBox("Flag 5"))

        columns.addLayout(layout2)

        self.setLayout(columns)


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
        popup = OGUILEMCrossOverDialog(self)
        popup.exec()


class OGUILEMCrossOverDialog(qW.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.tree = qW.QTreeView()
        self.tree.setModel(conf.crossover.get_model())
        layout = qW.QVBoxLayout()
        line1_layout = qW.QHBoxLayout()
        self.combo_box = qW.QComboBox()
        self.combo_box.setModel(conf.crossover.get_choices())
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
        self.setWindowTitle("Crossovers")

    def add_entry(self):
        conf.crossover.add_choice_to_model(self.combo_box.currentIndex())

    def remove_entry(self, indices):
        rows = set()
        for index in indices:
            rows.add(index.row())
        for row in rows:
            self.tree.model().removeRow(row)
            break
