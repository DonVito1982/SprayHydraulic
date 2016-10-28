import physics


class Node:
    def __init__(self):
        self.pressure = None
        self.elevation = None

    def set_pressure(self, value, unit):
        self.pressure = physics.Pressure(value, unit)

    def get_pressure(self, unit):
        return self.pressure.values[unit]

    def set_elevation(self, value, unit):
        self.elevation = physics.Elevation(value, unit)

    def get_elevation(self, unit):
        return self.elevation.values[unit]
