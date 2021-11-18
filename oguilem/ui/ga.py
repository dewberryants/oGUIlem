import PyQt5.QtWidgets as qW


class OGUILEMGeneticAlgoTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        columns = qW.QHBoxLayout()

        layout_left = qW.QVBoxLayout()

        group1 = qW.QGroupBox("Crossover Operators")
        layout1 = qW.QVBoxLayout()
        layout1.addWidget(qW.QTextEdit())
        layout1.addWidget(qW.QTabWidget())
        group1.setLayout(layout1)

        group2 = qW.QGroupBox("Mutation Operators")
        layout2 = qW.QVBoxLayout()
        layout2.addWidget(qW.QTextEdit())
        layout2.addWidget(qW.QTabWidget())
        group2.setLayout(layout2)

        layout_left.addWidget(group1)
        layout_left.addWidget(group2)

        layout_right = qW.QVBoxLayout()

        group3 = qW.QGroupBox("General GA Settings")
        layout3 = qW.QVBoxLayout()
        layout3.addWidget(qW.QCheckBox("Test"))
        group3.setLayout(layout3)
        layout_right.addWidget(group3)

        columns.addLayout(layout_left)
        columns.addLayout(layout_right)
        self.setLayout(columns)
