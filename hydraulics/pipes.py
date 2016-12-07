import physics

C_POWER = 1.852


class Pipe(object):
    """A cylindrical pipe through which water flows

    It doesn't need any parameters for initializing, instead it's given
    attributes through the following methods
    """
    def __init__(self):
        self.length = None
        self._input_node = None
        self._output_node = None
        self.inner_diam = None
        self.vol_flow = None
        self.c_coefficient = None
        self._name = None

    def is_complete(self):
        """
        Tests completeness of whether or not the pipe has all the information to
        start calculating
        :rtype: bool
        """
        return bool(self.length and
                    self.output_node and
                    self.input_node and
                    self.inner_diam)

    def set_length(self, value, unit):
        """
        Sets the pipe's length in a unit specified by a string
        :param value: the referential value the length is to be set to.
        :type value: float
        :param unit: the length unit. Ex: m
        :type unit: str
        :return:
        """
        if self.length:
            self.length.set_single_value(value, unit)
        else:
            self.length = physics.Length(value, unit)

    def get_length(self, unit):
        # type: (str) -> float
        """
        Getter for the *length* attribute. Must be called
        after :func: `set_length`.
        :param unit:
        :return:
        """
        return self.length.values[unit]

    def set_inner_diam(self, value, unit):
        if self.inner_diam:
            self.inner_diam.set_single_value(value, unit)
        else:
            self.inner_diam = physics.Length(value, unit)

    def get_inner_diam(self, unit):
        return self.inner_diam.values[unit]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name)

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        if self._input_node:
            raise IndexError
        self._input_node = node

    @property
    def output_node(self):
        return self._output_node

    @output_node.setter
    def output_node(self, node):
        self._output_node = node

    def set_c_coefficient(self, value):
        self.c_coefficient = value

    def get_c_coefficient(self):
        return self.c_coefficient

    def hazen_williams_loss(self, unit):
        length_ft = self.get_length('ft')
        flow = self.get_vol_flow('gpm')
        diam_in = self.get_inner_diam('in')
        c_coefficient = self.c_coefficient
        numerator = length_ft * 4.52 * flow * abs(flow) ** (C_POWER - 1)
        delta_press = numerator / (c_coefficient ** C_POWER * diam_in ** 4.87)
        pressure_loss = physics.Pressure(delta_press, 'psi')
        return pressure_loss.values[unit]

    def set_vol_flow(self, value, unit):
        if self.vol_flow:
            self.vol_flow.set_single_value(value, unit)
        else:
            self.vol_flow = physics.VolFlow(value, unit)

    def get_vol_flow(self, unit):
        return self.vol_flow.values[unit]

    def get_gpm_flow(self):
        in_ene = self.input_node.get_energy('psi')
        out_ene = self.output_node.get_energy('psi')
        if in_ene - out_ene == 0:
            q_flow = 0
        else:
            energy_ratio = (in_ene - out_ene) / self.k_flow()
            q_flow = energy_ratio * abs(energy_ratio) ** (1 / C_POWER - 1)
        self.set_vol_flow(q_flow, 'gpm')
        return q_flow

    def k_flow(self):
        pipe_length = self.get_length('ft')
        c = self.get_c_coefficient()
        inner_diam = self.get_inner_diam('in')
        factor = (4.52 * pipe_length) / (c ** C_POWER * inner_diam ** 4.87)
        return factor

    def get_node_jacobian(self, node):
        exponent = 1 / C_POWER - 1
        k_fac = self.k_flow()
        current_energy = node.get_energy('psi')
        result = 0
        if self.output_node == node:
            input_energy = self.input_node.get_energy('psi')
            result -= (1 / (C_POWER * k_fac)) * abs(
                (input_energy - current_energy) / k_fac) ** exponent
        if self.input_node == node:
            output_energy = self.output_node.get_energy('psi')
            result += (1 / (C_POWER * k_fac)) * abs(
                (current_energy - output_energy) / k_fac) ** exponent
        return result
