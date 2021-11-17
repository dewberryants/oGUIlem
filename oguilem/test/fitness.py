import unittest

from oguilem.configuration.fitness import OGUILEMFitnessFunctionConfiguration


class GeometryUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = OGUILEMFitnessFunctionConfiguration()

    def tearDown(self) -> None:
        self.conf = None


if __name__ == '__main__':
    unittest.main()
