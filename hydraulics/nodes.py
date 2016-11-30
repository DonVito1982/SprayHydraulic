from hydraulics import physics


class Node(object):
    def __init__(self):
        self._in_pressure = None
        self.elevation = None
        self.output_pipes = []
        self.input_pipes = []
        self._name = None
        self.in_energy = None

    def set_elevation(self, value, unit):
        if self.elevation:
            self.elevation.set_single_value(value, unit)
        else:
            self.elevation = physics.Length(value, unit)
        self.in_energy = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        name = str(name)
        self._name = name


class ConnectionNode(Node):
    """The nodes in a pipe network"""
    def set_in_pressure(self, value, unit):
        if self._in_pressure:
            self._in_pressure.set_single_value(value, unit)
        else:
            self._in_pressure = physics.Pressure(value, unit)
        self.in_energy = None

    def get_in_pressure(self, unit):
        return self._in_pressure.values[unit]

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

    def get_in_energy(self, unit):
        if self.in_energy:
            return self.in_energy.values[unit]
        else:
            elevation_m = self.get_elevation('m')
            press_meters = self.get_in_pressure('mH2O')
            self.in_energy = physics.Pressure(elevation_m + press_meters, 'mH2O')
            return self.in_energy.values[unit]

    def set_energy(self, value, unit):
        if self.in_energy:
            self.in_energy.set_single_value(value, unit)
        else:
            self.in_energy = physics.Pressure(value, unit)
        if self.elevation:
            self.set_in_pressure(self.get_in_energy('mH2O') -
                                 self.get_elevation('m'), 'mH2O')
