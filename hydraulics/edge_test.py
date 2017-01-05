import unittest

from pipes import Pipe, ConnectionNode, Nozzle, Edge, EndNode


class PipeTest(unittest.TestCase):
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

    def test_false_input(self):
        false_input = 'this is not a node'
        fail = False
        try:
            self.sys_pipe.input_node = false_input
        except ValueError:
            fail = True
        self.assertTrue(fail)

    def test_output(self):
        output_node = ConnectionNode()
        self.sys_pipe.output_node = output_node
        self.assertEqual(self.sys_pipe.output_node, output_node)
        output_node.set_input_pipe(self.sys_pipe)
        self.assertTrue(self.sys_pipe in output_node.get_input_pipes())

    def test_false_output(self):
        fail = False
        try:
            self.sys_pipe.output_node = 'node'
        except ValueError:
            fail = True
        self.assertTrue(fail)

    def test_repeated_output(self):
        output_node = ConnectionNode()
        other_node = ConnectionNode()
        self.sys_pipe.output_node = output_node
        fail = False
        try:
            self.sys_pipe.output_node = other_node
        except IndexError:
            fail = True
        self.assertTrue(fail)

    def test_inner_diam(self):
        self.sys_pipe.set_inner_diam(12, 'in')
        self.assertEqual(self.sys_pipe.get_inner_diam('in'), 12)
        self.assertEqual(self.sys_pipe.get_inner_diam('ft'), 1)

    def test_vol_flow(self):
        self.sys_pipe.set_vol_flow(200, 'gpm')
        self.assertEqual(self.sys_pipe.get_vol_flow('gpm'), 200)
        self.assertAlmostEqual(self.sys_pipe.get_vol_flow('m3/H'), 45.4176)
        self.assertAlmostEqual(self.sys_pipe.get_vol_flow('lpm'), 756.96)

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

    def test_c_completeness(self):
        self.sys_pipe.name = 1
        node0 = ConnectionNode()
        node1 = ConnectionNode()
        self.sys_pipe.input_node = node0
        self.sys_pipe.output_node = node1
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
        self.assertAlmostEqual(self.sys_pipe.get_node_jacobian(node_i),
                               result, 5)
        self.assertAlmostEqual(self.sys_pipe.get_node_jacobian(node_o),
                               -result, 5)


class NozzleTests(unittest.TestCase):
    def setUp(self):
        self.nozzle0 = Nozzle()

    def test_creation(self):
        self.assertTrue(isinstance(self.nozzle0, Nozzle))
        self.assertTrue(isinstance(self.nozzle0, Edge))

    def test_name(self):
        self.nozzle0.name = 3
        self.assertEqual(self.nozzle0.name, '3')

    def test_input_node(self):
        input_node = ConnectionNode()
        other_node = ConnectionNode()
        self.nozzle0.input_node = input_node
        self.assertEqual(self.nozzle0.input_node, input_node)
        fail = False
        try:
            self.nozzle0.input_node = other_node
        except IndexError:
            fail = True
        self.assertTrue(fail)

    def test_false_input(self):
        false_input = 'false node'
        fail = False
        try:
            self.nozzle0.input_node = false_input
        except ValueError:
            fail = True
        self.assertTrue(fail)

    def test_output(self):
        output_node = EndNode()
        self.nozzle0.output_node = output_node
        self.assertEqual(self.nozzle0.output_node, output_node)

    def test_end_output(self):
        output_node = ConnectionNode()
        fail = False
        try:
            self.nozzle0.output_node = output_node
        except ValueError:
            fail = True
        self.assertTrue(fail)

    def test_repeated_output(self):
        output_node = EndNode()
        other_node = EndNode()
        self.nozzle0.output_node = output_node
        fail = False
        try:
            self.nozzle0.output_node = other_node
        except ValueError:
            fail = True
        self.assertTrue(fail)

    def test_k_factor(self):
        self.nozzle0.set_factor(1.2, 'gpm/psi^0.5')
        k_lpm = self.nozzle0.get_factor('lpm/bar^0.5')
        self.assertAlmostEqual(k_lpm, 17.296757, 5)
        self.nozzle0.set_factor(17.29675758, 'lpm/bar^0.5')
        self.assertAlmostEqual(self.nozzle0.get_factor('gpm/psi^0.5'), 1.2)

    def test_gpm_flow(self):
        self.nozzle0.set_factor(2, 'gpm/psi^0.5')
        in_node = ConnectionNode()
        in_node.set_elevation(5, 'm')
        in_node.set_pressure(36, 'psi')
        out_node = EndNode()
        out_node.set_elevation(5, 'm')
        self.nozzle0.input_node = in_node
        self.nozzle0.output_node = out_node
        nozzle_flow = self.nozzle0.get_gpm_flow()
        self.assertAlmostEqual(nozzle_flow, 12)


if __name__ == '__main__':
    unittest.main()
