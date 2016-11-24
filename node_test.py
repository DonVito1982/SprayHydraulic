import unittest
from nodes import *
from pipes import *


class NodeTests(unittest.TestCase):
    def test_pressure(self):
        sys_node = Node()
        sys_node.set_pressure(8, "psi")
        self.assertEqual(sys_node.get_pressure("psi"), 8)
        self.assertAlmostEqual(sys_node.get_pressure("Pa"), 8*6894.757)
        self.assertAlmostEqual(sys_node.get_pressure('kPa'), 8*6.894757)
        self.assertAlmostEqual(sys_node.get_pressure('mH2O'), 8*0.703088907)
        sys_node.set_pressure(40000, 'Pa')
        self.assertAlmostEqual(sys_node.get_pressure('psi'), 40000/6894.757)
        sys_node.set_pressure(100, 'mH2O')
        self.assertAlmostEqual(sys_node.get_pressure('kPa'), 980.638)
        sys_node.set_pressure(15, 'psi')

    def test_elevation(self):
        sys_node = Node()
        other_node = sys_node
        sys_node.set_elevation(8, 'm')
        self.assertEqual(sys_node.get_elevation('m'), 8)
        self.assertAlmostEqual(sys_node.get_elevation('ft'), 8*3.2808399)
        self.assertEqual(other_node.get_elevation('m'), 8)

    def test_energy(self):
        sys_node = Node()
        sys_node.set_elevation(20, 'm')
        sys_node.set_pressure(20, 'mH2O')
        self.assertEqual(sys_node.get_energy('mH2O'), 40)
        sys_node.set_pressure(15, 'psi')
        self.assertAlmostEqual(sys_node.get_energy('psi'), 43.44590462)

    def test_name(self):
        sys_node = Node()
        sys_node.set_name('1')
        self.assertEqual(sys_node.get_name(), '1')

    def test_energy_pressure_elevation_combo(self):
        sys_node = Node()
        sys_node.set_elevation(20, 'm')
        sys_node.set_energy(35, 'mH2O')
        self.assertEqual(sys_node.get_pressure('mH2O'), 15)
        sys_node.set_pressure(10, 'mH2O')
        self.assertEqual(sys_node.get_energy('mH2O'), 30)

    def test_input_pipe(self):
        sys_node = Node()
        sys_pipe = Pipe()
        sys_pipe2 = Pipe()
        sys_node.set_input_pipe(sys_pipe)
        sys_node.set_input_pipe(sys_pipe2)
        self.assertTrue(sys_pipe in sys_node.get_input_pipes())
        self.assertTrue(sys_pipe2 in sys_node.get_input_pipes())

    def test_output_pipe(self):
        sys_node = Node()
        sys_pipe = Pipe()
        sys_node.set_output_pipe(sys_pipe)
        self.assertTrue(sys_pipe in sys_node.get_output_pipes())


class PipeTests(unittest.TestCase):
    def test_length(self):
        sys_pipe = Pipe()
        sys_pipe.set_length(2, 'm')
        self.assertEqual(sys_pipe.get_length('m'), 2)
        self.assertAlmostEqual(sys_pipe.get_length('ft'), 2*3.2808399, 4)
        self.assertAlmostEqual(sys_pipe.get_length('in'), 24 * 3.2808399, 4)
        sys_pipe.set_length(12, 'in')
        self.assertEqual(sys_pipe.get_length('ft'), 1)

    def test_input(self):
        input_node = Node()
        cur_pipe = Pipe()
        cur_pipe.input_node = input_node
        self.assertEqual(cur_pipe.input_node, input_node)
        input_node.set_output_pipe(cur_pipe)
        self.assertTrue(cur_pipe in input_node.get_output_pipes())

    def test_output(self):
        output_node = Node()
        cur_pipe = Pipe()
        cur_pipe.output_node = output_node
        self.assertEqual(cur_pipe.output_node, output_node)
        output_node.set_input_pipe(cur_pipe)
        self.assertTrue(cur_pipe in output_node.get_input_pipes())

    def test_inner_diam(self):
        cur_pipe = Pipe()
        cur_pipe.set_inner_diam(12, 'in')
        self.assertEqual(cur_pipe.get_inner_diam('in'), 12)
        self.assertEqual(cur_pipe.get_inner_diam('ft'), 1)

    def test_vol_flow(self):
        sys_pipe = Pipe()
        sys_pipe.set_vol_flow(200, 'gpm')
        self.assertEqual(sys_pipe.get_vol_flow('gpm'), 200)
        self.assertAlmostEqual(sys_pipe.get_vol_flow('m3/H'), 45.4176)

    def test_hazen_williams_loss(self):
        cur_pipe = Pipe()
        cur_pipe.set_length(82, 'ft')
        cur_pipe.set_inner_diam(4.026, 'in')
        cur_pipe.set_vol_flow(200, 'gpm')
        cur_pipe.set_c_coefficient(100)
        loss = cur_pipe.hazen_williams_loss('psi')
        self.assertAlmostEqual(loss, 1.5160886, 4)

    def test_negative_flow_loss(self):
        cur_pipe = Pipe()
        cur_pipe.set_length(82, 'ft')
        cur_pipe.set_inner_diam(4.026, 'in')
        cur_pipe.set_vol_flow(-200, 'gpm')
        cur_pipe.set_c_coefficient(100)
        loss = cur_pipe.hazen_williams_loss('psi')
        self.assertAlmostEqual(loss, -1.5160886, 4)

    def test_c_coefficient(self):
        cur_pipe = Pipe()
        cur_pipe.set_c_coefficient(100)
        self.assertEqual(cur_pipe.get_c_coefficient(), 100)


if __name__ == '__main__':
    unittest.main()
