import PyQt5.QtWidgets as qW

from config import OGUILEMConfig


def run_app(argv: list):
    app = qW.QApplication(argv)
    main_window = OGUILEMMainWindow()
    main_window.show()
    app.exec_()


class OGUILEMMainWindow(qW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = OGUILEMConfig()
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

        self.setCentralWidget(OGUILEMCalcWidget(self.config))


class OGUILEMCalcWidget(qW.QWidget):
    def __init__(self, config: OGUILEMConfig):
        super().__init__()
        layout = qW.QVBoxLayout()
        tabs = qW.QTabWidget()
        tabs.addTab(OGUILEMCalcInfoTab(config), "Main")
        tabs.addTab(OGUILEMCalcInfoTab(config), "Geometry")
        tabs.addTab(OGUILEMCalcInfoTab(config), "Environment")
        tabs.addTab(OGUILEMCalcInfoTab(config), "Advanced")
        tabs.setTabEnabled(1, False)
        tabs.setTabEnabled(2, False)
        tabs.setTabEnabled(3, False)

        layout.addWidget(tabs)
        self.setLayout(layout)


class OGUILEMCalcInfoTab(qW.QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        columns = qW.QHBoxLayout()

        layout1 = qW.QVBoxLayout()

        runtype = qW.QFormLayout()
        runtype.addWidget(qW.QLabel("Runtype"))
        runtype_box = OGUILEMRunTypeBox(self.config.get_runtypes())
        runtype.addWidget(runtype_box)

        layout1.addLayout(runtype)
        layout1.addWidget(QHLine())

        operators = qW.QFormLayout()
        operators.addWidget(qW.QLabel("Genetic Algorithm"))
        operators.addWidget(qW.QLabel("Crossover operators:"))
        operators.addWidget(qW.QListView())
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
    def __init__(self, runtypes):
        super().__init__()


class QHLine(qW.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(qW.QFrame.HLine)
        self.setFrameShadow(qW.QFrame.Sunken)
