import unittest

from pipe_network import PNetwork
from edges import Pipe, Nozzle
from nodes import ConnectionNode, EndNode
from solvers import UserSolver


class UserDefinedNetworks(unittest.TestCase):
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

    def test_set_active_nodes(self):
        user_defined = UserSolver(self.four_res)
        self.assertEqual(user_defined.get_active_nodes(), [1])
        node1 = EndNode()
        node2 = ConnectionNode()
        self.four_res.add_node(node1)
        self.four_res.add_node(node2)
        self.assertEqual(user_defined.get_active_nodes(), [1, 4])
        user_defined.prepare_solving_conditions()
        self.assertEqual(user_defined.size, 2)

    def test_reset_active_nodes(self):
        user_defined = UserSolver(self.four_res)
        node_list = user_defined.get_active_nodes()
        self.assertEqual(len(node_list), 1)
        node1 = ConnectionNode()
        self.four_res.add_node(node1)
        self.assertEqual(user_defined.get_active_nodes(), [1, 3])

    def test_f_equations(self):
        user_defined = UserSolver(self.four_res)
        self.node1.set_elevation(10, 'm')
        self.node1.set_energy(25, 'mH2O')
        self.reserve_node.set_elevation(27, 'm')
        self.nozzle_end.set_elevation(23, 'm')
        self.nozzle0.set_factor(1.2, 'gpm/psi^0.5')
        user_defined.prepare_solving_conditions()
        flow0 = self.pipe0.get_gpm_flow() - self.nozzle0.get_gpm_flow()
        self.assertEqual(float(user_defined.f_equations()), flow0)


