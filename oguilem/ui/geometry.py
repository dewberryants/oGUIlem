import os

import PyQt5.QtCore as qC
import PyQt5.QtGui as qG
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.configuration.geometry import OGUILEMMolecule


class OGUILEMGeometryTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        layout = qW.QHBoxLayout()
        self.entity_display = qW.QLineEdit()
        self.entity_display.setReadOnly(True)
        self.entity_display.setStyleSheet("min-width: 40px; max-width:40px")
        conf.geometry.changed.connect(self.update_entities)
        self.accept_btn = qW.QPushButton("Apply")
        self.accept_btn.setEnabled(False)
        self.accept_btn.clicked.connect(self.update_current_molecule)
        self.accept_btn.setStyleSheet("min-width: 60px; max-width:80px")
        self.mol_list = GeometryMoleculeList(self)
        self.mol_content_display = MoleculeInspectorEdit(self.mol_list)
        self.mol_content_display.textChanged.connect(lambda: self.accept_btn.setEnabled(True))

        group1 = qW.QGroupBox("Molecules")
        layout_g1 = qW.QVBoxLayout()
        info_row = qW.QHBoxLayout()
        btn1 = qW.QPushButton("Add...")
        btn1.clicked.connect(self.open_mol_add)
        btn2 = qW.QPushButton("Remove")
        btn2.clicked.connect(self.mol_list.remove_mol)
        btn1.setStyleSheet("min-width: 60px; max-width:80px")
        btn2.setStyleSheet("min-width: 60px; max-width:80px")
        info_row.addWidget(btn1)
        info_row.addWidget(btn2)
        info_row.addSpacerItem(qW.QSpacerItem(1, 0, qW.QSizePolicy.Expanding))
        info_row.addWidget(qW.QLabel("Total Entities:"))

        info_row.addWidget(self.entity_display)
        layout_g1.addLayout(info_row)
        layout_g1.addWidget(self.mol_list)
        group1.setLayout(layout_g1)
        layout.addWidget(group1)
        group2 = qW.QGroupBox("Selected Molecule")
        layout_g2_header = qW.QGridLayout()
        layout_g2 = qW.QVBoxLayout()
        layout_g2_header.addWidget(qW.QLabel("Molecule Info"), 0, 0)
        layout_g2_header.addWidget(self.accept_btn, 0, 1)
        layout_g2.addLayout(layout_g2_header)
        layout_g2.addWidget(self.mol_content_display)
        charge_label = qW.QLabel("Molecule Charges")
        charge_label.setEnabled(False)
        layout_g2.addWidget(charge_label)
        charge_table = qW.QTableWidget()
        charge_table.setEnabled(False)
        layout_g2.addWidget(charge_table)
        spin_label = qW.QLabel("Molecule Spins")
        spin_label.setEnabled(False)
        layout_g2.addWidget(spin_label)
        spin_table = qW.QTableWidget()
        spin_table.setEnabled(False)
        layout_g2.addWidget(spin_table)
        group2.setLayout(layout_g2)
        layout.addWidget(group2)

        self.setLayout(layout)

    def update_entities(self):
        self.entity_display.setText(str(conf.geometry.num_entities()))

    def open_mol_add(self):
        popup = OGUILEMAddMolDialog(self)
        ret = popup.exec()
        if ret == 1:
            conf.geometry += popup.mol
            conf.file_manager.signal_modification()

    def update_current_molecule(self):
        new_content = self.mol_content_display.document().toPlainText().split("\n")
        self.mol_list.mod_mol(new_content)
        self.accept_btn.setEnabled(False)


class GeometryMoleculeList(qW.QListView):
    none_molecule = OGUILEMMolecule([""])
    selection_changed = qC.pyqtSignal(OGUILEMMolecule)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.accept_btn = parent.accept_btn
        self.setModel(qG.QStandardItemModel())
        self.selectionModel().selectionChanged.connect(self.handle_selection)
        conf.geometry.changed.connect(self.update_list_from_config)

    def update_list_from_config(self):
        row_before = self.selectionModel().currentIndex().row()
        self.selectionModel().clearSelection()
        self.model().removeRows(0, self.model().rowCount())
        for n in range(len(conf.geometry)):
            self.model().appendRow(qG.QStandardItem("Molecule " + str(n)))
        new_index = self.model().index(row_before, 0)
        self.selectionModel().select(new_index, qC.QItemSelectionModel.Select | qC.QItemSelectionModel.Rows)

    def handle_selection(self, selection: qC.QItemSelection):
        try:
            selected_row = selection.indexes()[0].row()
            self.selection_changed.emit(conf.geometry.molecules[selected_row])
        except IndexError:
            # Happens when something was deleted or added
            self.selection_changed.emit(self.none_molecule)
        self.accept_btn.setEnabled(False)

    def mod_mol(self, content):
        if self.model().rowCount() > 0:
            try:
                selected = self.selectionModel().selection().indexes()[0].row()
                conf.geometry.update_mol(selected, content)
                conf.file_manager.signal_modification()
            except IndexError:
                print("No valid selection!")

    def remove_mol(self):
        if self.model().rowCount() > 0:
            try:
                selected = self.selectionModel().selection().indexes()[0].row()
                conf.geometry.pop(selected)
                conf.file_manager.signal_modification()
            except IndexError:
                print("No valid selection!")


