import physics


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
        # type: () -> Node
        return self.output_node

    def set_c_coefficient(self, value):
        self.c_coefficient = value

    def get_c_coefficient(self):
        return self.c_coefficient

    def hazen_williams_loss(self):
        length_ft = self.get_length('ft')
        flow_gpm = self.get_vol_flow('gpm')
        diam_in = self.get_inner_diam('in')
        c_coefficient = self.c_coefficient
        delta_press = (length_ft * 4.52 * flow_gpm * abs(flow_gpm) ** 0.85) / \
                      (c_coefficient ** 1.85 * diam_in ** 4.87)
        return delta_press

    def set_vol_flow(self, value, unit):
        if self.vol_flow:
            self.vol_flow.set_single_value(value, unit)
        else:
            self.vol_flow = physics.VolFlow(value, unit)

    def get_vol_flow(self, unit):
        return self.vol_flow.values[unit]
