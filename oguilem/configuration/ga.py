import re

from oguilem.configuration.utils import ConnectedValue


class OGUILEMGlobOptConfig:
    def __init__(self):
        self.mutation: ConnectedValue = ConnectedValue("")
        self.crossover: ConnectedValue = ConnectedValue("")

    def parse_globopt_string(self, string: str):
        match = re.search(r"cluster{(.+?)}", string)
        if not match:
            raise IOError("GlobOpt String did not contain 'cluster{...}' enclosure!")
        crossover = re.search(r"xover\((.+?)\)", match[1])
        mutation = re.search(r"mutation\((.+?)\)", match[1])
        if not mutation:
            raise IOError("GlobOpt String did not contain 'mutation(...)' enclosure!")
        if not crossover:
            raise IOError("GlobOpt String did not contain 'crossover(...)' enclosure!")
        self.mutation.set(mutation[1])
        self.crossover.set(crossover[1])
