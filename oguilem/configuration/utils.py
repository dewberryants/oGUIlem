from PyQt5.QtCore import pyqtSignal, QObject


class ConnectedValue(QObject):
    changed = pyqtSignal()

    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = type(value)

    def get(self, index=-1):
        if self.type is list and index >= 0:
            return self.value[index]
        return self.value

    def set(self, value, index=-1):
        if self.type is list and index >= 0:
            self.value[index] = value
        elif type(value) is self.type:
            self.value = value
        else:
            raise ValueError("Could not set connected value!")
        self.changed.emit()

    def __str__(self):
        return str(self.value)
