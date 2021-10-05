import random
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QPushButton, QTreeView
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem

app = QApplication(sys.argv)
model = QStandardItemModel()
model.setHorizontalHeaderItem(0, QStandardItem(""))
model.setHorizontalHeaderItem(1, QStandardItem(""))


class Fruit(QStandardItem):
    def __init__(self, name, juiciness, sweetness, shelf_life):
        super().__init__(name)
        self.setEditable(False)
        properties = zip(["Juiciness", "Sweetness", "Shelf Life"], [juiciness, sweetness, shelf_life])
        for label, value in properties:
            item = QStandardItem(label)
            item.setEditable(False)
            self.appendRow([item, QStandardItem(value)])


def add_entry():
    examples = [
        Fruit("Banana", "2", "8", "4"),
        Fruit("Apple", "5", "5", "10"),
        Fruit("Orange", "9", "5", "6"),
        Fruit("Grape", "8", "7", "5")
    ]
    item1 = examples[random.randrange(0, 3)]
    model.appendRow(item1)


def remove_entry(indices):
    rowsToBeRemoved = set()
    for index in indices:
        rowsToBeRemoved.add(index.row())
    for row in rowsToBeRemoved:
        model.removeRow(row)


main_window = QWidget()
layout = QVBoxLayout()

tree = QTreeView()
tree.setModel(model)

line1_layout = QHBoxLayout()
line1_layout.addSpacerItem(QSpacerItem(1, 0, hPolicy=QSizePolicy.MinimumExpanding))
plus_button = QPushButton("+")
plus_button.setStyleSheet("min-width: 30px; max-width:30px")
plus_button.clicked.connect(add_entry)
minus_button = QPushButton("-")
minus_button.setStyleSheet("min-width: 30px; max-width:30px")
minus_button.clicked.connect(lambda: remove_entry(tree.selectedIndexes()))
line1_layout.addWidget(minus_button)
line1_layout.addWidget(plus_button)

layout.addLayout(line1_layout)
layout.addWidget(tree)
main_window.setLayout(layout)

main_window.show()

sys.exit(app.exec_())
