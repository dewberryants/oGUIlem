from typing import List


class OGOLEMGeometryConfig:
    def __init__(self):
        self.particles: int = 0
        self.molecules: List[OGOLEMMolecule] = list()

    def __len__(self):
        return len(self.molecules)

    def __iadd__(self, other):
        if type(other) is OGOLEMMolecule:
            self.molecules.append(other)
        else:
            raise TypeError("Cannot add %s to OGOLEMGeometry!" % str(type(other)))
        return self

    def pop(self, index):
        return self.molecules.pop(index)

    def parse_from_block(self, block: List[str]):
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
                self.molecules += [OGOLEMMolecule([line.strip() for line in mol_block])]


class OGOLEMMolecule:
    def __init__(self, block: List[str]):
        self.content = block

    def __str__(self):
        ret = ""
        for line in self.content:
            ret += line + "\n"
        return ret
