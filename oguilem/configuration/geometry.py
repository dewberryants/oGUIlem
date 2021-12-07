import os
import re
from typing import List, Dict

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

    def update_mol(self, index, new_content: list, charges: dict, spins: dict):
        assert (type(new_content) == list)
        while "" in new_content:
            new_content.pop(new_content.index(""))
        self.molecules[index].content = new_content
        self.molecules[index].charges = charges
        self.molecules[index].spins = spins
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

    def parse_charge_block(self, charge_block: List[str]):
        for line in charge_block:
            tmp = line.strip()
            try:
                work = tmp.split(";")
                index = int(work[0])
                self.molecules[index].charges[work[1]] = float(work[2])
            except IndexError:
                raise RuntimeError("Unknown Atom Index in Charge Block!")
            except ValueError:
                raise RuntimeError("Failed parsing a value in the Charge Block!")

    def parse_spin_block(self, spin_block: List[str]):
        for line in spin_block:
            tmp = line.strip()
            try:
                work = tmp.split(";")
                index = int(work[0])
                self.molecules[index].spins[work[1]] = int(work[2])
            except IndexError:
                raise RuntimeError("Unknown Atom Index in Spin Block!")
            except ValueError:
                raise RuntimeError("Failed parsing a value in the Spin Block!")

    def get_finished_charge_block(self):
        content = ""
        for n, mol in enumerate(self.molecules):
            for index in mol.charges:
                content += "\n    %d;%s;%f" % (n, index, mol.charges[index])
        if content:
            content = "\n<CHARGES>" + content + "\n</CHARGES>"
        return content

    def get_finished_spin_block(self):
        content = ""
        for n, mol in enumerate(self.molecules):
            for index in mol.spins:
                content += "\n    %d;%s;%d" % (n, index, mol.spins[index])
        if content:
            content = "\n<SPINS>" + content + "\n</SPINS>"
        return content

    def get_finished_config(self, path="") -> str:
        content = "<GEOMETRY>"
        content += "\n    NumberOfParticles=" + str(self.num_entities())
        for molecule in self.molecules:
            content += "\n    <MOLECULE>"
            for line in molecule.content:
                pattern = r"[A-Za-z]+\s+[0-9]+\.?[0-9]?\s"
                if re.match(pattern, line):
                    tmp = re.sub(r"\s+", ";", line.strip())
                elif re.match("MoleculePath=", line.strip()) and os.path.exists(path):
                    tmp = line.strip().split("=")
                    current_dir = os.path.dirname(path)
                    cwd = os.getcwd()
                    os.chdir(current_dir)
                    target_dir = os.path.abspath(tmp[1])
                    tmp = "=".join([tmp[0], os.path.relpath(target_dir, current_dir)])
                    os.chdir(cwd)
                else:
                    tmp = line.strip()
                content += "\n        " + tmp
            content += "\n    </MOLECULE>"
        content += "\n</GEOMETRY>"
        content += self.get_finished_charge_block()
        content += self.get_finished_spin_block()
        return content


class OGUILEMMolecule:
    def __init__(self, block: List[str]):
        self.content: List[str] = block
        self.charges: Dict = dict()
        self.spins: Dict = dict()

    def __str__(self):
        ret = ""
        for line in self.content:
            ret += line + "\n"
        return ret
