import PyQt5.QtWidgets as qW


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
