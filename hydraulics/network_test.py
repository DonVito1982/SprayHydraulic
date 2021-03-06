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
        with self.assertRaises(AssertionError):
            self.four_res.add_node(node2)

    def test_add_pipes(self):
        self.assertTrue(self.pipe0 in self.four_res.get_edges())
        pipe2 = Pipe()
        self.four_res.add_edge(pipe2)
        self.assertEqual(len(self.four_res.get_edges()), 3)
        self.assertTrue(pipe2 in self.four_res.get_edges())
        with self.assertRaises(AssertionError):
            self.four_res.add_edge(pipe2)

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
        with self.assertRaises(ValueError):
            self.four_res.get_node_index_by_name('n3')
        self.assertEqual(self.four_res.get_node_index_by_name('n1'), 1)

    def test_search_pipe_by_name(self):
        self.pipe0.name = 'p0'
        pipe1 = Pipe()
        pipe1.name = 'p1'
        self.four_res.add_edge(pipe1)
        index = self.four_res.get_edge_index_by_name('p0')
        self.assertEqual(self.four_res.edge_at(index).get_length('m'), 1000)
        with self.assertRaises(IndexError):
            self.four_res.get_edge_index_by_name('n3')
        self.assertEqual(self.four_res.get_edge_index_by_name('p1'), 2)

    def test_network_node_name(self):
        self.four_res.set_node_name(0, 'n0')
        self.assertEqual(self.four_res.node_at(0).name, 'n0')
        self.assertEqual(self.reserve_node.name, 'n0')

    def test_repeated_name(self):
        self.reserve_node.name = 'n0'
        node1 = ConnectionNode()
        self.four_res.add_node(node1)
        with self.assertRaises(IndexError):
            self.four_res.set_node_name(1, 'n0')

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

    def test_repeated_pipe_int_name(self):
        self.pipe0.name = 0
        pipe1 = Pipe()
        self.four_res.add_edge(pipe1)
        with self.assertRaises(IndexError):
            self.four_res.set_pipe_name(1, 0)

    def test_detach_node_and_downstream(self):
        nozzle = Nozzle()
        self.four_res.add_edge(nozzle)
        self.four_res.separate_node_from_edge(1, 1)
        self.assertEqual(self.four_res.node_at(1).get_output_pipes(), [])
        self.assertEqual(self.nozzle0.input_node, None)
        with self.assertRaises(IndexError):
            self.four_res.separate_node_from_edge(1, 1)

    def test_detach_node_and_upstream(self):
        pipe1 = Pipe()
        self.four_res.add_edge(pipe1)
        self.four_res.connect_node_upstream_edge(1, 2)
        node1_inputs = self.four_res.node_at(1).get_input_pipes()
        self.assertEqual(len(node1_inputs), 2)
        self.four_res.separate_node_from_edge(1, 2)
        self.assertEqual(len(node1_inputs), 1)
        self.assertEqual(pipe1.output_node, None)
        with self.assertRaises(IndexError):
            self.four_res.separate_node_from_edge(0, 1)

    def test_when_one_nozzle_detached_second_remains(self):
        reservoir1 = EndNode()
        pipe1 = Pipe()
        self.four_res.add_node(reservoir1)
        self.four_res.add_edge(pipe1)
        self.four_res.connect_node_downstream_edge(3, 2)
        self.four_res.connect_node_upstream_edge(1, 2)
        node1_inputs = self.four_res.node_at(1).get_input_pipes()
        self.assertEqual(len(node1_inputs), 2)
        self.four_res.separate_node_from_edge(1, 0)
        self.assertEqual(len(node1_inputs), 1)
        self.assertEqual(self.pipe0.output_node, None)

    def test_input_index_is_3_when_fourth_node_is_input(self):
        input_node = InputNode()
        self.four_res.add_node(input_node)
        self.assertEqual(self.four_res.search_input_index(), 3)


class CompletenessTests(unittest.TestCase):
    def test_complete_network_creation_evaluates_to_completed(self):
        pipe_network = self.build_small_network()
        pipe_network.connect_node_downstream_edge(0, 0)
        pipe_network.connect_node_upstream_edge(1, 0)
        self.assertTrue(pipe_network.is_connected())

    @staticmethod
    def build_small_network():
        node0 = ConnectionNode()
        node0.name = 'n0'
        pipe0 = Pipe()
        pipe0.name = 'p1'
        node1 = EndNode()
        node1.name = 'n1'
        pipe_network = PNetwork()
        pipe_network.add_node(node0)
        pipe_network.add_node(node1)
        pipe_network.add_edge(pipe0)
        return pipe_network

    def test_incomplete_network_evaluates_to_incomplete(self):
        pipe_network = CompletenessTests.build_small_network()
        pipe_network.connect_node_downstream_edge(0, 0)
        self.assertFalse(pipe_network.is_connected())

    def test_not_connected_network_evaluates_to_incomplete(self):
        p_network = self.build_small_network()
        p_network.connect_node_downstream_edge(0, 0)
        p_network.connect_node_upstream_edge(1, 0)
        node2 = ConnectionNode()
        p_network.add_node(node2)
        self.assertFalse(p_network.is_connected())


if __name__ == '__main__':
    unittest.main()
