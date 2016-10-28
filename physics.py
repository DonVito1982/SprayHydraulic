class Pressure:
    """
    This class will serve to instantiate pressure measures
    """
    units = ['psi', 'Pascal', 'KPa']
    conversion = [[1, 6894.757, 6.894757],
                  [1/6894.757, 1, 1e-3],
                  [1/6.894757, 1e3, 1]]

    def __init__(self, value=None, unit=None):
        self.values = {}
        if unit is not None:
            self.set_single_value(value, unit)

    def set_single_value(self, value, unit):
        u_index = Pressure.units.index(unit)
        for cont in range(len(Pressure.units)):
            cur_unit = Pressure.units[cont]
            self.values[cur_unit] = value * Pressure.conversion[u_index][cont]


class Elevation:
    """
    Serves to instantiate elevation measures
    """
    units = ['m', 'ft']
    conversion = [[1, 3.2808],
                  [1/3.2808, 1]]

    def __init__(self, value=None, unit=None):
        self.values = {}
        if unit is not None:
            self.set_single_value(value, unit)

    def set_single_value(self, value, unit):
        u_index = Elevation.units.index(unit)
        for cont in range(len(Elevation.units)):
            cur_unit = Elevation.units[cont]
            self.values[cur_unit] = value * Elevation.conversion[u_index][cont]
