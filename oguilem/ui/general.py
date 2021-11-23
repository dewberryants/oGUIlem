import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.resources import presets
from oguilem.ui.advanced import OGUILEMAdvancedTab
from oguilem.ui.fitness import OGUILEMFitnessTab
from oguilem.ui.ga import OGUILEMGeneticAlgoTab
from oguilem.ui.geometry import OGUILEMGeometryTab
from oguilem.ui.widgets import SmartLineEdit


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
        tabs.addTab(OGUILEMAdvancedTab(), "Advanced")

        layout.addWidget(tabs)
        self.setLayout(layout)


class OGUILEMCalcInfoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = qW.QVBoxLayout()

        group = qW.QGroupBox("OGOLEM Run Preset")
        layout_group = qW.QVBoxLayout()
        layout_group.addWidget(OGUILEMPresetBox())
        group.setLayout(layout_group)

        layout.addWidget(group)

        layout_gen = qW.QGridLayout()
        layout_gen.addWidget(qW.QLabel("Pool Size"), 0, 0)
        layout_gen.addWidget(SmartLineEdit(conf.options.values["PoolSize"]), 0, 1)
        layout_gen.addWidget(qW.QLabel("Global Optimization Iterations"), 1, 0)
        layout_gen.addWidget(SmartLineEdit(conf.options.values["NumberOfGlobIterations"]), 1, 1)

        layout.addLayout(layout_gen)

        layout.addSpacerItem(qW.QSpacerItem(0, 1, vPolicy=qW.QSizePolicy.Expanding))

        self.setLayout(layout)


class OGUILEMPresetBox(qW.QComboBox):
    def __init__(self):
        super().__init__()
        model = qG.QStandardItemModel()
        for entry in presets:
            model.appendRow(qG.QStandardItem(entry[0]))
        self.setModel(model)
        self.last_index = 0
        self.setCurrentIndex(0)
        conf.load_from_file(presets[0][2])
        self.currentIndexChanged.connect(self.change_preset)
        self.reverse = False

    def change_preset(self):
        if self.reverse:
            return
        error_dialog = qW.QMessageBox()
        error_dialog.setStandardButtons(qW.QMessageBox.Yes | qW.QMessageBox.Cancel)
        error_dialog.setDefaultButton(qW.QMessageBox.Cancel)
        error_dialog.setText("You are about to change presets, which will override any unsaved changes! Continue?")
        x = error_dialog.exec_()
        if x == 16384:
            index = self.currentIndex()
            conf.load_from_file(presets[index][2])
            self.last_index = index
        else:
            self.reverse = True
            self.setCurrentIndex(self.last_index)
            self.reverse = False
