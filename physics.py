class Measure(object):
    units = []
    conversion = [[]]

    def __init__(self, value=None, unit=None):
        self.values = {}
        if unit is not None:
            self.set_single_value(value, unit)

    def set_single_value(self, value, unit):
        """
        Define the values for the whole list of possible units
        :param value: the referential value
        :type value: float
        :param unit: the referential unit
        :type unit: str
        :return:
        """
        u_index = self.__class__.units.index(unit)
        conversion_factors = self.__class__.conversion[u_index]
        for cont in range(len(self.__class__.units)):
            current_unit = self.__class__.units[cont]
            self.values[current_unit] = value * conversion_factors[cont]


class Pressure(Measure):
    """
    This class will serve to instantiate _pressure measures
    """
    units = ['psi', 'Pa', 'kPa', 'mH2O']
    conversion = [[1, 6894.757, 6.894757, 0.703088907],
                  [1/6894.757, 1, 1e-3, 0.000101974],
                  [1/6.894757, 1e3, 1, 0.101974],
                  [1.422295231, 9806.38, 9.80638, 1]]


class Length(Measure):
    """
    Serves to instantiate elevation measures
    """
    units = ['m', 'ft', 'in']
    conversion = [[1, 3.2808399, 39.37007874],
                  [1/3.2808399, 1, 12.0],
                  [1/39.37007874, 1/12.0, 1]]


class VolFlow(Measure):
    """
    Serves to instantiate volumetric flows
    """
    units = ['gpm', 'm3/H']
    conversion = [[1, 0.227088],
                  [25.01233, 1]]
