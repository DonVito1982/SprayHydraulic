import physics


class Node(object):
    """The nodes in a pipe network"""

    def __init__(self):
        self._pressure = None
        self.elevation = None
        self.output_pipes = []
        self.input_pipes = []

    def set_pressure(self, value, unit):
        if self._pressure:
            self._pressure.set_single_value(value, unit)
        else:
            self._pressure = physics.Pressure(value, unit)

    def get_pressure(self, unit):
        return self._pressure.values[unit]

    def set_elevation(self, value, unit):
        if self.elevation:
            self.elevation.set_single_value(value, unit)
        else:
            self.elevation = physics.Length(value, unit)

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
