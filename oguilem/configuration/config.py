import os
import re
import sys

from oguilem.configuration.fitness import OGUILEMFitnessFunctionConfiguration
from oguilem.configuration.ga import OGUILEMGlobOptConfig
from oguilem.configuration.geometry import OGUILEMGeometryConfig
from oguilem.configuration.utils import ConnectedValue, ConfigFileManager
from oguilem.resources import options


class OGUILEMConfig:
    def __init__(self):
        self.ui = OGUILEMUIConfig()
        self.globopt = OGUILEMGlobOptConfig()
        self.options = OGUILEMGeneralConfig()
        self.geometry = OGUILEMGeometryConfig()
        self.fitness = OGUILEMFitnessFunctionConfiguration()
        self.file_manager = ConfigFileManager()

    def save_to_file(self, path: str):
        content = "###OGOLEM###\n"
        content += self.globopt.get_finished_config()
        content += self.geometry.get_finished_config()
        content += self.fitness.get_finished_config()
        content += self.options.get_finished_config()
        with open(path, "w") as conf_file:
            conf_file.write(content)
        self.file_manager.signal_saved(path)

    def load_from_file(self, path: str, preset=False):
        self.options.set_to_default()
        with open(path, "r") as conf_file:
            content = conf_file.readlines()
            # Find geometry block and split off
            iter_content = iter(content)
            geo_block = list()
            backend_defs = list()
            charge_block = list()
            spin_block = list()

            # Separate off blocks
            start, end = -1, -1
            for n, line in enumerate(iter_content):
                # Charge and Spin Blocks
                if line.strip().startswith("<CHARGES>"):
                    start = n
                    try:
                        charge_line = next(iter_content).strip()
                    except StopIteration:
                        raise RuntimeError("Config ends after <CHARGES> tag!?")
                    while not charge_line.startswith("</CHARGES>"):
                        charge_block.append(charge_line)
                        try:
                            charge_line = next(iter_content).strip()
                        except StopIteration:
                            raise RuntimeError("Dangling <GEOMETRY> tag in configuration!")
                    end = start + len(charge_block) + 2
                    content = content[:start] + content[end:]
                if line.strip().startswith("<SPINS>"):
                    start = n
                    try:
                        spin_line = next(iter_content).strip()
                    except StopIteration:
                        raise RuntimeError("Config ends after <SPINS> tag!?")
                    while not spin_line.startswith("</SPINS>"):
                        spin_block.append(spin_line)
                        try:
                            spin_line = next(iter_content).strip()
                        except StopIteration:
                            raise RuntimeError("Dangling <SPINS> tag in configuration!")
                    end = start + len(spin_block) + 2
                    content = content[:start] + content[end:]

                # Geometry Block
                if line.strip().startswith("<GEOMETRY>"):
                    start = n
                    try:
                        geo_line = next(iter_content).strip()
                    except StopIteration:
                        raise RuntimeError("Config ends after <GEOMETRY> tag!?")
                    while not geo_line.startswith("</GEOMETRY>"):
                        geo_block.append(geo_line)
                        try:
                            geo_line = next(iter_content).strip()
                        except StopIteration:
                            raise RuntimeError("Dangling <GEOMETRY> tag in configuration!")
                    end = start + len(geo_block) + 2
                    content = content[:start] + content[end:]

                # Any Backend Definitions
                if line.strip().startswith("<CLUSTERBACKEND>"):
                    back_block = list()
                    start = n
                    try:
                        back_line = next(iter_content).strip()
                    except StopIteration:
                        raise RuntimeError("Config ends after <CLUSTERBACKEND> tag!?")
                    while not back_line.startswith("</CLUSTERBACKEND>"):
                        back_block.append(back_line)
                        try:
                            back_line = next(iter_content).strip()
                        except StopIteration:
                            raise RuntimeError("Dangling <CLUSTERBACKEND> tag in configuration!")
                    end = start + len(back_block) + 2
                    backend_defs.append(back_block)
                    content = content[:start] + content[end:]

            # Parse them
            self.geometry.parse_from_block(geo_block)
            self.geometry.parse_charge_block(charge_block)
            self.geometry.parse_spin_block(spin_block)
            self.fitness.parse_backend_tags(backend_defs)

            # Deal with the rest
            for line in content:
                if line.strip().startswith("LocOptAlgo="):
                    self.fitness.parse_locopt_algo(line.strip()[11:])
                elif line.strip().startswith("GlobOptAlgo="):
                    self.globopt.parse_globopt_string(line.strip()[12:])
                else:
                    for key in self.options.values:
                        type = self.options.values[key].type
                        if re.match(key + "=", line.strip()):
                            value, index = parse_value(line.strip()[len(key) + 1:], type)
                            if value is not None:
                                print("Option {:>30} set to: {:>30}".format(key, str(value)))
                                self.options.values[key].set(value, index)
                            else:
                                print("ERROR: Could not set Option %s. Set to default instead!" % key)
                                self.options.values[key].set(self.options.defaults[key])
        if not preset:
            self.file_manager.signal_saved(path)
        else:
            self.file_manager.signal_modification()


