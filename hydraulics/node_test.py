import unittest

from nodes import *
from pipes import *


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
        self.assertAlmostEqual(self.sys_node.get_elevation('ft'), 8 * 3.2808399)

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


class PipeTests(unittest.TestCase):
    def setUp(self):
        self.sys_pipe = Pipe()

    def test_length(self):
        self.sys_pipe.set_length(2, 'm')
        self.assertEqual(self.sys_pipe.get_length('m'), 2)
        self.assertAlmostEqual(self.sys_pipe.get_length('ft'), 2 * 3.2808399, 4)
        self.assertAlmostEqual(self.sys_pipe.get_length('in'), 78.740158, 4)
        self.sys_pipe.set_length(12, 'in')
        self.assertEqual(self.sys_pipe.get_length('ft'), 1)

    def test_input(self):
        input_node = ConnectionNode()
        other_node = ConnectionNode()
        self.sys_pipe.input_node = input_node
        self.assertEqual(self.sys_pipe.input_node, input_node)
        input_node.set_output_pipe(self.sys_pipe)
        fail = False
        try:
            self.sys_pipe.input_node = other_node
        except IndexError:
            fail = True
        self.assertTrue(fail)
        self.assertTrue(self.sys_pipe in input_node.get_output_pipes())

    def test_output(self):
        output_node = ConnectionNode()
        self.sys_pipe.output_node = output_node
        self.assertEqual(self.sys_pipe.output_node, output_node)
        output_node.set_input_pipe(self.sys_pipe)
        self.assertTrue(self.sys_pipe in output_node.get_input_pipes())

    def test_inner_diam(self):
        self.sys_pipe.set_inner_diam(12, 'in')
        self.assertEqual(self.sys_pipe.get_inner_diam('in'), 12)
        self.assertEqual(self.sys_pipe.get_inner_diam('ft'), 1)

    def test_vol_flow(self):
        self.sys_pipe.set_vol_flow(200, 'gpm')
        self.assertEqual(self.sys_pipe.get_vol_flow('gpm'), 200)
        self.assertAlmostEqual(self.sys_pipe.get_vol_flow('m3/H'), 45.4176)

    def test_hazen_williams_loss(self):
        self.sys_pipe.set_length(82, 'ft')
        self.sys_pipe.set_inner_diam(4.026, 'in')
        self.sys_pipe.set_vol_flow(200, 'gpm')
        self.sys_pipe.set_c_coefficient(100)
        loss = self.sys_pipe.hazen_williams_loss('psi')
        self.assertAlmostEqual(loss, 1.5160886, 4)

    def test_negative_flow_loss(self):
        self.sys_pipe.set_length(82, 'ft')
        self.sys_pipe.set_inner_diam(4.026, 'in')
        self.sys_pipe.set_vol_flow(-200, 'gpm')
        self.sys_pipe.set_c_coefficient(100)
        loss = self.sys_pipe.hazen_williams_loss('psi')
        self.assertAlmostEqual(loss, -1.5160886, 4)

    def test_c_coefficient(self):
        self.sys_pipe.set_c_coefficient(100)
        self.assertEqual(self.sys_pipe.get_c_coefficient(), 100)

    def test_name(self):
        self.sys_pipe.name = 1
        self.assertEqual(self.sys_pipe.name, "1")

    def test_diam_completeness(self):
        self.sys_pipe.name = 1
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        self.sys_pipe.output_node = node1
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.assertFalse(self.sys_pipe.is_complete())

    def test_length_completeness(self):
        self.sys_pipe.name = 1
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        self.sys_pipe.output_node = node1
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_inner_diam(10, 'in')
        self.assertFalse(self.sys_pipe.is_complete())

    def test_input_completeness(self):
        self.sys_pipe.name = 1
        node1 = ConnectionNode()
        self.sys_pipe.output_node = node1
        self.sys_pipe.set_inner_diam(10, 'in')
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.assertFalse(self.sys_pipe.is_complete())

    def test_output_completeness(self):
        self.sys_pipe.name = 1
        node0 = ConnectionNode()
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.sys_pipe.set_inner_diam(10, 'in')
        self.assertFalse(self.sys_pipe.is_complete())

    def test_pipe_completeness(self):
        self.sys_pipe.name = 1
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        self.sys_pipe.output_node = node1
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.sys_pipe.set_inner_diam(10, 'in')
        self.assertTrue(self.sys_pipe.is_complete())

    def test_k_factor(self):
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.sys_pipe.set_inner_diam(10.75, 'in')
        self.assertAlmostEqual(self.sys_pipe.k_flow(), 2.7807647e-6, 5)

    def test_pipe_energy_flow(self):
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        node0.set_elevation(10, 'm')
        node1.set_elevation(10, 'm')
        node0.set_pressure(11.26528826, 'psi')
        node1.set_pressure(10, 'psi')
        self.sys_pipe.output_node = node1
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.sys_pipe.set_inner_diam(10.75, 'in')
        self.sys_pipe.get_gpm_flow()
        self.assertAlmostEqual(self.sys_pipe.get_vol_flow('gpm'), 1135.244, 5)

    def test_pipe_negative_energy_flow(self):
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        node0.set_elevation(10, 'm')
        node1.set_elevation(10, 'm')
        node1.set_pressure(11.26528826, 'psi')
        node0.set_pressure(10, 'psi')
        self.sys_pipe.output_node = node1
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.sys_pipe.set_inner_diam(10.75, 'in')
        self.sys_pipe.get_gpm_flow()
        self.assertAlmostEqual(self.sys_pipe.get_vol_flow('gpm'), -1135.244, 5)

    def test_pipe_zero_energy_flow(self):
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        node0.set_elevation(10, 'm')
        node1.set_elevation(10, 'm')
        node1.set_pressure(10, 'psi')
        node0.set_pressure(10, 'psi')
        self.sys_pipe.output_node = node1
        self.sys_pipe.input_node = node0
        self.sys_pipe.set_c_coefficient(100)
        self.sys_pipe.set_length(100, 'm')
        self.sys_pipe.set_inner_diam(10.75, 'in')
        self.sys_pipe.get_gpm_flow()
        self.assertAlmostEqual(self.sys_pipe.get_vol_flow('gpm'), 0, 5)

    def test_jacobian(self):
        self.sys_pipe.set_length(900, 'm')
        self.sys_pipe.set_inner_diam(7.981, 'in')
        self.sys_pipe.set_c_coefficient(100)
        node_i = ConnectionNode()
        node_i.set_energy(90.01, 'psi')
        node_o = ConnectionNode()
        node_o.set_energy(90, 'psi')
        self.sys_pipe.input_node = node_i
        self.sys_pipe.output_node = node_o
        result = 626.5655816
        self.assertAlmostEqual(self.sys_pipe.get_node_jacobian(node_i), result, 5)
        self.assertAlmostEqual(self.sys_pipe.get_node_jacobian(node_o), -result, 5)


if __name__ == '__main__':
    unittest.main()
