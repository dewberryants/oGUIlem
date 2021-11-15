from typing import List

from PyQt5.QtCore import pyqtSignal, QObject


class OGUILEMGeometryConfig(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.particles: int = 0
        self.molecules: List[OGOLEMMolecule] = list()

    def __len__(self):
        return len(self.molecules)

    def __iadd__(self, other):
        if type(other) is OGOLEMMolecule:
            self.molecules.append(other)
        else:
            raise TypeError("Cannot add %s to OGOLEMGeometry!" % str(type(other)))
        self.changed.emit()
        return self

    def __iter__(self):
        return iter(self.molecules)

    def pop(self, index):
        popped = self.molecules.pop(index)
        self.changed.emit()
        return popped

    def parse_from_block(self, block: List[str]):
        self.molecules = list()
        iter_block = iter(block)
        for line in iter_block:
            tmp = line.strip()
            if tmp.startswith("NumberOfParticles"):
                self.particles = int(tmp.split("=")[1])
            elif tmp.startswith("<MOLECULE>"):
                try:
                    mol_line = next(iter_block)
                except StopIteration:
                    raise RuntimeError("Molecule config ends after <MOLECULE> tag!?")
                mol_block: List[str] = list()
                while not mol_line.startswith("</MOLECULE>"):
                    mol_block.append(mol_line)
                    try:
                        mol_line = next(iter_block)
                    except StopIteration:
                        raise RuntimeError("Dangling <MOLECULE> tag in configuration!")
                # Pre-parse the semicolons to spaces
                self.molecules += [OGOLEMMolecule(["    ".join(line.strip().split(";")) for line in mol_block])]
        self.changed.emit()


class OGOLEMMolecule:
    def __init__(self, block: List[str]):
        self.content = block

    def __str__(self):
        ret = ""
        for line in self.content:
            ret += line + "\n"
        return ret
