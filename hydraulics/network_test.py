import unittest

from pipes import Pipe, ConnectionNode, EndNode
from pipe_network import PNetwork


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
        self.four_res.add_node(self.node0)
        self.four_res.add_pipe(self.pipe0)
        self.four_res.connect_node_upstream_pipe(0, 0)
        self.assertTrue(self.pipe0 in self.node0.get_input_pipes())
        self.assertEqual(self.pipe0.output_node, self.node0)

    def test_search_node_by_name(self):
        self.node0.name = 'n0'
        self.node0.set_pressure(25, 'psi')
        node1 = ConnectionNode()
        node1.name = 'n1'
        self.four_res.add_node(self.node0)
        self.four_res.add_node(node1)
        index = self.four_res.get_node_index_by_name('n0')
        self.assertEqual(self.four_res.get_nodes()[index].get_pressure('psi'),
                         25)
        self.assertRaises(IndexError,
                          lambda: self.four_res.get_node_index_by_name('n3'))
        self.assertEqual(self.four_res.get_node_index_by_name('n1'), 1)

    def test_search_pipe_by_name(self):
        self.pipe0.name = 'p0'
        pipe1 = Pipe()
        pipe1.name = 'p1'
        self.four_res.add_pipe(self.pipe0)
        self.four_res.add_pipe(pipe1)
        index = self.four_res.get_pipe_index_by_name('p0')
        self.assertEqual(self.four_res.get_pipes()[index].get_length('m'),
                         1000)
        self.assertRaises(IndexError,
                          lambda: self.four_res.get_pipe_index_by_name('n3'))
        self.assertEqual(self.four_res.get_pipe_index_by_name('p1'), 1)

    def test_network_node_name(self):
        self.four_res.add_node(self.node0)
        self.four_res.set_node_name(0, 'n0')
        self.assertEqual(self.four_res.get_nodes()[0].name, 'n0')
        self.assertEqual(self.node0.name, 'n0')

    def test_repeated_name(self):
        self.node0.name = 'n0'
        self.four_res.add_node(self.node0)
        node1 = ConnectionNode()
        self.four_res.add_node(node1)
        self.assertRaises(IndexError,
                          lambda: self.four_res.set_node_name(1, 'n0'))

    def test_node_downstream_pipe(self):
        self.four_res.add_node(self.node0)
        self.four_res.add_pipe(self.pipe0)
        self.four_res.connect_node_downstream_pipe(0, 0)
        self.assertTrue(self.pipe0 in self.node0.get_output_pipes())
        self.assertEqual(self.pipe0.input_node, self.node0)

    def test_set_active_nodes(self):
        self.assertEqual(self.four_res.get_active_nodes(), [])
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

    def test_pipe_name(self):
        self.four_res.add_pipe(self.pipe0)
        self.four_res.set_pipe_name(0, 'p1')
        self.assertEqual(self.pipe0.name, 'p1')

    def test_repeated_pipe_name(self):
        self.pipe0.name = 'p0'
        self.four_res.add_pipe(self.pipe0)
        pipe1 = Pipe()
        self.four_res.add_pipe(pipe1)
        self.assertRaises(IndexError,
                          lambda: self.four_res.set_pipe_name(1, 'p0'))

    def test_f_equations(self):
        self.node0.set_energy(25, 'mH2O')
        node1 = EndNode()
        node1.set_elevation(27, 'm')
        node2 = EndNode()
        node2.set_elevation(23, 'm')
        self.four_res.add_pipe(self.pipe0)
        self.four_res.add_node(self.node0)
        self.four_res.add_node(node1)
        self.four_res.add_node(node2)
        pipe1 = Pipe()
        pipe1.set_inner_diam(6, 'in')
        pipe1.set_c_coefficient(100)
        pipe1.set_length(800, 'm')
        self.four_res.add_pipe(pipe1)
        self.four_res.connect_node_upstream_pipe(0, 0)
        self.four_res.connect_node_downstream_pipe(0, 1)
        self.four_res.connect_node_downstream_pipe(1, 0)
        self.four_res.connect_node_upstream_pipe(2, 1)
        flow0 = self.pipe0.get_gpm_flow() - pipe1.get_gpm_flow()
        self.assertEqual(float(self.four_res.f_equations()), flow0)


class ExampleTests(unittest.TestCase):
    def test_four_reservoir(self):
        elevations = [100, 85, 65, 65, 70, 70]
        names = [0, 1, 2, 3, 4, 5]
        problem = PNetwork()

        # SET END NODES
        for cont in range(4):
            cur_node = EndNode()
            cur_node.set_elevation(elevations[cont], 'm')
            cur_node.name = names[cont]
            problem.add_node(cur_node)

        # SET CONNECTION NODES
        node_count = len(elevations)
        end_count = 4

        for node_index in range(end_count, node_count):
            cur_node = ConnectionNode()
            cur_node.set_pressure(0, 'psi')
            cur_node.set_elevation(elevations[node_index], 'm')
            cur_node.name = names[node_index]
            problem.add_node(cur_node)

        # SET PIPES
        lengths = [1000, 1200, 900, 500, 600]
        inner_diameters = [10.75, 7.981, 7.981, 6.065, 6.065]

        pipe_count = len(lengths)
        for pipe_index in range(pipe_count):
            cur_pipe = Pipe()
            cur_pipe.set_length(lengths[pipe_index], 'm')
            cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
            cur_pipe.set_c_coefficient(100)
            cur_pipe.name = pipe_index
            problem.add_pipe(cur_pipe)

        # SET CONNECTIVITY
        problem.connect_node_downstream_pipe(4, 2)
        problem.connect_node_upstream_pipe(4, 1)
        problem.connect_node_upstream_pipe(4, 0)
        problem.connect_node_downstream_pipe(0, 0)
        problem.connect_node_downstream_pipe(1, 1)
        problem.connect_node_upstream_pipe(5, 2)
        problem.connect_node_downstream_pipe(5, 3)
        problem.connect_node_downstream_pipe(5, 4)
        problem.connect_node_upstream_pipe(2, 3)
        problem.connect_node_upstream_pipe(3, 4)

        problem.solve_system()

        end_flows = []

        for cont5 in range(pipe_count):
            end_flows.append(problem.get_pipes()[cont5].get_gpm_flow())

        # FLOW CHECK
        test_flows = [1135.2443, -383.5847, 751.6596, 394.3143, 357.3453]
        for cont in range(pipe_count):
            self.assertAlmostEquals(end_flows[cont], test_flows[cont], 4)

        # PRESSURE CHECK
        test_press = [0, 0, 0, 0, 30.016, 7.383]
        for cont in range(node_count):
            cur_pressure = problem.get_nodes()[cont].get_pressure('psi')
            self.assertAlmostEquals(cur_pressure, test_press[cont], 3)


if __name__ == '__main__':
    unittest.main()
