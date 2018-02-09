from abc import abstractmethod, ABCMeta

from hydraulics import physics
# from hydraulics.eductor import Eductor


class Node(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._pressure = None
        self.elevation = None
        self.output_pipes = []
        self.input_pipes = []
        self._name = None
        self.energy = None
        self._out_flow = physics.VolFlow(0, 'gpm')

    def set_elevation(self, value, unit):
        if self.elevation:
            self.elevation.set_single_value(value, unit)
        else:
            self.elevation = physics.Length(value, unit)
        self.energy = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        name = str(name)
        self._name = name

    def get_elevation(self, unit):
        return self.elevation.values[unit]

    @abstractmethod
    def get_pressure(self, unit):
        pass

    def get_energy(self, unit):
        if self.energy:
            return self.energy.values[unit]
        else:
            elevation_m = self.get_elevation('m')
            press_meters = self.get_pressure('mH2O')
            self.energy = physics.Pressure(elevation_m + press_meters, 'mH2O')
            return self.energy.values[unit]

    def set_output_pipe(self, pipe):
        self.output_pipes.append(pipe)

    def get_output_pipes(self):
        return self.output_pipes

    def set_input_pipe(self, pipe):
        self.input_pipes.append(pipe)

    def get_input_pipes(self):
        return self.input_pipes

    def get_output_flow(self, unit):
        return self._out_flow.values[unit]

    def set_output_flow(self, value, unit):
        self._out_flow.set_single_value(value, unit)


class ConnectionNode(Node):
    """The nodes in a pipe network"""
    def set_pressure(self, value, unit):
        if self._pressure:
            self._pressure.set_single_value(value, unit)
        else:
            self._pressure = physics.Pressure(value, unit)
        self.energy = None

    def get_pressure(self, unit):
        return self._pressure.values[unit]

    def set_energy(self, value, unit):
        if self.energy:
            self.energy.set_single_value(value, unit)
        else:
            self.energy = physics.Pressure(value, unit)
        if self.elevation:
            self.set_pressure(self.get_energy('mH2O') -
                              self.get_elevation('m'), 'mH2O')

    def remove_output(self, index):
        self.output_pipes.pop(index)

    def remove_input(self, index):
        self.input_pipes.pop(index)


class EndNode(Node):
    def __init__(self):
        Node.__init__(self)
        self._pressure = physics.Pressure(0, 'psi')

    def set_pressure(self, value, unit):
        self._pressure.set_single_value(value, unit)
        self.energy = None

    def get_pressure(self, unit):
        return self._pressure.values[unit]


class InputNode(ConnectionNode):
    pass


class EductorInlet(ConnectionNode):
    def set_pressure(self, value, unit):
        if self._pressure:
            self._pressure.set_single_value(value, unit)
            # print len(self.get_output_pipes())
            for edge in self.get_output_pipes():
                try:
                    edge.is_eductor()
                    edge.output_node.influence_pressure(value*.65, unit)
                    # print "inicia"
                    # print "{} asi".format(guess)
                except AttributeError:
                    pass
        else:
            self._pressure = physics.Pressure(value, unit)
        self.energy = None

    # def get_energy(self, unit):
    #     super(EductorInlet, self).get_energy(unit)
    #     # print "Got energy inlet"


class EductorOutlet(ConnectionNode):
    def __init__(self):
        super(EductorOutlet, self).__init__()
        self._reference_pressure = None

    def influence_pressure(self, value, unit):
        # print "influencing {}".format(self.name)
        if self._reference_pressure:
            self._reference_pressure.set_single_value(value, unit)
        else:
            self._reference_pressure = physics.Pressure(value, unit)
        self.energy = None
        current = self.get_pressure(unit)
        if self._pressure:
            current = self.get_pressure(unit)
            average = (value + current) / 2
            self._pressure.set_single_value(average, unit)
        return "mas o menos {:.2f} {}".format((value + current)/2, unit)

    def set_pressure(self, value, unit):
        if self._pressure:
            if self._reference_pressure:
                reference = self._reference_pressure.values[unit]
                factor = 0.
                modified = factor * reference + (1 - factor) * value
                self._pressure.set_single_value(modified, unit)
            else:
                self._pressure.set_single_value(value, unit)
        else:
            self._pressure = physics.Pressure(value, unit)
        self.energy = None

    # def get_energy(self, unit):
    #     super(EductorOutlet, self).get_energy(unit)
    #     # print "Got energy outlet"
