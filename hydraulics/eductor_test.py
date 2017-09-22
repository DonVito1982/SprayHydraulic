import unittest

from edges import Edge
from eductor import Eductor
from nodes import ConnectionNode, EndNode


class NozzleTests(unittest.TestCase):
    def setUp(self):
        self.eductor0 = Eductor()
        self.in_node = ConnectionNode()

    def test_creation(self):
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
        with self.assertRaises(ValueError):
            self.eductor0.input_node = in_node

    def test_accepts_connection_node_as_output_node(self):
        self.eductor0.output_node = self.in_node
        self.assertEqual(self.eductor0.output_node, self.in_node)

    def test_fails_when_output_node_is_end_node(self):
        out_node = EndNode()
        with self.assertRaises(ValueError):
            self.eductor0.output_node = out_node

    def test_output_node_is_initially_none(self):
        self.assertEqual(self.eductor0.output_node, None)

    def test_repeated_output_fails(self):
        other_node = ConnectionNode()
        self.eductor0.output_node = self.in_node
        with self.assertRaises(IndexError):
            self.eductor0.output_node = other_node

if __name__ == '__main__':
    unittest.main()
