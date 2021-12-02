import unittest

from oguilem.configuration.geometry import OGUILEMGeometryConfig, OGUILEMMolecule


class GeometryUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = OGUILEMGeometryConfig()
        self.mol = OGUILEMMolecule(["N/A"])

    def tearDown(self) -> None:
        self.conf = None
        self.mol = None

    def test_alloc_conf(self):
        self.assertIsNotNone(self.conf)

    def test_alloc_mol(self):
        self.assertIsNotNone(self.mol)

    def test_init_geom(self):
        self.assertIs(len(self.conf), 0)

    def test_add_mol(self):
        org = len(self.conf)
        self.conf += self.mol
        self.assertIs(len(self.conf), org + 1)

    def test_add_wrong(self):
        self.assertRaises(TypeError, self.conf.__iadd__, "bad")

    def test_pop(self):
        self.conf += self.mol
        self.assertIs(self.conf.pop(-1), self.mol)

    def test_parse(self):
        block = ["NumberOfParticles=2",
                 "<MOLECULE>",
                 "MoleculeRepetitions=2",
                 "O;1;2;3",
                 "H;1;3;3",
                 "H;1;2;4",
                 "</MOLECULE>"]
        self.conf.parse_from_block(block)
        self.assertEqual(len(self.conf.molecules), 1)

    def test_parse_wrong(self):
        block = ["NumberOfParticles=2",
                 "<MOLECULE>",
                 "MoleculeRepetitions=2",
                 "O;1;2;3",
                 "H;1;3;3",
                 "H;1;2;4"]
        self.assertRaises(RuntimeError, self.conf.parse_from_block, block)

    def test_parse_empty(self):
        block = ["NumberOfParticles=2", "<MOLECULE>"]
        self.assertRaises(RuntimeError, self.conf.parse_from_block, block)

    def test_parse_content(self):
        block = ["NumberOfParticles=2",
                 "<MOLECULE>",
                 "TEST",
                 "</MOLECULE>"]
        self.conf.parse_from_block(block)
        self.assertEqual(str(self.conf.molecules[0]), "TEST\n")

    def test_determine_num_entities(self):
        block = ["NumberOfParticles=12",
                 "<MOLECULE>",
                 "MoleculeRepetitions=2",
                 "O;1;2;3",
                 "H;1;3;3",
                 "H;1;2;4",
                 "</MOLECULE>",
                 "<MOLECULE>",
                 "MoleculeRepetitions=6",
                 "C;0;0;0",
                 "O;0;1.2;0",
                 "</MOLECULE>",
                 "<MOLECULE>",
                 "MoleculeRepetitions=4",
                 "Na;0;0;2",
                 "</MOLECULE>"]
        self.conf.parse_from_block(block)
        self.assertEqual(12, self.conf.num_entities())

    def test_parse_charge_block(self):
        geo_block = ["NumberOfParticles=2",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "O;1;2;3",
                     "H;1;3;3",
                     "H;1;2;4",
                     "</MOLECULE>",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "C;0;0;0",
                     "O;0;1.2;0",
                     "</MOLECULE>"]
        self.conf.parse_from_block(geo_block)
        charge_block = ["0;1;1.000000",
                        "1;1;-1.000000"]
        self.conf.parse_charge_block(charge_block)
        self.assertEqual("\n<CHARGES>\n    %s\n    %s\n</CHARGES>" % (charge_block[0], charge_block[1]),
                         self.conf.get_finished_charge_block())

    def test_parse_charge_block_empty(self):
        geo_block = ["NumberOfParticles=2",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "O;1;2;3",
                     "H;1;3;3",
                     "H;1;2;4",
                     "</MOLECULE>",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "C;0;0;0",
                     "O;0;1.2;0",
                     "</MOLECULE>"]
        self.conf.parse_from_block(geo_block)
        self.assertEqual("", self.conf.get_finished_charge_block())

    def test_parse_spin_block(self):
        geo_block = ["NumberOfParticles=2",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "O;1;2;3",
                     "H;1;3;3",
                     "H;1;2;4",
                     "</MOLECULE>",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "C;0;0;0",
                     "O;0;1.2;0",
                     "</MOLECULE>"]
        self.conf.parse_from_block(geo_block)
        spin_block = ["0;1;1",
                      "1;1;-1"]
        self.conf.parse_spin_block(spin_block)
        self.assertEqual("\n<SPINS>\n    %s\n    %s\n</SPINS>" % (spin_block[0], spin_block[1]),
                         self.conf.get_finished_spin_block())

    def test_parse_spin_block_empty(self):
        geo_block = ["NumberOfParticles=2",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "O;1;2;3",
                     "H;1;3;3",
                     "H;1;2;4",
                     "</MOLECULE>",
                     "<MOLECULE>",
                     "MoleculeRepetitions=1",
                     "C;0;0;0",
                     "O;0;1.2;0",
                     "</MOLECULE>"]
        self.conf.parse_from_block(geo_block)
        self.assertEqual("", self.conf.get_finished_spin_block())


if __name__ == '__main__':
    unittest.main()
