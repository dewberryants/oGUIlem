import sys

from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from oguilem.configuration.properties import OGOLEMProperty, PersistentValue, PersistentItemDelegate

boolean = OGOLEMProperty("Boolean", PersistentValue(bool, True))
integer = OGOLEMProperty("Integer", PersistentValue(int, 2))
floating = OGOLEMProperty("Float", PersistentValue(float, 6.0))

app = QApplication(sys.argv)

layout = QFormLayout()
tree = QTreeView()
tree.setItemDelegate(PersistentItemDelegate())

model = QStandardItemModel()
model.setHorizontalHeaderItem(0, QStandardItem("Property"))
model.setHorizontalHeaderItem(1, QStandardItem("Value"))

model.appendRow(boolean.generate_item())
model.appendRow(integer.generate_item())
model.appendRow(floating.generate_item())

tree.setModel(model)
layout.addWidget(tree)

test_window = QWidget()
test_window.setLayout(layout)
test_window.show()

sys.exit(app.exec_())