def parse_value(line, type):
    value = None
    index = -1
    work = line.strip()
    if type is str:
        value = work
    elif type is int:
        value = int(work)
    elif type is float:
        value = float(work)
    elif type is bool:
        value = work.lower() == "true"
    elif type is list:
        tmp = work.split(";")
        value = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
    return value, index


class OGUILEMGeneralConfig:
    def __init__(self):
        self.defaults = dict()
        self.values = dict()
        for key in options:
            type, default = options[key]
            if type == "str":
                self.defaults[key] = default
            elif type == "int":
                self.defaults[key] = int(default)
            elif type == "float":
                self.defaults[key] = float(default)
            elif type == "bool":
                self.defaults[key] = (default.lower() == "true")
            elif type == "3;float":
                default = default.strip().split(";")
                self.defaults[key] = [float(default[0]), float(default[1]), float(default[2])]
            else:
                raise IOError("Could not parse xml key %s in general configs!" % key)
            self.values[key] = ConnectedValue(self.defaults[key])

    def set_to_default(self):
        for key in options:
            self.values[key].set(self.defaults[key])

    def get_finished_config(self) -> str:
        content = ""
        for key in self.values:
            self.values[key].request_update()
            value = self.values[key].value
            if value != self.defaults[key]:
                content += "\n" + key + "=" + str(self.values[key])
        return content


def find_config_folder():
    if sys.platform == 'Windows':
        path = os.path.join(os.environ['APPDATA'], 'oguilem')
    else:
        path = os.path.join(os.environ['HOME'], '.config', 'oguilem')
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


class OGUILEMUIConfig:
    def __init__(self):
        self.window_size = None
        self.window_position = None
        self.java_path = None
        self.java_vm_variables = None
        self.ogo_path = None
        self.ogo_args = None
        self.environmental_variables = None
        try:
            self.recover_from_file()
        except ValueError:
            print("There are format errors in the UI config file in '%s'. Using defaults." % find_config_folder())
        except IOError:
            print("Config file not found. A new one will generate once the program exits.")

    def get_run_command(self):
        if not all([self.java_path, self.ogo_path, self.ogo_args]):
            raise RuntimeError("Cannot run ogolem without knowing java and ogolem paths as well as ogolem arguments!")
        if self.java_vm_variables:
            return self.java_path + self.java_vm_variables + " -jar " + self.ogo_path + self.ogo_args
        return self.java_path + " -jar " + self.ogo_path + self.ogo_args

    def recover_from_file(self):
        path = os.path.join(find_config_folder(), "oguilem.cfg")
        with open(path, "r") as config:
            lines = config.readlines()
        for line in lines:
            work = line.strip()
            if work.startswith("WINDOWSIZE"):
                self.window_size = (int(work.split()[1]), int(work.split()[2]))
            elif work.startswith("WINDOWPOS"):
                self.window_position = (int(work.split()[1]), int(work.split()[2]))
            elif work.startswith("JAVAPATH"):
                self.java_path = work[8:].strip()
            elif work.startswith("JAVAVM"):
                self.java_vm_variables = work[7:].strip()
            elif work.startswith("OGOPATH"):
                self.ogo_path = work[7:].strip()
            elif work.startswith("OGOARGS"):
                self.ogo_args = work[7:].strip()
            elif work.startswith("ENV"):
                self.environmental_variables = work[3:].strip()

    def save_to_file(self):
        path = os.path.join(find_config_folder(), "oguilem.cfg")
        with open(path, "w") as config:
            if self.window_size:
                config.write("WINDOWSIZE %d %d\n" % (self.window_size[0], self.window_size[1]))
            if self.window_position:
                config.write("WINDOWPOS %d %d\n" % (self.window_position[0], self.window_position[1]))
            if self.java_path:
                config.write("JAVAPATH %s\n" % self.java_path)
            if self.java_vm_variables:
                config.write("JAVAVM %s\n" % self.java_vm_variables)
            if self.ogo_path:
                config.write("OGOPATH %s\n" % self.ogo_path)
            if self.ogo_args:
                config.write("OGOARGS %s\n" % self.ogo_args)
            if self.java_path:
                config.write("ENV %s\n" % self.environmental_variables)
