class OGOLEMFitnessFunctionConfiguration:
    def __init__(self):
        pass


class DummyConfig:
    def __init__(self, name="N/A", desc="N/A", symb="N/A"):
        self.name = name
        self.desc = desc
        self.symb = symb
        self.properties = dict()

    def __str__(self):
        add = ""
        for key in self.properties:
            if self.properties[key] is not None:
                add += key + str(self.properties[key]) + ","
        return self.symb + add[:-1]


class DummyGenericProperty:
    def __init__(self, t: type, default=None):
        self.type = t
        self.value = default
        self.req = default is None

    def set(self, value):
        assert (type(value) is self.type)
        self.value = value

    def get(self):
        return self.value

    def __str__(self):
        return str(self.value)


test_config = list()
test_config.append(DummyConfig("L-BFGS", "Standard Built-In Local Optimzier", "lbfgs:"))
test_config[0].properties = {
    "backend=": '<font color="red">&lt;GENERIC BACKEND&gt;</font>',
    "maxiter=": DummyGenericProperty(int, 100)
}
