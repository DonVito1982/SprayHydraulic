import unittest

from edges import Pipe, Nozzle
from nodes import ConnectionNode, EndNode, InputNode
from pipe_network import PNetwork


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.four_res = PNetwork()
        self.pipe0 = Pipe()
        self.pipe0.set_length(1000, 'm')
        self.pipe0.set_inner_diam(10.75, 'in')
        self.pipe0.set_c_coefficient(100)
        self.reserve_node = EndNode()
        self.node1 = ConnectionNode()
        self.nozzle_end = EndNode()
        self.nozzle0 = Nozzle()
        self.four_res.add_node(self.reserve_node)
        self.four_res.add_node(self.node1)
        self.four_res.add_node(self.nozzle_end)
        self.four_res.add_edge(self.pipe0)
        self.four_res.add_edge(self.nozzle0)
        self.four_res.connect_node_downstream_edge(0, 0)
        self.four_res.connect_node_upstream_edge(1, 0)
        self.four_res.connect_node_downstream_edge(1, 1)
        self.four_res.connect_node_upstream_edge(2, 1)

    def test_create_network(self):
        self.assertEqual(True, isinstance(self.four_res, PNetwork))

    def test_when_node_at_position_queried_obtained(self):
        self.assertTrue(self.four_res.node_at(1) is self.node1)

    def test_add_nodes(self):
        node2 = ConnectionNode()
        self.assertTrue(self.reserve_node in self.four_res.get_nodes())
        self.four_res.add_node(node2)
        self.assertEqual(len(self.four_res.get_nodes()), 4)
        self.assertTrue(node2 in self.four_res.get_nodes())
        self.assertRaises(AssertionError, lambda: self.four_res.add_node(node2))

    def test_add_pipes(self):
        self.assertTrue(self.pipe0 in self.four_res.get_edges())
        pipe2 = Pipe()
        self.four_res.add_edge(pipe2)
        self.assertEqual(len(self.four_res.get_edges()), 3)
        self.assertTrue(pipe2 in self.four_res.get_edges())
        self.assertRaises(AssertionError, lambda: self.four_res.add_edge(pipe2))

    def test_node_upstream_pipe(self):
        self.assertTrue(self.pipe0 in self.node1.get_input_pipes())
        self.assertEqual(self.pipe0.output_node, self.node1)

    def test_search_node_by_name(self):
        self.reserve_node.name = 'n0'
        self.node1.set_pressure(25, 'psi')
        self.node1.name = 'n1'
        index = self.four_res.get_node_index_by_name('n1')
        node_pressure = self.four_res.node_at(index).get_pressure('psi')
        self.assertEqual(node_pressure, 25)
        self.assertRaises(IndexError,
                          lambda: self.four_res.get_node_index_by_name('n3'))
        self.assertEqual(self.four_res.get_node_index_by_name('n1'), 1)

    def test_search_pipe_by_name(self):
        self.pipe0.name = 'p0'
        pipe1 = Pipe()
        pipe1.name = 'p1'
        self.four_res.add_edge(pipe1)
        index = self.four_res.get_edge_index_by_name('p0')
        self.assertEqual(self.four_res.get_edges()[index].get_length('m'),
                         1000)
        self.assertRaises(IndexError,
                          lambda: self.four_res.get_edge_index_by_name('n3'))
        self.assertEqual(self.four_res.get_edge_index_by_name('p1'), 2)

    def test_network_node_name(self):
        self.four_res.set_node_name(0, 'n0')
        self.assertEqual(self.four_res.get_nodes()[0].name, 'n0')
        self.assertEqual(self.reserve_node.name, 'n0')

    def test_repeated_name(self):
        self.reserve_node.name = 'n0'
        node1 = ConnectionNode()
        self.four_res.add_node(node1)
        self.assertRaises(IndexError,
                          lambda: self.four_res.set_node_name(1, 'n0'))

    def test_node_downstream_pipe(self):
        self.assertTrue(self.pipe0 in self.reserve_node.get_output_pipes())
        self.assertEqual(self.pipe0.input_node, self.reserve_node)

    def test_pipe_name(self):
        self.four_res.set_pipe_name(0, 'p1')
        self.assertEqual(self.pipe0.name, 'p1')

    def test_repeated_pipe_name(self):
        self.pipe0.name = 'p0'
        pipe1 = Pipe()
        self.four_res.add_edge(pipe1)
        self.assertRaises(IndexError,
                          lambda: self.four_res.set_pipe_name(1, 'p0'))

    def test_detach_node_and_downstream(self):
        nozzle = Nozzle()
        self.four_res.add_edge(nozzle)
        self.four_res.separate_node_from_edge(1, 1)
        self.assertEqual(self.four_res.get_nodes()[1].get_output_pipes(), [])
        self.assertEqual(self.nozzle0.input_node, None)
        self.assertRaises(ValueError,
                          lambda: self.four_res.separate_node_from_edge(1, 1))

    def test_detach_node_and_upstream(self):
        pipe1 = Pipe()
        self.four_res.add_edge(pipe1)
        self.four_res.connect_node_upstream_edge(1, 2)
        node1_inputs = self.four_res.get_nodes()[1].get_input_pipes()
        self.assertEqual(len(node1_inputs), 2)
        self.four_res.separate_node_from_edge(1, 2)
        self.assertEqual(len(node1_inputs), 1)
        self.assertEqual(pipe1.output_node, None)
        self.assertRaises(ValueError,
                          lambda: self.four_res.separate_node_from_edge(0, 1))

    def test_input_index_is_3_when_fourth_node_is_input(self):
        input_node = InputNode()
        self.four_res.add_node(input_node)
        self.assertEqual(self.four_res.search_input_index(), 3)


if __name__ == '__main__':
    unittest.main()
