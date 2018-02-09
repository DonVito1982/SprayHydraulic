import physics

from edges import Edge
from nodes import EductorInlet, EductorOutlet
from math import sqrt


class Eductor(Edge):
    def __init__(self):
        super(Eductor, self).__init__()
        self._k_factor = None
        self._concentration = None

    def calculate_gpm_flow(self):

        input_energy = self.input_node.get_energy('psi')
        output_energy = self.output_node.get_energy('psi')
        aug_dif = (input_energy - output_energy) / 0.35
        k_fac = self.get_factor('gpm/psi^0.5')
        q_flow1 = k_fac * aug_dif / sqrt(abs(aug_dif))

        pressure = self.input_node.get_pressure('psi')
        k_fac = self.get_factor('gpm/psi^0.5')
        q_flow2 = pressure * k_fac / sqrt(abs(pressure))
        fac = 0
        q_flow = (1 - fac) * q_flow1 + fac * q_flow2

        self.set_vol_flow(q_flow, 'gpm')
        return q_flow

    def adjust_pressure(self):
        pressure = self.input_node.get_pressure('psi')
        self.output_node.set_pressure(pressure*0.65, 'psi')

    def get_node_jacobian(self, node):
        result = 0
        fac = 0.5
        if self.input_node == node:
            k_factor = self.get_factor('gpm/psi^0.5') * 0.5
            result1 = k_factor / sqrt(abs(node.get_pressure('psi')))
            k_factor = self.get_factor('gpm/psi^0.5') * 0.5 / sqrt(0.35)
            diff = node.get_energy('psi') - self.output_node.get_energy('psi')
            result2 = k_factor / sqrt(abs(diff))
            result += fac * result1 + (1 - fac) * result2
        if self.output_node == node:
            k_factor = self.get_factor('gpm/psi^0.5') * 0.5 / sqrt(0.35)
            diff = self.input_node.get_energy('psi') - node.get_energy('psi')
            result -= (1 - fac) * k_factor / sqrt(abs(diff))
        return result

    def is_complete(self):
        completeness = True
        completeness = completeness and self._k_factor
        completeness = completeness and self._input_node
        completeness = completeness and self._output_node
        completeness = completeness and self._concentration
        return completeness

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        if self._input_node:
            raise IndexError("Already have input node")
        if not isinstance(node, EductorInlet):
            raise TypeError
        self._input_node = node

    @property
    def output_node(self):
        return self._output_node

    @output_node.setter
    def output_node(self, node):
        if self._output_node:
            raise IndexError
        if not isinstance(node, EductorOutlet):
            raise TypeError
        self._output_node = node

    def set_factor(self, value, unit):
        if self._k_factor is not None:
            self._k_factor.set_single_value(value, unit)
        else:
            self._k_factor = physics.NozzleK(value, unit)

    def get_factor(self, unit):
        return self._k_factor.values[unit]

    @property
    def concentration(self):
        return self._concentration

    @concentration.setter
    def concentration(self, value):
        if not isinstance(value, float):
            raise TypeError
        if value >= 1:
            raise ValueError
        self._concentration = value

    def set_vol_flow(self, value, unit):
        super(Eductor, self).set_vol_flow(value, unit)
        self.output_node.set_output_flow(-value*self.concentration, unit)

    def is_eductor(self):
        ed = self._k_factor
        return ed
