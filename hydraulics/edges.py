from abc import abstractmethod, ABCMeta
from math import sqrt
import physics
from nodes import Node, EndNode


class Edge(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._vol_flow = None
        self._name = None
        self._input_node = None
        self._output_node = None

    def clear_input(self):
        self._input_node = None

    def clear_output(self):
        self._output_node = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name)

    def set_vol_flow(self, value, unit):
        if self._vol_flow:
            self._vol_flow.set_single_value(value, unit)
        else:
            self._vol_flow = physics.VolFlow(value, unit)

    def get_vol_flow(self, unit):
        return self._vol_flow.values[unit]

    @abstractmethod
    def calculate_gpm_flow(self):
        pass

    @abstractmethod
    def is_complete(self):
        """
        Tests completeness of whether or not the edge has all the information
        to start calculating
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_node_jacobian(self, node):
        pass

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        if self._input_node:
            raise IndexError
        if not isinstance(node, Node):
            raise ValueError
        self._input_node = node

    def connects(self):
        return bool(self._input_node and self._output_node)


class Nozzle(Edge):
    def __init__(self):
        super(Nozzle, self).__init__()
        self.k_factor = None
        self._required_pressure = None

    def set_factor(self, value, unit):
        if self.k_factor is not None:
            self.k_factor.set_single_value(value, unit)
        else:
            self.k_factor = physics.NozzleK(value, unit)

    def get_factor(self, unit):
        return self.k_factor.values[unit]

    def set_required_pressure(self, value, unit):
        if self._required_pressure is not None:
            self._required_pressure.set_single_value(value, unit)
        else:
            self._required_pressure = physics.Pressure(value, unit)

    def get_required_pressure(self, unit):
        return self._required_pressure.values[unit]

    def calculate_gpm_flow(self):
        in_ene = self.input_node.get_energy('psi')
        out_ene = self.output_node.get_energy('psi')
        if in_ene - out_ene == 0:
            q_flow = 0
        else:
            energy_diff = (in_ene - out_ene)
            k_fac = self.get_factor('gpm/psi^0.5')
            q_flow = energy_diff * k_fac / sqrt(abs(energy_diff))
        self.set_vol_flow(q_flow, 'gpm')
        return q_flow

    def get_node_jacobian(self, node):
        result = 0
        if self.input_node == node:
            k_factor = self.get_factor('gpm/psi^0.5')
            diff = node.get_energy('psi') - self.output_node.get_energy('psi')
            # result += (k_factor * 0.5) / sqrt(abs(k_factor * diff))
            result += (k_factor * 0.5) / sqrt(abs(diff))
        return result

    def is_complete(self):
        return bool(self.k_factor and self.input_node and self.output_node and
                    self._required_pressure)

    @property
    def output_node(self):
        return self._output_node

    @output_node.setter
    def output_node(self, node):
        if self._output_node is None and isinstance(node, EndNode):
            self._output_node = node
        else:
            raise ValueError


class Pipe(Edge):
    C_POWER = 1 / 0.54

    def __init__(self):
        super(Pipe, self).__init__()
        self.length = None
        self.inner_diam = None
        self.c_coefficient = None
        self.k_pipe = None

    def is_complete(self):
        """
        Tests completeness of whether or not the pipe has all the information to
        start calculating
        :rtype: bool
        """
        return bool(self.length and
                    self._output_node and
                    self._input_node and
                    self.inner_diam and
                    self.c_coefficient)

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
        self.k_pipe = None

    def get_length(self, unit):
        """
        Getter for the *length* attribute. Must be called
        after :func: `set_length`.
        :param unit: the pipe length's unit
        :type unit: str
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

    def set_c_coefficient(self, value):
        self.c_coefficient = value

    def get_c_coefficient(self):
        return self.c_coefficient

    def get_hazen_williams_loss(self, unit):
        length_ft = self.get_length('ft')
        flow = self.get_vol_flow('gpm')
        diam_in = self.get_inner_diam('in')
        c_coefficient = self.c_coefficient
        num = length_ft * 4.52 * flow * abs(flow) ** (Pipe.C_POWER - 1)
        delta_press = num / (c_coefficient ** Pipe.C_POWER * diam_in ** 4.87)
        pressure_loss = physics.Pressure(delta_press, 'psi')
        return pressure_loss.values[unit]

    def calculate_gpm_flow(self):
        in_ene = self.input_node.get_energy('psi')
        out_ene = self.output_node.get_energy('psi')
        if in_ene - out_ene == 0:
            q_flow = 0
        else:
            energy_ratio = (in_ene - out_ene) / self.k_flow()
            q_flow = energy_ratio * abs(energy_ratio) ** (1 / Pipe.C_POWER - 1)
        self.set_vol_flow(q_flow, 'gpm')
        return q_flow

    def _set_k_pipe(self):
        pipe_length = self.get_length('ft')
        c = self.get_c_coefficient()
        diam = self.get_inner_diam('in')
        self.k_pipe = (4.52 * pipe_length) / (c ** Pipe.C_POWER * diam ** 4.87)

    def k_flow(self):
        if not self.k_pipe:
            self._set_k_pipe()
        return self.k_pipe

    def get_node_jacobian(self, node):
        exponent = 1 / Pipe.C_POWER - 1
        k_fac = self.k_flow()
        current_energy = node.get_energy('psi')
        result = 0
        if self.output_node == node:
            input_energy = self.input_node.get_energy('psi')
            result -= (1 / (Pipe.C_POWER * k_fac)) * abs(
                (input_energy - current_energy) / k_fac) ** exponent
        if self.input_node == node:
            output_energy = self.output_node.get_energy('psi')
            result += (1 / (Pipe.C_POWER * k_fac)) * abs(
                (current_energy - output_energy) / k_fac) ** exponent
        return result

    @property
    def output_node(self):
        return self._output_node

    @output_node.setter
    def output_node(self, node):
        if self._output_node:
            raise IndexError
        if not isinstance(node, Node):
            raise ValueError('Must be node')
        self._output_node = node


class ANSIPipe(Pipe):
    schedules = ('Std', '80')
    in_diams = {1: (1.049, 0.957),
                2: (2.067, 1.939),
                3: (3.068, 2.9)}
    mm_diams = {25: (26.64, 24.3),
                50: (52.48, 49.22),
                80: (77.92, 73.66)}

    def __init__(self):
        super(ANSIPipe, self).__init__()
        self._nominal_diameter = None
        self.c_coefficient = 100
        self._schedule = None
        self._unit = None

    @property
    def nominal_diameter(self):
        return self._nominal_diameter

    @nominal_diameter.setter
    def nominal_diameter(self, diameter):
        self._nominal_diameter = diameter
        if self._schedule and self._unit:
            self._set_diam()

    @property
    def diam_unit(self):
        return self._unit

    @diam_unit.setter
    def diam_unit(self, unit):
        self._unit = unit
        if self._schedule and self._nominal_diameter:
            self._set_diam()

    @property
    def schedule(self):
        return self._schedule

    @schedule.setter
    def schedule(self, schedule):
        self._schedule = str(schedule)
        if self._nominal_diameter and self._unit:
            self._set_diam()

    def _set_diam(self):
        sch_index = self.schedules.index(self.schedule)
        nom_diam = self.nominal_diameter
        if self._unit == 'in':
            unit_diams = self.in_diams
        elif self._unit == 'mm':
            unit_diams = self.mm_diams
        self.set_inner_diam(unit_diams[nom_diam][sch_index], self._unit)
