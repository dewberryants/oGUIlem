import unittest

from oguilem.configuration.ga import OGUILEMGlobOptConfig


class GeometryUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = OGUILEMGlobOptConfig()

    def tearDown(self) -> None:
        self.conf = None

    def test_alloc(self):
        self.assertIsNotNone(self.conf)

    def test_parse(self):
        string = "cluster{xover(sweden:)mutation(montecarlo:)}"
        self.conf.parse_globopt_string(string)
        self.assertEqual("montecarlo:", self.conf.mutation.value)
        self.assertEqual("sweden:", self.conf.crossover.value)

    def test_parse_empty(self):
        string = ""
        self.assertRaises(IOError, self.conf.parse_globopt_string, string)

    def test_parse_wrong(self):
        string = "cluster{xover(sweden:mutation(montecarlo:)"
        self.assertRaises(IOError, self.conf.parse_globopt_string, string)


if __name__ == '__main__':
    unittest.main()
