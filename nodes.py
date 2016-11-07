import physics


class Node(object):
    """The nodes in a pipe network"""

    def __init__(self):
        self._pressure = None
        self.elevation = None
        self.output_pipes = []
        self.input_pipes = []
        self.__energy = None
        self._name = None

    def set_pressure(self, value, unit):
        if self._pressure:
            self._pressure.set_single_value(value, unit)
        else:
            self._pressure = physics.Pressure(value, unit)
        self.__energy = None

    def get_pressure(self, unit):
        return self._pressure.values[unit]

    def set_elevation(self, value, unit):
        if self.elevation:
            self.elevation.set_single_value(value, unit)
        else:
            self.elevation = physics.Length(value, unit)
        self.__energy = None

    def get_elevation(self, unit):
        return self.elevation.values[unit]

    def set_output_pipe(self, pipe):
        self.output_pipes.append(pipe)

    def get_output_pipes(self):
        return self.output_pipes

    def set_input_pipe(self, pipe):
        self.input_pipes.append(pipe)

    def get_input_pipes(self):
        return self.input_pipes

    def get_energy(self, unit):
        if self.__energy:
            return self.__energy.values[unit]
        else:
            elevation_m = self.get_elevation('m')
            press_meters = self.get_pressure('mH2O')
            self.__energy = physics.Pressure(elevation_m + press_meters, 'mH2O')
            return self.__energy.values[unit]

    def set_name(self, name):
        assert isinstance(name, str)
        self._name = name

    def get_name(self):
        return self._name

    def set_energy(self, value, unit):
        if self.__energy:
            self.__energy.set_single_value(value, unit)
        else:
            self.__energy = physics.Pressure(value, unit)
        if self.elevation:
            self.set_pressure(self.get_energy('mH2O') -
                              self.get_elevation('m'), 'mH2O')
