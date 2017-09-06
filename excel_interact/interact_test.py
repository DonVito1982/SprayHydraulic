import unittest

from hydraulics.nodes import InputNode
from panda_reader import PandaReader as SomeReader
# from excel_reader import ExcelReader as SomeReader
from hydraulics.edges import Pipe
from hydraulics.pipe_network import PNetwork


class ExcelReaderTestsForFirstFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network = SomeReader.invoke('../test_resources/test_network.xlsx')

    def test_gets_network(self):
        self.assertTrue(isinstance(self.network, PNetwork))

    def test_when_reads_file_gets_first_pipe(self):
        self.assertTrue(isinstance(self.network.edge_at(0), Pipe))
        self.assertEqual(self.network.edge_at(0).get_inner_diam('in'), 3.068)
        self.assertEqual(self.network.edge_at(0).get_length('m'), 20)

    def test_second_pipe_diameter(self):
        self.assertEqual(self.network.edge_at(1).get_inner_diam('in'), 1.939)

    def test_fifth_pipe_diameter(self):
        self.assertEqual(self.network.edge_at(4).get_inner_diam('in'), 1.939)

    def test_second_pipe_name(self):
        self.assertEqual(self.network.edge_at(1).name, '2')

    def test_first_pipe_name(self):
        self.assertEqual(self.network.edge_at(0).name, '5"-3-HA5')

    def test_zeroth_node_name(self):
        self.assertEqual(self.network.node_at(0).name, 'i1')

    def test_zeroth_node_height(self):
        zeroth_node = self.network.node_at(0)
        self.assertEqual(zeroth_node.get_elevation('ft'), 2)

    def test_zeroth_node_is_input(self):
        self.assertTrue(isinstance(self.network.node_at(0), InputNode))

    def test_zeroth_pipe_input_name_is_correct(self):
        self.assertEqual(self.network.edge_at(0).input_node.name, 'i1')

    def test_first_node_height(self):
        self.assertEqual(self.network.node_at(1).get_elevation('ft'), 3)

    def test_first_node_is_not_input(self):
        self.assertFalse(isinstance(self.network.node_at(1), InputNode))


class ExcelReaderTestsForSecondFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network = SomeReader.invoke('../test_resources/test_network2.xlsx')

    def test_when_reads_second_file_gets_80mm_in_pipe(self):
        zeroth_edge = self.network.edge_at(0)
        assert isinstance(zeroth_edge, Pipe)
        self.assertEqual(zeroth_edge.get_inner_diam('mm'), 77.92)
        self.assertEqual(zeroth_edge.get_length('ft'), 60)

    def test_first_node_height_is_1_meter(self):
        first_node = self.network.node_at(1)
        self.assertEqual(first_node.get_elevation('m'), 1)

    def test_first_node_name_is_2(self):
        self.assertEqual(self.network.node_at(1).name, '2')

    def test_first_pipe_input_name_is_correct(self):
        self.assertEqual(self.network.edge_at(1).input_node.name, '2')


if __name__ == '__main__':
    unittest.main()
