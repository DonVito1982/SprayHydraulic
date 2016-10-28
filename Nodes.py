import physics


class Node:
    def __init__(self):
        self.pressure = None
        self.elevation = None

    def set_pressure(self, value, unit):
        if self.pressure:
            self.pressure.set_single_value(value, unit)
        else:
            self.pressure = physics.Pressure(value, unit)

    def get_pressure(self, unit):
        return self.pressure.values[unit]

    def set_elevation(self, value, unit):
        if self.elevation:
            self.elevation.set_single_value(value, unit)
        else:
            self.elevation = physics.Length(value, unit)

    def get_elevation(self, unit):
        return self.elevation.values[unit]
