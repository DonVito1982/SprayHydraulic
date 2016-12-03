import unittest

from pipes import Pipe
from pipe_network import PNetwork
from nodes import ConnectionNode, EndNode


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.four_res = PNetwork()
        self.pipe0 = Pipe()
        self.pipe0.set_length(1000, 'm')
        self.pipe0.set_inner_diam(10.75, 'in')
        self.pipe0.set_c_coefficient(100)
        self.node0 = ConnectionNode()

    def test_create_network(self):
        self.assertEqual(True, isinstance(self.four_res, PNetwork))

    def test_add_nodes(self):
        node2 = ConnectionNode()
        self.four_res.add_node(self.node0)
        self.assertTrue(self.node0 in self.four_res.get_nodes())
        self.four_res.add_node(node2)
        self.assertEqual(len(self.four_res.net_nodes), 2)
        self.assertTrue(node2 in self.four_res.get_nodes())

    def test_add_pipes(self):
        self.four_res.add_pipe(self.pipe0)
        self.assertTrue(self.pipe0 in self.four_res.get_pipes())
        pipe2 = Pipe()
        self.four_res.add_pipe(pipe2)
        self.assertEqual(len(self.four_res.get_pipes()), 2)

    def test_node_upstream_pipe(self):
        PNetwork.node_upstream_pipe(self.node0, self.pipe0)
        self.assertTrue(self.pipe0 in self.node0.get_input_pipes())
        self.assertEqual(self.pipe0.output_node, self.node0)

    def test_search_node_by_name(self):
        self.node0.name = 'n0'
        self.node0.set_pressure(25, 'psi')
        node1 = ConnectionNode()
        node1.name = 'n1'
        self.four_res.add_node(self.node0)
        self.four_res.add_node(node1)
        self.assertEqual(self.four_res.node_by_name('n0').get_pressure('psi'), 25)
        self.assertRaises(IndexError, lambda: self.four_res.node_by_name('n3'))

    def test_node_downstream_pipe(self):
        PNetwork.node_downstream_pipe(self.node0, self.pipe0)
        self.assertTrue(self.pipe0 in self.node0.get_output_pipes())
        self.assertEqual(self.pipe0.input_node, self.node0)

    def test_set_active_nodes(self):
        node1 = EndNode()
        node2 = ConnectionNode()
        self.four_res.add_node(self.node0)
        self.four_res.add_node(node1)
        self.four_res.add_node(node2)
        self.assertEqual(self.four_res.get_active_nodes(), [0, 2])
        self.assertEqual(self.four_res.get_problem_size(), 2)

    def test_reset_active_nodes(self):
        self.four_res.add_node(self.node0)
        node_list = self.four_res.get_active_nodes()
        assert len(node_list) == 1
        node1 = ConnectionNode()
        self.four_res.add_node(node1)
        self.assertEqual(self.four_res.get_active_nodes(), [0, 1])

if __name__ == '__main__':
    unittest.main()
