import unittest

from edges import Edge
from nodes import ConnectionNode, EndNode


class PumpTests(unittest.TestCase):
    def setUp(self):
        self.pump = Pump()

    def test_creation(self):
        self.assertTrue(isinstance(self.pump, Pump))
        self.assertTrue(isinstance(self.pump, Edge))

    def test_name(self):
        self.pump.name = 1
        self.assertEqual(self.pump.name, '1')

    def test_input_node_set_then_input_node_retrieved(self):
        in_node = ConnectionNode()
        self.pump.input_node = in_node
        self.assertEqual(self.pump.input_node, in_node)

    def test_when_set_end_node_as_input_node_fails(self):
        end_node = EndNode()
        with self.assertRaises(ValueError):
            self.pump.input_node = end_node

    def test_when_second_input_set_fails(self):
        in_node = ConnectionNode()
        self.pump.input_node = in_node
        other_node = ConnectionNode()
        with self.assertRaises(IndexError):
            self.pump.input_node = other_node


class Pump(Edge):
    def calculate_gpm_flow(self):
        pass

    def get_node_jacobian(self, node):
        pass

    def is_complete(self):
        pass

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        if isinstance(node, EndNode):
            raise ValueError
        if self._input_node:
            raise IndexError
        self._input_node = node


if __name__ == '__main__':
    unittest.main()
