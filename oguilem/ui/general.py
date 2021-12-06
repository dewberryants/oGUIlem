import traceback

import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.resources import icon
from oguilem.resources import presets
from oguilem.ui.advanced import OGUILEMAdvancedTab
from oguilem.ui.fitness import OGUILEMFitnessTab
from oguilem.ui.ga import OGUILEMGeneticAlgoTab
from oguilem.ui.geometry import OGUILEMGeometryTab
from oguilem.ui.run import OGUILEMRunDialog, OGUILEMRunOutputWindow
from oguilem.ui.widgets import SmartLineEdit


class OGUILEMApplication(qW.QApplication):
    def __init__(self, argv):
        super().__init__(argv)

    def run(self) -> int:
        main_window = OGUILEMMainWindow()
        main_window.show()
        return self.exec_()


class OGUILEMMainWindow(qW.QMainWindow):
    def __init__(self):
        super().__init__()
        if not conf.ui.window_position:
            conf.ui.window_position = ((qW.qApp.desktop().screenGeometry().width() - self.geometry().width()) / 2,
                                       (qW.qApp.desktop().screenGeometry().height() - self.geometry().height()) / 2)
        if not conf.ui.window_size:
            conf.ui.window_size = (self.geometry().width(), self.geometry().height())
        x, y = conf.ui.window_position
        width, height = conf.ui.window_size
        self.setGeometry(x, y, width, height)
        self.output_dialog = OGUILEMRunOutputWindow(self)
        self.run_dialog = OGUILEMRunDialog(self)
        self.init_ui()
        conf.file_manager.config_modified.connect(self.update_window_title)

    def init_ui(self):
        file_menu = self.menuBar().addMenu("File")
        q_open = qW.QAction("Open...", self)
        q_open.triggered.connect(self.open_file_dialog)
        file_menu.addAction(q_open)
        q_save = qW.QAction("Save...", self)
        q_save.triggered.connect(self.save_file_dialog)
        file_menu.addAction(q_save)
        file_menu.addSeparator()
        q_exit = qW.QAction("Exit", self)
        q_exit.triggered.connect(qW.qApp.exit)
        file_menu.addAction(q_exit)

        calc_menu = self.menuBar().addMenu("Calculation")
        q_run = qW.QAction("Run...", self)
        q_run.triggered.connect(self.open_run_dialog)
        calc_menu.addAction(q_run)
        q_out = qW.QAction("Stream output...", self)
        q_out.setEnabled(False)
        calc_menu.addAction(q_out)
        q_abort = qW.QAction("Abort", self)
        q_abort.setEnabled(False)
        calc_menu.addAction(q_abort)

        self.setCentralWidget(OGUILEMCentralWidget())
        self.setWindowTitle("oGUIlem")
        self.setWindowIcon(qG.QIcon(icon))

    def open_run_dialog(self):
        if conf.file_manager.unsaved_changes:
            error_dialog = qW.QMessageBox()
            error_dialog.setStandardButtons(qW.QMessageBox.Ok)
            error_dialog.setText("Unsaved Changes! Please save to file before running!")
            error_dialog.setWindowTitle("Unsaved Changes")
            error_dialog.exec_()
        else:
            self.run_dialog.exec_()

    def update_window_title(self, file_name):
        if file_name:
            self.setWindowTitle("oGUIlem - " + file_name)
        elif self.windowTitle().strip()[-2:] != " *":
            self.setWindowTitle(self.windowTitle().strip() + " *")

    def open_file_dialog(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Open Config...", "", "OGOLEM Config Files (*.ogo)")
        if file_name:
            try:
                conf.load_from_file(file_name)
            except IOError:
                error_dialog = qW.QMessageBox()
                error_dialog.setStandardButtons(qW.QMessageBox.Ok)
                error_dialog.setText("Could not successfully parse the input file! \n\n"
                                     + traceback.format_exc())
                error_dialog.setWindowTitle("Error")
                error_dialog.exec_()

    def save_file_dialog(self):
        file_name, _ = qW.QFileDialog.getSaveFileName(self, "Save Config...", "", "OGOLEM Config Files (*.ogo)")
        if file_name:
            conf.save_to_file(file_name)

    def closeEvent(self, a0) -> None:
        conf.ui.window_position = (self.geometry().x(), self.geometry().y())
        conf.ui.window_size = (self.geometry().width(), self.geometry().height())
        super().closeEvent(a0)


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

        layout.addWidget(qW.QLabel("Welcome. Start by selecting a Preset from the Box below!"))

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

        expl_label = qW.QLabel("Be aware that by default, Sanity Checks are active (see 'Advanced' Tab)."
                               " If your ogolem run is not producing any individuals, you might need to adjust"
                               " the BlowFactors (bond tolerances) or debug the problem by turning up the"
                               " Debug Level.")
        expl_label.setWordWrap(True)
        layout.addWidget(expl_label)

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
        self.last_index = -1
        self.setCurrentIndex(-1)
        self.currentIndexChanged.connect(self.change_preset)
        self.reverse = False

    def change_preset(self):
        if self.reverse:
            return
        if self.last_index == -1:
            index = self.currentIndex()
            conf.load_from_file(presets[index][2], preset=True)
            self.last_index = index
            return
        error_dialog = qW.QMessageBox()
        error_dialog.setStandardButtons(qW.QMessageBox.Yes | qW.QMessageBox.Cancel)
        error_dialog.setDefaultButton(qW.QMessageBox.Cancel)
        error_dialog.setText("You are about to change presets, which will override any unsaved changes! Continue?")
        error_dialog.setWindowTitle("Preset Change")
        x = error_dialog.exec_()
        if x == 16384:
            index = self.currentIndex()
            conf.load_from_file(presets[index][2], preset=True)
            self.last_index = index
        else:
            self.reverse = True
            self.setCurrentIndex(self.last_index)
            self.reverse = False
