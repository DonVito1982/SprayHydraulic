import unittest

from edges import Pipe
from nodes import ConnectionNode, EndNode, InputNode


class NodeTests(unittest.TestCase):
    def setUp(self):
        self.sys_node = ConnectionNode()

    def test_creation(self):
        self.assertTrue(isinstance(self.sys_node, ConnectionNode))

    def test_pressure(self):
        self.sys_node.set_pressure(8, "psi")
        self.assertEqual(self.sys_node.get_pressure("psi"), 8)
        self.assertAlmostEqual(self.sys_node.get_pressure("Pa"), 8 * 6894.757)
        self.assertAlmostEqual(self.sys_node.get_pressure('kPa'), 8 * 6.894757)
        self.assertAlmostEqual(self.sys_node.get_pressure('mH2O'), 5.624711256)
        self.sys_node.set_pressure(40000, 'Pa')
        self.assertAlmostEqual(self.sys_node.get_pressure('psi'), 5.80150975589)
        self.sys_node.set_pressure(100, 'mH2O')
        self.assertAlmostEqual(self.sys_node.get_pressure('kPa'), 980.638)
        self.sys_node.set_pressure(15, 'psi')

    def test_elevation(self):
        self.sys_node.set_elevation(8, 'm')
        self.assertEqual(self.sys_node.get_elevation('m'), 8)
        elevation = self.sys_node.get_elevation('ft')
        self.assertAlmostEqual(elevation, 8 * 3.28083989)

    def test_energy(self):
        self.sys_node.set_elevation(20, 'm')
        self.sys_node.set_pressure(20, 'mH2O')
        self.assertEqual(self.sys_node.get_energy('mH2O'), 40)
        self.sys_node.set_pressure(15, 'psi')
        self.assertAlmostEqual(self.sys_node.get_energy('psi'), 43.44590462)

    def test_name(self):
        self.sys_node.name = 1
        self.assertEqual(self.sys_node.name, '1')

    def test_energy_pressure_elevation_combo(self):
        self.sys_node.set_elevation(20, 'm')
        self.sys_node.set_energy(35, 'mH2O')
        self.assertEqual(self.sys_node.get_pressure('mH2O'), 15)
        self.sys_node.set_pressure(10, 'mH2O')
        self.assertEqual(self.sys_node.get_energy('mH2O'), 30)

    def test_input_pipe(self):
        sys_pipe = Pipe()
        sys_pipe2 = Pipe()
        self.sys_node.set_input_pipe(sys_pipe)
        self.sys_node.set_input_pipe(sys_pipe2)
        self.assertTrue(sys_pipe in self.sys_node.get_input_pipes())
        self.assertTrue(sys_pipe2 in self.sys_node.get_input_pipes())

    def test_output_pipe(self):
        sys_pipe = Pipe()
        self.sys_node.set_output_pipe(sys_pipe)
        self.assertTrue(sys_pipe in self.sys_node.get_output_pipes())

    def test_end_node_energy(self):
        node = EndNode()
        node.set_elevation(10, 'm')
        self.assertEqual(node.get_energy('mH2O'), 10)

    def test_initial_flow_output(self):
        self.assertEqual(self.sys_node.get_output_flow('gpm'), 0)

    def test_flow_output(self):
        self.sys_node.set_output_flow(20, 'gpm')
        self.assertEqual(self.sys_node.get_output_flow('gpm'), 20)
        self.assertAlmostEqual(self.sys_node.get_output_flow('m3/H'), 4.5418, 4)

    def test_input_node(self):
        in_node = InputNode()
        self.assertTrue(isinstance(in_node, ConnectionNode))


if __name__ == '__main__':
    unittest.main()
