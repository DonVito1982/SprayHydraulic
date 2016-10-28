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
    This class will serve to instantiate pressure measures
    """
    units = ['psi', 'Pascal', 'KPa']
    conversion = [[1, 6894.757, 6.894757],
                  [1/6894.757, 1, 1e-3],
                  [1/6.894757, 1e3, 1]]


class Length(Measure):
    """
    Serves to instantiate elevation measures
    """
    units = ['m', 'ft']
    conversion = [[1, 3.2808],
                  [1/3.2808, 1]]
