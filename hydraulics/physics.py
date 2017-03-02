WMETER_TO_PSI = 1.422295231
GAL_TO_LT = 3.7848


class Measure(object):
    units = []
    conversion = [[]]

    def __init__(self, value=None, unit=None):
        self.values = {}
        if unit:
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
    conversion = [[1, 6894.757, 6.894757, 1 / WMETER_TO_PSI],
                  [1 / 6894.757, 1, 1e-3, 0.000101974],
                  [1 / 6.894757, 1e3, 1, 0.101974],
                  [WMETER_TO_PSI, 9806.38, 9.80638, 1]]


class Length(Measure):
    """
    Serves to instantiate elevation measures
    """
    units = ['m', 'ft', 'in']
    conversion = [[1, 3.28083989, 39.37007874],
                  [1 / 3.28083989, 1, 12.0],
                  [1 / 39.37007874, 1 / 12.0, 1]]


class Volume(Measure):
    units = ['lt', 'gal', 'm3']
    conversion = [[1, 1 / GAL_TO_LT, 0.001],
                  [GAL_TO_LT, 1, GAL_TO_LT / 1000],
                  [1000, 1000 / GAL_TO_LT, 1]]


class Time(Measure):
    units = ['min', 'hr']
    conversion = [[1, 1 / 60.0],
                  [60.0, 1]]


class VolFlow(Measure):
    """
    Serves to instantiate volumetric flows
    """
    units = ['gpm', 'm3/H', 'lpm']
    gal_index = Volume.units.index('gal')
    m3_index = Volume.units.index('m3')
    gal_to_m3 = Volume.conversion[gal_index][m3_index]
    conversion = [[1, gal_to_m3 * 60, Volume.conversion[1][0]],
                  [Volume.conversion[2][1] * Time.conversion[0][1], 1,
                   1000 / 60.0],
                  [1 / GAL_TO_LT, 60 / 1000.0, 1]]


class NozzleK(Measure):
    units = ['gpm/psi^0.5', 'lpm/bar^0.5']
    psi_index = Pressure.units.index('psi')
    kPa_index = Pressure.units.index('kPa')
    psi_to_kPa = Pressure.conversion[psi_index][kPa_index]
    conversion = [[1, GAL_TO_LT * (100 / psi_to_kPa) ** .5],
                  [((psi_to_kPa / 100) ** .5) / GAL_TO_LT, 1]]
