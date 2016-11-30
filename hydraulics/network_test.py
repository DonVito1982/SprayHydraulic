import unittest

from pipes import Pipe
from pipe_network import *
from nodes import Node


class HardWiredEnergyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reservoir_net = PNetwork()
        elevations = [100, 85, 65, 65, 70, 70]
        names = ["n0", "n1", "n2", "n3", "n4", "n5"]
        node_count = len(elevations)
        for node_index in range(node_count):
            cur_node = Node()
            cur_node.set_pressure(0, 'psi')
            cur_node.set_elevation(elevations[node_index], 'm')
            cur_node.name = names[node_index]
            cls.reservoir_net.add_node(cur_node)
        lengths = [1000, 1200, 900, 500, 600]
        inner_diameters = [10.75, 7.981, 7.981, 6.065, 6.065]
        pipe_count = len(lengths)
        for pipe_index in range(pipe_count):
            cur_pipe = Pipe()
            cur_pipe.set_length(lengths[pipe_index], 'm')
            cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
            cur_pipe.set_c_coefficient(100)
            cur_pipe.name = "p%d" % pipe_index
            cls.reservoir_net.add_pipe(cur_pipe)

    def test_pipe_existence(self):
        network = self.__class__.reservoir_net
        self.assertEqual(network.get_nodes()[0].name, "n0")


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.four_res = PNetwork()

    def test_create_network(self):
        self.assertEqual(True, isinstance(self.four_res, PNetwork))

    def test_add_nodes(self):
        node1 = Node()
        node2 = Node()
        self.four_res.add_node(node1)
        self.assertTrue(node1 in self.four_res.get_nodes())
        self.four_res.add_node(node2)
        self.assertEqual(len(self.four_res.net_nodes), 2)
        self.assertTrue(node2 in self.four_res.get_nodes())

    def test_add_pipes(self):
        pipe1 = Pipe()
        self.four_res.add_pipe(pipe1)
        self.assertTrue(pipe1 in self.four_res.get_pipes())
        pipe2 = Pipe()
        self.four_res.add_pipe(pipe2)
        self.assertEqual(len(self.four_res.get_pipes()), 2)

    def test_node_upstream_pipe(self):
        node0 = Node()
        pipe0 = Pipe()
        PNetwork.node_upstream_pipe(node0, pipe0)
        self.assertTrue(pipe0 in node0.get_input_pipes())
        self.assertEqual(pipe0.output_node, node0)

    def test_search_node_by_name(self):
        node0 = Node()
        node0.name = 'n0'
        node0.set_pressure(25, 'psi')
        node1 = Node()
        node1.name = 'n1'
        self.four_res.add_node(node0)
        self.four_res.add_node(node1)
        self.assertEqual(self.four_res.node_by_name('n0').get_pressure('psi'), 25)
        self.assertRaises(NameException, lambda: self.four_res.node_by_name('n3'))

    def test_node_downstream_pipe(self):
        node0 = Node()
        pipe0 = Pipe()
        PNetwork.node_downstream_pipe(node0, pipe0)
        self.assertTrue(pipe0 in node0.get_output_pipes())
        self.assertEqual(pipe0.input_node, node0)


if __name__ == '__main__':
    unittest.main()
