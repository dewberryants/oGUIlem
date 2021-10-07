from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QStyledItemDelegate


class PersistentValue:
    """
    A value object containing a single value, to allow call by reference for primitve types.
    """
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return str(self.value)

    def __class__(self):
        return self.type


class PersistentStandardItem(QStandardItem):
    """
    An augmented QStandardItem. OGOLEMProperties generate these from their persistant values.
    This, if put into a view using the PersistentItemDelegate, allows editing of individual persistant values
    by the user.
    """
    def __init__(self, value: PersistentValue):
        super().__init__(str(value))
        self.persistent_reference = value

    def text(self) -> str:
        return str(self.persistent_reference)

    def setText(self, atext: str) -> None:
        try:
            value = self.persistent_reference.type(atext)
        except (ValueError, TypeError):
            return
        self.persistent_reference.value = value
        self.setValue(value)

    def setValue(self, value) -> None:
        if value.__class__ is not self.persistent_reference.type:
            try:
                value = self.persistent_reference.type(value)
            except (ValueError, TypeError):
                return
        self.persistent_reference.value = value
        super().setText(str(self.persistent_reference))


class PersistentItemDelegate(QStyledItemDelegate):
    """
    A variant of QStyledItemDelegate that assumes the use of persistent Value items. Allows
    to directly access and edit the persistent values themselves.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        item = index.model().itemFromIndex(index)
        if item.persistent_reference.type is bool:
            item.setValue(not item.persistent_reference.value)
            return None
        else:
            return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index) -> None:
        item = model.itemFromIndex(index)
        item.setText(editor.text())


class OGOLEMProperty:
    """
    An abstract property that can also be used for simple single-value properties.
    """
    def __init__(self, name: str, value: PersistentValue):
        self.name = name
        self.value = value

    def generate_item(self):
        return [QStandardItem(self.name), PersistentStandardItem(self.value)]