class ExampleTests(unittest.TestCase):
    def test_four_reservoir(self):
        self.set_4_reservoir_network()
        user_solve = UserSolver(self.pipe_network)
        user_solve.solve_system()
        self.check_flow()
        self.check_pressures()

    def test_reservoir_nozzle(self):
        self.set_reservoir_nozzles_network()
        user_defined = UserSolver(self.pipe_network)
        user_defined.solve_system()
        self.check_nozzle_nodes_energy()
        self.check_nozzle_flows()

    def check_nozzle_flows(self):
        edge_flows = [9.8088, 27.1569, 36.9657, 24.3163, 12.0977,
                      12.6494, 12.2186, 12.0977]
        for edge_index in range(8):
            cur_flow = self.pipe_network.get_edges()[edge_index].get_gpm_flow()
            self.assertAlmostEqual(cur_flow, edge_flows[edge_index], 4)

    def check_nozzle_nodes_energy(self):
        node_psi_energies = [42.6689, 49.7803, 41.8689, 40.0016, 37.3237,
                             0, 0, 0, 36.5887]
        for node_index in range(len(self.pipe_network.get_nodes())):
            cur_node = self.pipe_network.get_nodes()[node_index]
            cur_energy = cur_node.get_energy('psi')
            self.assertAlmostEqual(cur_energy, node_psi_energies[node_index], 4)

    def set_reservoir_nozzles_network(self):
        self.pipe_network = PNetwork()
        # SET NODES
        system_nodes = ['e', 'e', 'c', 'c', 'c', 'e', 'e', 'e', 'c']
        elevations = [30, 35, 25, 0, 0, 0, 0, 0, 0]
        for index in range(len(system_nodes)):
            if system_nodes[index] == 'e':
                cur_node = EndNode()
            if system_nodes[index] == 'c':
                cur_node = ConnectionNode()
                cur_node.set_pressure(0, 'psi')
            cur_node.set_elevation(elevations[index], 'm')
            cur_node.name = index
            self.pipe_network.add_node(cur_node)

        # SET PIPES
        lengths = [100, 150, 20, 2, 2]
        inner_diameters = [1.939, 1.939, 1.939, .957, .957]
        pipe_count = len(lengths)
        for pipe_index in range(pipe_count):
            cur_pipe = Pipe()
            cur_pipe.set_length(lengths[pipe_index], 'm')
            cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
            cur_pipe.set_c_coefficient(100)
            self.pipe_network.add_edge(cur_pipe)
            self.pipe_network.set_pipe_name(pipe_index, pipe_index)

        # SET NOZZLES
        for index in range(5, 8):
            cur_pipe = Nozzle()
            cur_pipe.set_factor(2, 'gpm/psi^0.5')
            cur_pipe.name = index
            self.pipe_network.add_edge(cur_pipe)

        self.set_nozzle_network_connectivity()

    def set_nozzle_network_connectivity(self):
        self.connect_edge_to_up_node_and_down_node(0, 0, 2)
        self.connect_edge_to_up_node_and_down_node(1, 1, 2)
        self.connect_edge_to_up_node_and_down_node(2, 2, 3)
        self.connect_edge_to_up_node_and_down_node(5, 3, 5)
        self.connect_edge_to_up_node_and_down_node(3, 3, 4)
        self.connect_edge_to_up_node_and_down_node(4, 4, 8)
        self.connect_edge_to_up_node_and_down_node(6, 4, 6)
        self.connect_edge_to_up_node_and_down_node(7, 8, 7)

    def set_4_reservoir_network(self):
        self.pipe_network = PNetwork()
        elevations = [100, 85, 65, 65, 70, 70]
        names = [0, 1, 2, 3, 4, 5]
        # SET END NODES
        for cont in range(4):
            cur_node = EndNode()
            cur_node.set_elevation(elevations[cont], 'm')
            cur_node.name = names[cont]
            self.pipe_network.add_node(cur_node)

        # SET CONNECTION NODES
        node_count = len(elevations)
        end_count = 4
        for node_index in range(end_count, node_count):
            cur_node = ConnectionNode()
            cur_node.set_pressure(0, 'psi')
            cur_node.set_elevation(elevations[node_index], 'm')
            cur_node.name = names[node_index]
            self.pipe_network.add_node(cur_node)
        self.set_edges()
        self.set_connectivity()

    def set_edges(self):
        lengths = [1000, 1200, 900, 500, 600]
        inner_diameters = [10.75, 7.981, 7.981, 6.065, 6.065]
        pipe_count = len(lengths)
        for pipe_index in range(pipe_count):
            cur_pipe = Pipe()
            cur_pipe.set_length(lengths[pipe_index], 'm')
            cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
            cur_pipe.set_c_coefficient(100)
            cur_pipe.name = pipe_index
            self.pipe_network.add_edge(cur_pipe)

    def set_connectivity(self):
        self.connect_edge_to_up_node_and_down_node(2, 4, 5)
        self.connect_edge_to_up_node_and_down_node(1, 1, 4)
        self.connect_edge_to_up_node_and_down_node(0, 0, 4)
        self.connect_edge_to_up_node_and_down_node(3, 5, 2)
        self.connect_edge_to_up_node_and_down_node(4, 5, 3)

    def connect_edge_to_up_node_and_down_node(self, edge_index, up_node,
                                              down_node):
        self.pipe_network.connect_node_downstream_edge(up_node, edge_index)
        self.pipe_network.connect_node_upstream_edge(down_node, edge_index)

    def check_pressures(self):
        number_of_nodes = len(self.pipe_network.get_nodes())
        test_press = [0, 0, 0, 0, 30.016, 7.383]
        for cont in range(number_of_nodes):
            cur_node = self.pipe_network.get_nodes()[cont]
            cur_pressure = cur_node.get_pressure('psi')
            self.assertAlmostEquals(cur_pressure, test_press[cont], 3)

    def check_flow(self):
        number_of_edges = len(self.pipe_network.get_edges())
        test_flows = [1135.2443, -383.5847, 751.6596, 394.3143, 357.3453]
        for cont in range(number_of_edges):
            cur_edge = self.pipe_network.get_edges()[cont]
            cur_flow = cur_edge.get_gpm_flow()
            self.assertAlmostEquals(cur_flow, test_flows[cont], 4)

if __name__ == '__main__':
    unittest.main()
