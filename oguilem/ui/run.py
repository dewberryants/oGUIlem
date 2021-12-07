import os
import re
import subprocess

import PyQt5.QtCore as qC
import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.resources import icon
from oguilem.ui.matplotlib import MoleculeVisualizerWidget


class OGUILEMRunOutputWindow(qW.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.main_window = parent
        self.last_fitness = None
        self.clock = qC.QTimer()
        self.clock.timeout.connect(self.update_molecule)
        self.display = qW.QTextEdit()
        self.display.setReadOnly(True)
        columns = qW.QHBoxLayout()
        layout = qW.QVBoxLayout()
        layout.addWidget(self.display)
        layout_btn = qW.QHBoxLayout()
        layout_btn.addSpacerItem(qW.QSpacerItem(0, 0, hPolicy=qW.QSizePolicy.Expanding))
        self.terminate_btn = qW.QPushButton("Terminate")
        self.terminate_btn.clicked.connect(self.terminate_run)
        layout_btn.addWidget(self.terminate_btn)
        layout.addLayout(layout_btn)
        self.visualizer = MoleculeVisualizerWidget()
        columns.addLayout(layout)
        columns.addWidget(self.visualizer)
        self.setLayout(columns)
        self.setWindowTitle("Run Output")
        self.setWindowIcon(qG.QIcon(icon))
        self.thread = None
        self.worker = None

    def start_run(self):
        w = round(self.main_window.width() * 0.4)
        h = round(self.main_window.height() * 0.4)
        x = round(self.main_window.x() + self.main_window.width())
        y = round(self.main_window.y())
        self.setGeometry(x, y, w, h)
        self.display.clear()
        self.visualizer.clear()
        self.show()
        # Figure out what to run where
        try:
            run_cmd = conf.ui.get_run_command()
        except RuntimeError as err:
            self.display.setText(str(err))
            return
        directory = os.path.dirname(conf.file_manager.current_filename)
        print("Running '%s' in directory '%s'..." % (run_cmd, directory))
        self.thread = qC.QThread()
        self.worker = OGUILEMRunWorker(run_cmd, directory)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.run_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.output.connect(self.handle_output)
        self.terminate_btn.setEnabled(True)
        self.thread.start()
        self.clock.start(5000)

    def update_molecule(self):
        wd = os.path.dirname(conf.file_manager.current_filename)
        bn = ".".join(os.path.basename(conf.file_manager.current_filename).split(".")[:-1])
        log_file = os.path.join(os.path.join(wd, bn), bn + ".log")
        pool = os.path.join(os.path.join(wd, bn), "IntermediateClusterPool.bin")
        if not os.path.exists(log_file):
            print(log_file, " does not exit!")
            return
        with open(log_file, "r") as logfile:
            line = logfile.readline()
            while line != "":
                old_line = line
                line = logfile.readline()
        match = re.search(r"fitness\s+(-?[0-9]+\.?[0-9]+)", old_line)
        if self.last_fitness is None or float(match[1]) < self.last_fitness:
            self.last_fitness = float(match[1])
            print("New best was found, fitness: ", match[1])
            self.visualizer.load_rank_0(pool)

    def terminate_run(self):
        if self.worker is not None:
            self.worker.terminate()

    def run_finished(self, return_code: int):
        self.terminate_btn.setEnabled(False)
        self.clock.stop()
        print("Run finished: ", return_code)

    def handle_output(self, incoming: str):
        self.display.insertPlainText(incoming)
        self.display.verticalScrollBar().setValue(self.display.verticalScrollBar().maximum())


class OGUILEMRunWorker(qC.QObject):
    finished = qC.pyqtSignal(int)
    output = qC.pyqtSignal(str)

    def __init__(self, run_cmd, directory):
        super().__init__()
        self.process = None
        self.run_cmd = run_cmd
        self.dir = directory

    def run(self):
        try:
            args = self.run_cmd.split()
            self.process = subprocess.Popen(args, cwd=self.dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            encoding='utf-8')
        except FileNotFoundError:
            print("Java path invalid! (FileNotFoundError)")
            self.finished.emit(-1)
        for line in self.process.stdout:
            if line == "":
                break
            self.output.emit(line)
        self.output.emit(self.process.stderr.read())
        self.finished.emit(self.process.returncode)

    def terminate(self):
        if self.process is not None:
            self.process.kill()
        self.finished.emit(-1)


class OGUILEMRunDialog(qW.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.start_run = parent.output_dialog.start_run
        self.setWindowTitle("Run...")
        w = round(self.parent().width() * 0.6)
        x = round(self.parent().x() + self.parent().width() * 0.4 / 2)
        y = round(self.parent().y() + self.parent().height() * 0.4 / 2)
        self.setGeometry(x, y, w, self.height())
        self.jre_edit = qW.QLineEdit()
        if conf.ui.java_path:
            self.jre_edit.setText(conf.ui.java_path)
        self.ogo_edit = qW.QLineEdit()
        if conf.ui.ogo_path:
            self.ogo_edit.setText(conf.ui.ogo_path)
        self.vm_args = qW.QLineEdit()
        if conf.ui.java_vm_variables:
            self.vm_args.setText(conf.ui.java_vm_variables)
        self.run_args = qW.QLineEdit()
        if conf.ui.ogo_args:
            self.run_args.setText(conf.ui.ogo_args)

        layout_main = qW.QVBoxLayout()

        jre_btn = qW.QPushButton("...")
        jre_btn.setStyleSheet("min-width: 20px; max-width:40px")
        jre_btn.clicked.connect(self.get_jre_path)

        ogo_btn = qW.QPushButton("...")
        ogo_btn.setStyleSheet("min-width: 20px; max-width:40px")
        ogo_btn.clicked.connect(self.get_ogo_path)

        layout = qW.QGridLayout()
        layout.addWidget(qW.QLabel("Java Runtime"), 0, 0)
        layout_jre = qW.QHBoxLayout()
        layout_jre.addWidget(self.jre_edit)
        layout_jre.addWidget(jre_btn)
        layout.addLayout(layout_jre, 0, 1)

        layout.addWidget(qW.QLabel("OGOLEM JAR"), 1, 0)
        layout_ogo = qW.QHBoxLayout()
        layout_ogo.addWidget(self.ogo_edit)
        layout_ogo.addWidget(ogo_btn)
        layout.addLayout(layout_ogo, 1, 1)

        layout.addWidget(qW.QLabel("Java VM Options"), 2, 0)
        layout.addWidget(self.vm_args, 2, 1)

        layout.addWidget(qW.QLabel("Run Options"), 3, 0)
        layout.addWidget(self.run_args, 3, 1)

        layout_main.addLayout(layout)

        run_btn = qW.QPushButton("Run!")
        run_btn.clicked.connect(self.accept)
        cancel_btn = qW.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        layout_btns = qW.QHBoxLayout()
        layout_btns.addWidget(run_btn)
        layout_btns.addWidget(cancel_btn)

        layout_main.addLayout(layout_btns)

        self.setLayout(layout_main)

    def get_jre_path(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Choose java runtime binary", "")
        if file_name:
            self.jre_edit.setText(file_name)

    def get_ogo_path(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Open Ogolem Runtime", "", "JAR (*.jar)")
        if file_name:
            self.ogo_edit.setText(file_name)

    def update_options(self):
        conf.ui.java_path = self.jre_edit.text().strip()
        conf.ui.java_vm_variables = self.vm_args.text().strip()
        conf.ui.ogo_path = self.ogo_edit.text().strip()
        conf.ui.ogo_args = self.run_args.text().strip()

    def accept(self) -> None:
        self.update_options()
        self.start_run()
        super().accept()

    def reject(self) -> None:
        self.update_options()
        super().reject()
