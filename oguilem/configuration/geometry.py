import re
from typing import List

from PyQt5.QtCore import pyqtSignal, QObject


class OGUILEMGeometryConfig(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.particles: int = 0
        self.molecules: List[OGUILEMMolecule] = list()

    def __len__(self):
        return len(self.molecules)

    def __iadd__(self, other):
        if type(other) is OGUILEMMolecule:
            self.molecules.append(other)
        else:
            raise TypeError("Cannot add %s to OGOLEMGeometry!" % str(type(other)))
        self.changed.emit()
        return self

    def __iter__(self):
        return iter(self.molecules)

    def num_entities(self) -> int:
        num = 0
        for mol in self:
            match = re.search(r"(MoleculeRepetitions=)([0-9]+)", "\n".join(mol.content))
            if match:
                num += int(match[2])
            else:
                num += 1
        return num

    def update_mol(self, index, new_content: str):
        self.molecules[index].content = new_content
        self.changed.emit()

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
                self.molecules += [OGUILEMMolecule(["    ".join(line.strip().split(";")) for line in mol_block])]
        self.changed.emit()

    def get_finished_config(self) -> str:
        content = "<GEOMETRY>"
        content += "\n    NumberOfParticles=" + str(self.num_entities())
        for molecule in self.molecules:
            content += "\n    <MOLECULE>"
            for line in molecule.content:
                pattern = r"[A-Za-z]+\s+[0-9]+\.[0-9]+\s"
                if re.match(pattern, line):
                    tmp = re.sub(r"\s+", ";", line)
                else:
                    tmp = line
                content += "\n        " + tmp
            content += "\n    </MOLECULE>"
        content += "\n</GEOMETRY>"
        return content


class OGUILEMMolecule:
    def __init__(self, block: List[str]):
        self.content = block

    def __str__(self):
        ret = ""
        for line in self.content:
            ret += line + "\n"
        return ret