class MoleculeInspectorEdit(qW.QTextEdit):
    def __init__(self, parent: GeometryMoleculeList):
        super().__init__(parent=parent)
        self.parent().selection_changed.connect(self.update_content)

    def update_content(self, incoming):
        if incoming is GeometryMoleculeList.none_molecule:
            self.setText("")
        self.setText(str(incoming))


class OGUILEMAddMolDialog(qW.QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.text_cache = ""
        self.mol = OGUILEMMolecule([""])
        layout = qW.QVBoxLayout()

        grid = qW.QGridLayout()
        grid.addWidget(qW.QLabel("Molecule Copies"), 0, 0)
        self.mol_reps = qW.QLineEdit("1")
        self.mol_reps.setAlignment(qC.Qt.AlignRight)
        self.mol_reps.textChanged.connect(lambda: self.mol_reps.setStyleSheet(""))
        grid.addWidget(self.mol_reps, 0, 1)

        self.cbox = qW.QCheckBox("From File: ")
        self.cbox.setChecked(False)
        self.cbox.clicked.connect(self.cbox_clicked)
        grid.addWidget(self.cbox, 1, 0)

        file_layout = qW.QHBoxLayout()
        self.file_line = qW.QLineEdit()
        self.file_line.setEnabled(False)
        self.file_line.textChanged.connect(lambda: self.file_line.setStyleSheet(""))
        file_layout.addWidget(self.file_line)
        self.btn = qW.QPushButton("...")
        self.btn.setStyleSheet("min-width: 20px; max-width:40px")
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self.get_path)
        file_layout.addWidget(self.btn)

        bonds_layout = qW.QHBoxLayout()
        grid.addWidget(qW.QLabel("Bond List"), 2, 0)
        self.bonds_line = qW.QLineEdit()
        self.bonds_line.setPlaceholderText("Auto determine")
        self.bonds_line.textChanged.connect(lambda: self.bonds_line.setStyleSheet(""))
        bonds_layout.addWidget(self.bonds_line)
        self.btn2 = qW.QPushButton("...")
        self.btn2.setStyleSheet("min-width: 20px; max-width:40px")
        self.btn2.clicked.connect(self.get_path_bonds)
        bonds_layout.addWidget(self.btn2)

        grid.addLayout(file_layout, 1, 1)
        grid.addLayout(bonds_layout, 2, 1)

        layout.addLayout(grid)

        layout.addWidget(qW.QLabel("Input Block"))
        self.text_edit = qW.QTextEdit()
        self.text_edit.append("O    0.0    0.0    0.0")
        self.text_edit.append("H    1.0    0.0    0.0")
        self.text_edit.append("H    0.0    1.0    0.0")
        self.text_cache = self.text_edit.document().toPlainText()
        layout.addWidget(self.text_edit)

        btn_layout = qW.QHBoxLayout()
        accept = qW.QPushButton("Add")
        accept.clicked.connect(self.accept)
        cancel = qW.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btn_layout.addWidget(accept)
        btn_layout.addWidget(cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setWindowTitle("Add Molecule...")

    def accept(self) -> None:
        try:
            reps = int(self.mol_reps.text())
        except ValueError:
            print("Molecular Copies must be a positive Integer!")
            self.mol_reps.setStyleSheet("color: red")
            return
        self.mol.content = list()
        if reps > 1:
            self.mol.content.append("MoleculeRepetitions=%d" % reps)
        if self.bonds_line.text():
            path = self.bonds_line.text()
            if os.path.isfile(path):
                self.mol.content.append("BondMatrix=%s" % self.bonds_line.text())
            else:
                print("Invalid Path for Bond List!")
                self.bonds_line.setStyleSheet("color: red")
                return
        if self.cbox.isChecked():
            path = self.file_line.text()
            if os.path.isfile(path):
                self.mol.content.append("MoleculePath=%s" % path)
            else:
                print("Invalid Path for xyz File!")
                self.file_line.setStyleSheet("color: red")
                return
        else:
            text = self.text_edit.document().toPlainText()
            self.mol.content += text.split("\n")
        super().accept()

    def get_path(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Open Molecule File...", "", "XYZ (*.xyz)")
        if file_name:
            self.file_line.setText(file_name)

    def get_path_bonds(self):
        file_name, _ = qW.QFileDialog.getOpenFileName(self, "Open Bond List...", "", "LIST (*.list)")
        if file_name:
            self.bonds_line.setText(file_name)

    def cbox_clicked(self, checked):
        self.btn.setEnabled(checked)
        self.file_line.setEnabled(checked)
        self.text_edit.setEnabled(not checked)
        if checked:
            self.text_cache = self.text_edit.document().toPlainText()
            self.text_edit.setText("")
        else:
            self.text_edit.setText(self.text_cache)
