import PyQt5.QtCore as qC
import PyQt5.QtWidgets as qW

from oguilem.configuration import conf


class SmartLineEdit(qW.QLineEdit):
    def __init__(self, connected_value, minimum_size=False):
        super().__init__()
        self.setAlignment(qC.Qt.AlignRight)
        self.connected_value = connected_value
        self.connected_value.changed.connect(self.update_from_config)
        self.connected_value.update_requested.connect(self.update_to_config)
        self.connected_value.error.connect(self.error_box)
        self.textEdited.connect(conf.file_manager.signal_modification)
        self.update_from_config()
        if minimum_size:
            self.setSizePolicy(qW.QSizePolicy.Minimum, qW.QSizePolicy.Minimum)

    def update_from_config(self):
        self.setText(str(self.connected_value))

    def update_to_config(self):
        self.connected_value.set(self.text())

    def error_box(self):
        error_dialog = qW.QMessageBox()
        error_dialog.setStandardButtons(qW.QMessageBox.Ok)
        error_dialog.setText("Value Error! '%s' is not of type '%s'!" % (self.text(), str(self.connected_value.type)))
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()


class SmartTripleLineEdit(qW.QHBoxLayout):
    def __init__(self, connected_value):
        super().__init__()
        self.edit1 = SmartLineEdit(connected_value)
        self.edit2 = SmartLineEdit(connected_value)
        self.edit3 = SmartLineEdit(connected_value)
        self.addWidget(self.edit1)
        self.addWidget(self.edit2)
        self.addWidget(self.edit3)
        self.connected_value = connected_value
        self.connected_value.changed.connect(self.update_from_config)
        self.connected_value.update_requested.connect(self.update_to_config)
        self.update_from_config()

    def update_from_config(self):
        self.edit1.setText(str(self.connected_value.get(0)))
        self.edit2.setText(str(self.connected_value.get(1)))
        self.edit3.setText(str(self.connected_value.get(2)))

    def update_to_config(self):
        self.connected_value.set(self.edit1.text(), 0)
        self.connected_value.set(self.edit2.text(), 1)
        self.connected_value.set(self.edit3.text(), 2)


class SmartCheckBox(qW.QCheckBox):
    def __init__(self, label, connected_value):
        super().__init__(label)
        self.connected_value = connected_value
        self.connected_value.changed.connect(self.update_from_config)
        self.connected_value.update_requested.connect(self.update_to_config)
        self.clicked.connect(conf.file_manager.signal_modification)
        self.update_from_config()

    def update_from_config(self):
        if self.connected_value.value:
            self.setCheckState(qC.Qt.Checked)
        else:
            self.setCheckState(qC.Qt.Unchecked)

    def update_to_config(self):
        if self.isChecked():
            self.connected_value.set(True)
        else:
            self.connected_value.set(False)


class SmartSlider(qW.QSlider):
    def __init__(self, connected_value, ticks=3):
        super().__init__(qC.Qt.Horizontal)
        self.setTickInterval(1)
        self.setMinimum(0)
        self.setMaximum(ticks - 1)
        self.setTickPosition(qW.QSlider.TicksBelow)
        self.connected_value = connected_value
        self.connected_value.changed.connect(self.update_from_config)
        self.connected_value.update_requested.connect(self.update_to_config)
        self.sliderMoved.connect(conf.file_manager.signal_modification)
        self.update_from_config()

    def update_from_config(self):
        if self.connected_value.value >= self.maximum():
            self.setSliderPosition(self.maximum())
        elif self.connected_value.value <= 0:
            self.setSliderPosition(self.minimum())
        else:
            self.setSliderPosition(self.connected_value.value)

    def update_to_config(self):
        self.connected_value.set(self.sliderPosition())


class InactiveDelegate(qW.QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent: qW.QWidget, option, index) -> qW.QWidget:
        pass
