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
        self.assertEqual(self.four_res.get_nodes()[index].get_pressure('psi'),
                         25)
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

    def test_set_active_nodes(self):
        self.assertEqual(self.four_res.get_active_nodes(), [1])
        node1 = EndNode()
        node2 = ConnectionNode()
        self.four_res.add_node(node1)
        self.four_res.add_node(node2)
        self.assertEqual(self.four_res.get_active_nodes(), [1, 4])
        self.assertEqual(self.four_res.get_problem_size(), 2)

    def test_reset_active_nodes(self):
        node_list = self.four_res.get_active_nodes()
        assert len(node_list) == 1
        node1 = ConnectionNode()
        self.four_res.add_node(node1)
        self.assertEqual(self.four_res.get_active_nodes(), [1, 3])

    def test_pipe_name(self):
        self.four_res.set_pipe_name(0, 'p1')
        self.assertEqual(self.pipe0.name, 'p1')

    def test_repeated_pipe_name(self):
        self.pipe0.name = 'p0'
        pipe1 = Pipe()
        self.four_res.add_edge(pipe1)
        self.assertRaises(IndexError,
                          lambda: self.four_res.set_pipe_name(1, 'p0'))

    def test_f_equations(self):
        self.node1.set_elevation(10, 'm')
        self.node1.set_energy(25, 'mH2O')
        self.reserve_node.set_elevation(27, 'm')
        self.nozzle_end.set_elevation(23, 'm')
        self.nozzle0.set_factor(1.2, 'gpm/psi^0.5')
        flow0 = self.pipe0.get_gpm_flow() - self.nozzle0.get_gpm_flow()
        self.assertEqual(float(self.four_res.f_equations()), flow0)

    def test_delete_nozzle(self):
        self.nozzle0.set_factor(1, 'gpm/psi^0.5')
        self.nozzle0.set_required_pressure(36.0, 'psi')
        nozzle2 = Nozzle()
        self.four_res.add_edge(nozzle2)
        for index in range(len(self.four_res.get_edges())):
            self.four_res.set_pipe_name(index, index)
        for index in range(len(self.four_res.get_nodes())):
            self.four_res.set_node_name(index, index)
        self.four_res.hold_nozzle(1)
        self.assert_nozzle_deletion()
        self.four_res.reinsert_nozzle()
        self.assert_nozzle_insertion()

    def assert_nozzle_insertion(self):
        self.assertEqual(len(self.four_res.get_edges()), 3)
        self.assertEqual(self.four_res.get_edges()[1].name, '1')
        output_name = self.four_res.get_nodes()[1].get_output_pipes()[0].name
        self.assertEqual(self.four_res.get_nodes()[1].get_output_flow('gpm'), 0)
        self.assertEqual(output_name, '1')

    def assert_nozzle_deletion(self):
        self.assertEqual(len(self.four_res.get_edges()), 2)
        self.assertEqual(self.four_res.detached_nozzle_index, 1)
        self.assertEqual(self.four_res.get_nodes()[1].get_output_pipes(), [])
        self.assertEqual(self.four_res.get_nodes()[1].get_output_flow('gpm'), 6)

    def test_detach_node_and_downstream(self):
        nozzle = Nozzle()
        self.four_res.add_edge(nozzle)
        self.four_res.detach_node_edge(1, 1)
        self.assertEqual(self.four_res.get_nodes()[1].get_output_pipes(), [])
        self.assertEqual(self.nozzle0.input_node, None)
        self.assertRaises(ValueError,
                          lambda: self.four_res.detach_node_edge(1, 1))

    def test_detach_node_and_upstream(self):
        pipe1 = Pipe()
        self.four_res.add_edge(pipe1)
        self.four_res.connect_node_upstream_edge(1, 2)
        node1_inputs = self.four_res.get_nodes()[1].get_input_pipes()
        self.assertEqual(len(node1_inputs), 2)
        self.four_res.detach_node_edge(1, 2)
        self.assertEqual(len(node1_inputs), 1)
        self.assertEqual(pipe1.output_node, None)
        self.assertRaises(ValueError,
                          lambda: self.four_res.detach_node_edge(0, 1))


class NozzleNetworkTest(unittest.TestCase):
    def setUp(self):
        self.nozzle_network = PNetwork()
        self.input_node = InputNode()

    def test_single_nozzle(self):
        input_node, nozzle0 = self.set_single_nozzle()
        self.nozzle_network.solve_remote_nozzle()
        self.check_nozzle_flow(0, 10)
        self.assertEqual(input_node.get_output_flow('gpm'), -10)
        nozzle0.set_factor(3, 'gpm/psi^0.5')
        self.nozzle_network.solve_remote_nozzle()
        self.check_nozzle_flow(0, 15)
        self.assertAlmostEqual(input_node.get_output_flow('gpm'), -15)

    def check_nozzle_flow(self, nozzle_index, vol_flow):
        nozzle = self.nozzle_network.get_edges()[nozzle_index]
        self.assertAlmostEqual(nozzle.get_vol_flow('gpm'), vol_flow)

    def set_single_nozzle(self):
        input_node = InputNode()
        input_node.set_elevation(10, 'm')
        end_node0 = EndNode()
        end_node0.set_elevation(10, 'm')
        self.nozzle_network.add_node(input_node)
        self.nozzle_network.add_node(end_node0)
        nozzle0 = Nozzle()
        nozzle0.set_factor(2, 'gpm/psi^0.5')
        nozzle0.set_required_pressure(25, 'psi')
        self.nozzle_network.add_edge(nozzle0)
        self.nozzle_network.connect_node_downstream_edge(0, 0)
        self.nozzle_network.connect_node_upstream_edge(1, 0)
        return input_node, nozzle0

    def test_two_nozzles(self):
        input_node, nozzle0, = self.set_single_nozzle()
        end_node1 = EndNode()
        end_node1.set_elevation(10, 'm')
        self.nozzle_network.add_node(end_node1)
        nozzle1 = Nozzle()
        nozzle1.set_factor(1, 'gpm/psi^0.5')
        nozzle1.set_required_pressure(36, 'psi')
        self.nozzle_network.add_edge(nozzle1)
        self.nozzle_network.connect_node_downstream_edge(0, 1)
        self.nozzle_network.connect_node_upstream_edge(2, 1)
        self.nozzle_network.solve_remote_nozzle()
        self.check_nozzle_flow(1, 6)
        self.check_nozzle_flow(0, 12)
        self.assertEqual(input_node.get_output_flow('gpm'), -18)
        nozzle0.set_required_pressure(49, 'psi')
        self.nozzle_network.solve_remote_nozzle()
        self.assertAlmostEqual(input_node.get_output_flow('gpm'), -21)


if __name__ == '__main__':
    unittest.main()
