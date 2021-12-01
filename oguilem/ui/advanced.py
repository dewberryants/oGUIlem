import PyQt5.QtWidgets as qW

from oguilem.configuration import conf
from oguilem.ui.widgets import SmartCheckBox, SmartLineEdit, SmartSlider


class OGUILEMAdvancedTab(qW.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        columns = qW.QHBoxLayout()

        layout_left = qW.QVBoxLayout()
        layout_left.addWidget(self.construct_output_group())
        layout_left.addSpacerItem(qW.QSpacerItem(0, 1, vPolicy=qW.QSizePolicy.Expanding))
        columns.addLayout(layout_left)

        layout_right = qW.QVBoxLayout()
        layout_right.addWidget(self.construct_sanity_group())
        layout_right.addSpacerItem(qW.QSpacerItem(0, 1, vPolicy=qW.QSizePolicy.Expanding))
        columns.addLayout(layout_right)

        self.setLayout(columns)

    def construct_output_group(self):
        runtype_group = qW.QGroupBox("Output Control")
        runtype_group.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        runtype_layout = qW.QGridLayout()

        runtype_layout.addWidget(qW.QLabel("Debug Level"), 0, 0)
        debug_slider = SmartSlider(conf.options.values["DebugLevel"])
        runtype_layout.addWidget(debug_slider, 0, 1)
        runtype_layout.addWidget(SmartCheckBox("Silent Mode", conf.options.values["SilentMode"]), 1, 0)
        runtype_layout.addWidget(qW.QLabel("Genetic Record Buffer Size"), 2, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["GeneticRecordBufferSize"]), 2, 1)
        runtype_layout.addWidget(SmartCheckBox("Cluster Detailed Stats",
                                               conf.options.values["ClusterDetailedStats"]), 3, 0)
        runtype_layout.addWidget(qW.QLabel("Niching Printout after # Steps:"), 4, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["NichingAddToStats"]), 4, 1)
        runtype_layout.addWidget(qW.QLabel("Serialize Genetic Records After # Steps:"), 5, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["GeneticRecordsToSerial"]), 5, 1)
        runtype_layout.addWidget(qW.QLabel("Serialize Geometries After # Steps:"), 6, 0)
        runtype_layout.addWidget(SmartLineEdit(conf.options.values["GeometriesToSerial"]), 6, 1)
        runtype_layout.addWidget(SmartCheckBox("Serialize Pool after new Best",
                                               conf.options.values["SerializePoolAfterBest"]), 7, 0)
        runtype_layout.addWidget(SmartCheckBox("Write every Geometry", conf.options.values["WriteEveryGeometry"]), 8, 0)
        runtype_group.setLayout(runtype_layout)
        return runtype_group

    def construct_sanity_group(self):
        group_sanity = qW.QGroupBox("Sanity Checks")
        group_sanity.setSizePolicy(qW.QSizePolicy(qW.QSizePolicy.Preferred, qW.QSizePolicy.Fixed))
        layout_sanity = qW.QVBoxLayout()

        layout_upper = qW.QHBoxLayout()

        group_cd = qW.QGroupBox("Collision Detection")
        layout_cd = qW.QFormLayout()
        layout_cd.addWidget(SmartCheckBox("Pre-Fitness", conf.options.values["PreSanityCD"]))
        layout_cd.addWidget(SmartCheckBox("Post-Fitness", conf.options.values["PostSanityCD"]))
        layout_cd.addWidget(qW.QLabel("Bond Detection Blow Factor"))
        layout_cd.addWidget(SmartLineEdit(conf.options.values["BlowBondDetect"]))
        layout_cd.addWidget(qW.QLabel("Initial Bond Detection Blow Factor"))
        layout_cd.addWidget(SmartLineEdit(conf.options.values["BlowInitialBonds"]))
        group_cd.setLayout(layout_cd)

        layout_upper.addWidget(group_cd)

        group_dd = qW.QGroupBox("Dissociation Detection")
        layout_dd = qW.QFormLayout()
        layout_dd.addWidget(SmartCheckBox("Pre-Fitness", conf.options.values["PreSanityDD"]))
        layout_dd.addWidget(SmartCheckBox("Post-Fitness", conf.options.values["PostSanityDD"]))
        layout_dd.addWidget(qW.QLabel("Dissociation Detection Blow Factor"))
        layout_dd.addWidget(SmartLineEdit(conf.options.values["BlowFacDissoc"]))
        group_dd.setLayout(layout_dd)

        layout_upper.addWidget(group_dd)

        layout_sanity.addLayout(layout_upper)

        group_sanity.setLayout(layout_sanity)
        return group_sanity
