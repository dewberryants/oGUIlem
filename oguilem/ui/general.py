import PyQt5.QtCore as qC
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.ui.fitness import OGUILEMFitnessTab
from oguilem.ui.ga import OGUILEMGeneticAlgoTab
from oguilem.ui.geometry import OGUILEMGeometryTab
from oguilem.ui.widgets import SmartCheckBox, SmartLineEdit, SmartTripleLineEdit


class OGUILEMApplication(qW.QApplication):
    def __init__(self, argv):
        super().__init__(argv)

    def run(self):
        main_window = OGUILEMMainWindow()
        main_window.show()
        self.exec_()


class OGUILEMMainWindow(qW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry((qW.qApp.desktop().screenGeometry().width() - self.geometry().width()) / 2,
                         (qW.qApp.desktop().screenGeometry().height() - self.geometry().height()) / 2,
                         self.geometry().width(), self.geometry().height())

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

        self.setCentralWidget(OGUILEMCentralWidget())
        self.setWindowTitle("oGUIlem")

    def open_file_dialog(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Open Config...", "", "OGOLEM Config Files (*.ogo)")
        if file_name:
            conf.load_from_file(file_name)


class OGUILEMCentralWidget(qW.QWidget):
    def __init__(self):
        super().__init__()
        layout = qW.QVBoxLayout()
        tabs = qW.QTabWidget()
        tabs.addTab(OGUILEMCalcInfoTab(), "Main")
        tabs.addTab(OGUILEMGeometryTab(), "Geometry")
        tabs.addTab(OGUILEMFitnessTab(), "Fitness Function")
        tabs.addTab(OGUILEMGeneticAlgoTab(), "Genetic Algorithm")
        tabs.addTab(OGUILEMCalcInfoTab(), "Advanced")
        tabs.setTabEnabled(4, False)

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
        layout_left.addWidget(self.construct_output_group())
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

    def construct_output_group(self):
        runtype_group = qW.QGroupBox("Output Control")
        runtype_group.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        runtype_layout = qW.QGridLayout()

        runtype_layout.addWidget(qW.QLabel("Debug Level"), 0, 0)
        debug_slider = qW.QSlider(qC.Qt.Horizontal)
        debug_slider.setTickInterval(1)
        debug_slider.setMinimum(0)
        debug_slider.setMaximum(2)
        debug_slider.setTickPosition(qW.QSlider.TicksBelow)
        runtype_layout.addWidget(debug_slider, 0, 1)
        runtype_layout.addWidget(SmartCheckBox("Silent Mode", conf.options.values["SilentMode"]), 1, 0)
        runtype_layout.addWidget(qW.QLabel("Genetic Record Buffer Size"), 2, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["GeneticRecordBufferSize"]), 2, 1)
        runtype_layout.addWidget(SmartCheckBox("Cluster Detailed Stats",
                                               conf.options.values["ClusterDetailedStats"]), 3, 0)
        runtype_layout.addWidget(qW.QLabel("Niching Printout after # Steps:"), 4, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["NichingAddToStats"]), 4, 1)
        runtype_layout.addWidget(qW.QLabel("Serialize Genetic Records After # Steps:"), 5, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["GeneticRecordsToSerial"]), 5, 1)
        runtype_layout.addWidget(qW.QLabel("Serialize Geometries After # Steps:"), 6, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["GeometriesToSerial"]), 6, 1)
        runtype_layout.addWidget(SmartCheckBox("Serialize Pool after new Best",
                                               conf.options.values["SerializePoolAfterBest"]), 7, 0)
        runtype_layout.addWidget(SmartCheckBox("Write every Geometry", conf.options.values["WriteEveryGeometry"]), 8, 0)
        runtype_group.setLayout(runtype_layout)
        return runtype_group

    def construct_general_group(self):
        group_general = qW.QGroupBox("General Settings")
        group_general.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        layout_gen = qW.QGridLayout()
        layout_gen.addWidget(qW.QLabel("Pool Size"), 0, 0)
        layout_gen.addWidget(SmartLineEdit(conf.options.values["PoolSize"]), 0, 1)
        layout_gen.addWidget(qW.QLabel("Global Optimization Iterations"), 1, 0)
        layout_gen.addWidget(SmartLineEdit(conf.options.values["NumberOfGlobIterations"]), 1, 1)
        layout_gen.addWidget(qW.QLabel("Cell Size"), 2, 0)
        triple_layout = SmartTripleLineEdit(conf.options.values["CellSize"])
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
        layout_cd.addWidget(SmartCheckBox("Pre-Fitness", conf.options.values["PreSanityCD"]))
        layout_cd.addWidget(SmartCheckBox("Post-Fitness", conf.options.values["PostSanityCD"]))
        layout_cd.addWidget(qW.QLabel("Bond Detection Blow Factor"))
        layout_cd.addWidget(SmartLineEdit(conf.options.values["BlowBondDetect"]))
        layout_cd.addWidget(qW.QLabel("Initial Bond Detection Blow Factor"))
        layout_cd.addWidget(SmartLineEdit(conf.options.values["BlowInitialBonds"]))
        group_cd.setLayout(layout_cd)

        layout_upper.addWidget(group_cd)

        group_dd = qW.QGroupBox("Dissociation Detection")
        layout_dd = qW.QFormLayout()
        layout_dd.addWidget(SmartCheckBox("Pre-Fitness", conf.options.values["PreSanityDD"]))
        layout_dd.addWidget(SmartCheckBox("Post-Fitness", conf.options.values["PostSanityDD"]))
        layout_dd.addWidget(qW.QLabel("Dissociation Detection Blow Factor"))
        layout_dd.addWidget(SmartLineEdit(conf.options.values["BlowFacDissoc"]))
        group_dd.setLayout(layout_dd)

        layout_upper.addWidget(group_dd)

        layout_sanity.addLayout(layout_upper)

        group_sanity.setLayout(layout_sanity)
        return group_sanity


class OGUILEMRunTypeBox(qW.QComboBox):
    def __init__(self):
        super().__init__()
