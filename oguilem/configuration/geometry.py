from typing import List, Union


class OGOLEMGeometryConfig:
    def __init__(self):
        self.geoms: List[OGOLEMGeometry] = list()

    def __len__(self):
        return len(self.geoms)

    def __iadd__(self, other):
        if type(other) is OGOLEMGeometry:
            self.geoms.append(other)
        else:
            raise TypeError("Cannot add %s to OGOLEMGeometryConfig!" % str(type(other)))
        return self

    def pop(self, index):
        return self.geoms.pop(index)


class OGOLEMGeometry:
    def __init__(self):
        self.filename: str = ""
        self.particles: int = 0
        self.move_to_com: bool = False

    def parse_from_block(self, block: List[str]):
        mol_blocks: List[List[str]] = list()
        iter_block = iter(block)
        for line in iter_block:
            tmp = line.strip()
            if tmp.startswith("NumberOfParticles"):
                self.particles = int(tmp.split("=")[1])
            elif tmp.startswith("<MOLECULE>"):
                mol_line = next(iter_block, None)
                mol_block: List[str] = list()
                while not mol_line.startswith("</MOLECULE>"):
                    if mol_line is None or mol_line == "":
                        raise RuntimeError("Dangling <MOLECULE> tag!")
                    mol_block.append(mol_line)
                    mol_line = next(iter_block, None)
                mol_blocks.append(mol_block)
        return mol_blocks
