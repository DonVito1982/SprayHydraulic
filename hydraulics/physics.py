WMETER_TO_PSI = 1.4219702
# GAL_TO_LT = 3.785411
PSI_TO_KPA = 6.894757
IN_TO_MM = 25.4


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
    conversion = [[1, 1000 * PSI_TO_KPA, PSI_TO_KPA, 1 / WMETER_TO_PSI],
                  [0.001 / PSI_TO_KPA, 1, 1e-3,
                   PSI_TO_KPA * 1000 / WMETER_TO_PSI],
                  [1 / PSI_TO_KPA, 1e3, 1, PSI_TO_KPA / WMETER_TO_PSI],
                  [WMETER_TO_PSI, 9806.38, 9.80638, 1]]


class Length(Measure):
    """
    Serves to instantiate elevation or length measures
    """
    units = ['m', 'ft', 'in', 'mm']
    ft_to_mm = IN_TO_MM * 12
    conversion = [[1, 1000 / ft_to_mm, 1000 / IN_TO_MM, 1000],
                  [ft_to_mm / 1000, 1, 12.0, ft_to_mm],
                  [IN_TO_MM / 1000, 1 / 12.0, 1, IN_TO_MM],
                  [0.001, 1 / ft_to_mm, 1 / IN_TO_MM, 1]]


class Volume(Measure):
    units = ['lt', 'gal', 'm3']
    GAL_TO_LT = 3.785411
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
                  [1 / Volume.GAL_TO_LT, 60 / 1000.0, 1]]


class NozzleK(Measure):
    units = ['gpm/psi^0.5', 'lpm/bar^0.5']
    psi_index = Pressure.units.index('psi')
    kPa_index = Pressure.units.index('kPa')
    psi_to_kPa = Pressure.conversion[psi_index][kPa_index]
    conversion = [[1, Volume.GAL_TO_LT * (100 / psi_to_kPa) ** .5],
                  [((psi_to_kPa / 100) ** .5) / Volume.GAL_TO_LT, 1]]
