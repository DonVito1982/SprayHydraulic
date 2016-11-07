import physics


C_POWER = 1.852


class Pipe(object):
    def __init__(self):
        self.length = None
        self._input_node = None
        self.output_node = None
        self.inner_diam = None
        self.vol_flow = None
        self.c_coefficient = None

    def set_length(self, value, unit):
        if self.length:
            self.length.set_single_value(value, unit)
        else:
            self.length = physics.Length(value, unit)

    def get_length(self, unit):
        return self.length.values[unit]

    def set_inner_diam(self, value, unit):
        if self.inner_diam:
            self.inner_diam.set_single_value(value, unit)
        else:
            self.inner_diam = physics.Length(value, unit)

    def get_inner_diam(self, unit):
        return self.inner_diam.values[unit]

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        self._input_node = node

    def set_output(self, node):
        self.output_node = node

    def get_output(self):
        return self.output_node

    def set_c_coefficient(self, value):
        self.c_coefficient = value

    def get_c_coefficient(self):
        return self.c_coefficient

    def hazen_williams_loss(self, unit):
        length_ft = self.get_length('ft')
        flow = self.get_vol_flow('gpm')
        diam_in = self.get_inner_diam('in')
        c_coefficient = self.c_coefficient
        delta_press = (length_ft * 4.52 * flow * abs(flow) ** (C_POWER-1)) / \
                      (c_coefficient ** C_POWER * diam_in ** 4.87)
        pressure_loss = physics.Pressure(delta_press, 'psi')
        return pressure_loss.values[unit]

    def set_vol_flow(self, value, unit):
        if self.vol_flow:
            self.vol_flow.set_single_value(value, unit)
        else:
            self.vol_flow = physics.VolFlow(value, unit)

    def get_vol_flow(self, unit):
        return self.vol_flow.values[unit]
