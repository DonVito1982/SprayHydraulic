import physics


class Pipe(object):
    def __init__(self):
        self.length = None
        self.input_node = None
        self.output_node = None
        self.inner_diam = None
        self.vol_flow = None

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

    def set_input(self, node):
        self.input_node = node

    def get_input(self):
        return self.input_node

    def set_output(self, node):
        self.output_node = node

    def get_output(self):
        return self.output_node

    def haz_will_loss(self):
        length_ft = self.get_length('ft')
        flow_gpm = self.get_vol_flow('gpm')
        diam_in = self.get_inner_diam('in')
        delta_press = (length_ft * 4.52 * flow_gpm * abs(flow_gpm) ** 0.85) / \
                      (100 ** 1.85 * diam_in ** 4.87)
        return delta_press

    def set_vol_flow(self, value, unit):
        if self.vol_flow:
            self.vol_flow.set_single_value(value, unit)
        else:
            self.vol_flow = physics.VolFlow(value, unit)

    def get_vol_flow(self, unit):
        return self.vol_flow.values[unit]
