import unittest

from edges import Edge
from eductor import Eductor
from nodes import ConnectionNode, EndNode, EductorInlet, EductorOutlet


class NozzleTests(unittest.TestCase):
    def setUp(self):
        self.eductor0 = Eductor()
        self.in_node = EductorInlet()

    def test_creation(self):
        self.assertTrue(isinstance(self.in_node, EductorInlet))
        self.assertTrue(isinstance(self.eductor0, Eductor))
        self.assertTrue(isinstance(self.eductor0, Edge))

    def test_name(self):
        self.eductor0.name = 1
        self.assertEqual(self.eductor0.name, '1')

    def test_input_node(self):
        other_node = ConnectionNode()
        self.eductor0.input_node = self.in_node
        self.assertEqual(self.eductor0.input_node, self.in_node)
        with self.assertRaises(IndexError):
            self.eductor0.input_node = other_node

    def test_fails_when_input_node_is_end_node(self):
        in_node = EndNode()
        with self.assertRaises(TypeError):
            self.eductor0.input_node = in_node

    def test_accepts_EductorOutlet_node_as_output_node(self):
        out_node = EductorOutlet()
        self.eductor0.output_node = out_node
        self.assertEqual(self.eductor0.output_node, out_node)

    def test_fails_when_output_node_is_end_node(self):
        out_node = EndNode()
        with self.assertRaises(TypeError):
            self.eductor0.output_node = out_node

    def test_output_node_is_initially_none(self):
        self.assertEqual(self.eductor0.output_node, None)

    def test_repeated_output_fails(self):
        out_node = EductorOutlet()
        other_node = EductorOutlet()
        self.eductor0.output_node = out_node
        with self.assertRaises(IndexError):
            self.eductor0.output_node = other_node

    def test_when_k_is_set_can_be_fetched(self):
        self.eductor0.set_factor(1.2, 'gpm/psi^0.5')
        k_lpm = self.eductor0.get_factor('lpm/bar^0.5')
        self.assertAlmostEqual(k_lpm, 17.29955, 5)

    def test_when_concentration_is_set_can_be_fetched(self):
        self.eductor0.concentration = 0.03
        self.assertEqual(self.eductor0.concentration, 0.03)

    def test_when_concentration_set_to_letter_fails(self):
        with self.assertRaises(TypeError):
            self.eductor0.concentration = '2'

    def test_when_concentration_set_to_bigger_or_equal_than_1_fails(self):
        with self.assertRaises(ValueError):
            self.eductor0.concentration = 1.2
        with self.assertRaises(ValueError):
            self.eductor0.concentration = 1.0

    def test_when_energy_is_set_vol_flow_can_be_fetched(self):
        self.eductor0.set_factor(2, 'gpm/psi^0.5')
        self.in_node.set_elevation(5, 'm')
        self.in_node.set_pressure(36, 'psi')
        out_node = EductorOutlet()
        out_node.set_elevation(5, 'm')
        out_node.set_pressure(23.4, 'psi')
        self.eductor0.input_node = self.in_node
        self.eductor0.output_node = out_node
        self.eductor0.concentration = 0.03
        eductor_flow = self.eductor0.calculate_gpm_flow()
        self.assertAlmostEqual(eductor_flow, 12)

    def test_when_flow_is_set_concentrate_flow_il_also_set(self):
        out_node = EductorOutlet()
        self.eductor0.output_node = out_node
        self.eductor0.concentration = 0.03
        self.eductor0.set_vol_flow(10, 'gpm')
        self.assertAlmostEqual(out_node.get_output_flow('gpm'), -0.3)

    def test_cant_calculate_gpm_without_concentration(self):
        self.in_node.set_elevation(5, 'm')
        self.in_node.set_pressure(36, 'psi')
        out_node = EductorOutlet()
        out_node.set_elevation(5, 'm')
        out_node.set_pressure(0, 'psi')
        self.eductor0.input_node = self.in_node
        self.eductor0.output_node = out_node
        self.eductor0.concentration = 0.03
        with self.assertRaises(AttributeError):
            self.eductor0.calculate_gpm_flow()

    def test_is_not_complete_without_factor(self):
        self.in_node.set_elevation(5, 'm')
        self.in_node.set_pressure(36, 'psi')
        out_node = EductorOutlet()
        out_node.set_elevation(5, 'm')
        out_node.set_pressure(0, 'psi')
        self.eductor0.input_node = self.in_node
        self.eductor0.output_node = out_node
        self.eductor0.concentration = 0.03
        self.assertFalse(self.eductor0.is_complete())

    def test_is_complete_when_has_all_information(self):
        self.eductor0.set_factor(2, 'gpm/psi^0.5')
        out_node = EductorOutlet()
        self.eductor0.input_node = self.in_node
        self.eductor0.output_node = out_node
        self.eductor0.concentration = 0.03
        self.assertTrue(self.eductor0.is_complete())

    def test_is_not_complete_without_input_node(self):
        self.eductor0.set_factor(3, 'gpm/psi^0.5')
        out_node = EductorOutlet()
        self.eductor0.output_node = out_node
        self.eductor0.concentration = 0.03
        self.assertFalse(self.eductor0.is_complete())

    def test_is_not_complete_without_output_node(self):
        self.eductor0.set_factor(2, 'gpm/psi^0.5')
        self.eductor0.input_node = self.in_node
        self.eductor0.concentration = 0.03
        self.assertFalse(self.eductor0.is_complete())

    def test_is_not_complete_without_concentration(self):
        self.eductor0.set_factor(2, 'gpm/psi^0.5')
        out_node = EductorOutlet()
        self.eductor0.input_node = self.in_node
        self.eductor0.output_node = out_node
        self.assertFalse(self.eductor0.is_complete())

    def test_gpm_flow(self):
        self.eductor0.set_factor(7,  'gpm/psi^0.5')
        self.eductor0.concentration = 0.03
        self.in_node.set_pressure(36, 'psi')
        self.in_node.set_elevation(0, 'm')
        out_node = EductorOutlet()
        out_node.set_elevation(0, 'm')
        out_node.set_pressure(23.4, 'psi')
        self.eductor0.input_node = self.in_node
        self.eductor0.output_node = out_node
        eductor_flow = self.eductor0.calculate_gpm_flow()
        self.assertAlmostEqual(eductor_flow, 42)

    def test_fails_when_inlet_is_not_EductorInlet(self):
        inlet = ConnectionNode()
        with self.assertRaises(TypeError):
            self.eductor0.input_node = inlet

    def test_fails_when_outlet_is_not_EductorOutlet(self):
        outlet = ConnectionNode()
        with self.assertRaises(TypeError):
            self.eductor0.output_node = outlet


if __name__ == '__main__':
    unittest.main()
