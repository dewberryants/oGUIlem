from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class ConfigFileManager(QObject):
    config_modified = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_filename = ""
        self.unsaved_changes = True

    def signal_modification(self):
        self.unsaved_changes = True
        self.config_modified.emit("")

    def signal_saved(self, file_name: str):
        self.unsaved_changes = False
        self.current_filename = file_name
        self.config_modified.emit(file_name)


class ConnectedValue(QObject):
    changed = pyqtSignal()
    update_requested = pyqtSignal()
    error = pyqtSignal()

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
            try:
                self.value = self.type(value)
            except ValueError:
                self.error.emit()
                return
        self.changed.emit()

    def request_update(self):
        self.update_requested.emit()

    def __str__(self):
        return str(self.value)


class BuildingBlockHelper:
    def __init__(self, config):
        self.table = list()
        # Config is a dict of _Node items
        for key in config:
            label = key if config[key].label is None else config[key].label
            required = ""
            optional = ""
            divider = config[key].divider
            for item in config[key].opts:
                item_label = item.id if item.label is None else item.label
                if item.required:
                    if "<" in item.descr and ">" in item.descr:
                        descr = item.descr.replace("<", "&lt;").replace(">", "&gt;")
                        required += item_label + "<font color=\"red\">" + descr + "</font>" + divider
                    else:
                        required += item_label + item.descr + divider
                else:
                    optional += item_label + item.descr + divider
            if len(required) > 0 and required[-1] == divider:
                required = required[:-1]
            if len(optional) > 0 and optional[-1] == divider:
                optional = optional[:-1]
            self.table.append((config[key].name, config[key].descr, label, required, optional))

    def get(self, index: int, optionals=False) -> str:
        text = self.table[index][2]
        required_exists = len(self.table[index][3]) > 0
        if required_exists:
            text += self.table[index][3]
        if optionals and len(self.table[index][4]) > 0:
            if required_exists:
                text += ","
            text += self.table[index][4]
        return text


class _NodeItem(QStandardItem):
    def __init__(self, node, ignore_opts=False):
        super().__init__()
        self.choices = None
        if node.id:
            self.id = node.id
        if node.name:
            self.setText(node.name)
        if node.descr:
            self.setToolTip(node.descr)
        if node.opts and not ignore_opts:
            for opt in node.opts:
                if len(opt.opts) >= 1:
                    choices = QStandardItemModel()
                    for opt_opt in opt.opts:
                        opt_item = _NodeItem(opt_opt, ignore_opts=True)
                        if opt_opt.user_defined:
                            opt_item.setEditable(True)
                        choices.appendRow(opt_item)
                    item = _NodeItem(opt, ignore_opts=True)
                    item.choices = choices
                    self.appendRow([item, choices.item(0, 0).clone()])
                else:
                    opt_item = _NodeItem(opt)
                    if opt.user_defined:
                        opt_item.setEditable(True)
                    self.appendRow([opt_item, _EmptyItem()])
        self.setEditable(False)

    def clone(self):
        ret = super().clone()
        rows = self.rowCount()
        if rows > 0:
            for n in range(rows):
                ret.appendRow([self.child(n, 0).clone(), self.child(n, 1).clone()])
        return ret


class _EmptyItem(QStandardItem):
    def __init__(self):
        super().__init__("")
        self.setEditable(False)
