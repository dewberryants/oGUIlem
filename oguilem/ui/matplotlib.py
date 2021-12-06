import matplotlib as mpl
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Line3DCollection

mpl.use('Qt5Agg')


class XYZFile:
    def __init__(self, file_name="", bond_list="", auto_bonds=True):
        self.symbols: np.ndarray = np.zeros(0, dtype="str")
        self.coordinates: np.ndarray = np.zeros(0)
        self.bonds: np.ndarray = np.zeros(0, dtype="bool")
        if file_name:
            self.load_from_file(file_name, bond_list, auto_bonds)

    def load_from_file(self, file_name: str, bonds: str, auto_bonds=True):
        with open(file_name) as xyz:
            try:
                atms = int(xyz.readline().strip())
            except ValueError:
                print("Faulty XYZ format.")
                return
            self.symbols = np.zeros(atms, dtype="str")
            self.coordinates = np.zeros((3, atms), dtype="float32")
            self.bonds = np.zeros((atms, atms), dtype="bool")
            xyz.readline()
            for n in range(atms):
                line = xyz.readline().strip().split()
                self.symbols[n] = line[0]
                self.coordinates[0][n] = float(line[1])
                self.coordinates[1][n] = float(line[2])
                self.coordinates[2][n] = float(line[3])
        if not bonds and auto_bonds:
            rsq = map_symbols_to_radii(self.symbols)
            rsq = rsq[..., np.newaxis] + rsq
            dx = self.coordinates[0][..., np.newaxis] - self.coordinates[0]
            dy = self.coordinates[1][..., np.newaxis] - self.coordinates[1]
            dz = self.coordinates[2][..., np.newaxis] - self.coordinates[2]
            dsq = dx * dx + dy * dy + dz * dz + 0.41
            self.bonds = (dsq < rsq) + (dsq < 0.4)


def map_symbols_to_radii(symbols: np.ndarray):
    radii = np.zeros(symbols.shape[0], dtype='float32')
    for n in range(symbols.shape[0]):
        radii[n] = 1.5
    return radii


class MoleculeVisualizer(FigureCanvasQTAgg):
    def __init__(self, size):
        fig = Figure(figsize=(size, size), tight_layout={'pad': 0})
        self.axes = fig.add_subplot(111, projection='3d')
        self.axes.axis(False)
        self.axes.set_box_aspect([ub - lb for lb, ub in (getattr(self.axes, f'get_{a}lim')() for a in 'xyz')])
        super().__init__(fig)

    def load(self, xyz: XYZFile):
        x, y, z = xyz.coordinates
        segments = list()
        for i in range(xyz.bonds.shape[0]):
            for j in range(i + 1, xyz.bonds.shape[1]):
                if xyz.bonds[i][j]:
                    segment = ((x[i], y[i], z[i]), (x[j], y[j], z[j]))
                    segments.append(segment)
        bonds = Line3DCollection(segments, color="gray")
        print(bonds)
        self.axes.add_collection3d(bonds)
        self.axes.scatter(x, y, z, color="black")
