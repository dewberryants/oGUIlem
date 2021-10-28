import unittest
from ..configuration.geometry import OGOLEMGeometryConfig, OGOLEMGeometry


class GeometryUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = OGOLEMGeometryConfig()
        self.geom = OGOLEMGeometry()

    def tearDown(self) -> None:
        self.conf = None
        self.geom = None

    def test_alloc_conf(self):
        self.assertIsNotNone(self.conf)

    def test_alloc_geom(self):
        self.assertIsNotNone(self.geom)

    def test_add_geom(self):
        org = len(self.conf)
        self.conf += self.geom
        self.assertIs(len(self.conf), org + 1)

    def test_add_wrong(self):
        self.assertRaises(TypeError, self.conf.__iadd__, "bad")

    def test_pop(self):
        test = OGOLEMGeometryConfig()
        geom = OGOLEMGeometry()
        test += geom
        self.assertIs(test.pop(-1), geom)

    def test_parse(self):
        block = ["NumberOfParticles=2",
                 "<MOLECULE>",
                 "MoleculeRepetitions=2",
                 "O;1;2;3",
                 "H;1;3;3",
                 "H;1;2;4",
                 "</MOLECULE>"]
        parsed = self.geom.parse_from_block(block)
        print(parsed)
        self.assertIs(len(parsed), 1)


if __name__ == '__main__':
    unittest.main()
