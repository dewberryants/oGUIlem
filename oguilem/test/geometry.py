import unittest

from oguilem.configuration.geometry import OGUILEMGeometryConfig, OGOLEMMolecule


class GeometryUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = OGUILEMGeometryConfig()
        self.mol = OGOLEMMolecule(["N/A"])

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


if __name__ == '__main__':
    unittest.main()
