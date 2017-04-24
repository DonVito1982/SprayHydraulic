import unittest

from pipe_network import PNetwork
from edges import Pipe, Nozzle
from nodes import ConnectionNode, EndNode, InputNode
from solvers import UserSolver, RemoteNozzleSolver


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
        self.check_4_reservoir_flow()
        self.check_4_reservoir_pressures()

    def set_4_reservoir_network(self):
        self.pipe_network = PNetwork()
        self.set_4_reservoir_nodes()
        self.set_4_reservoir_edges()
        self.set_4_reservoir_connectivity()

    def set_4_reservoir_nodes(self):
        elevations = [100, 85, 65, 65, 70, 70]
        self.set_4_reservoir_end_nodes(elevations)
        self.set_4_reservoir_connection_nodes(elevations)

    def set_4_reservoir_connection_nodes(self, elevations):
        node_count = len(elevations)
        end_count = 4
        for node_index in range(end_count, node_count):
            cur_node = ConnectionNode()
            cur_node.set_pressure(0, 'psi')
            cur_node.set_elevation(elevations[node_index], 'm')
            cur_node.name = node_index
            self.pipe_network.add_node(cur_node)

    def set_4_reservoir_end_nodes(self, elevations):
        for cont in range(4):
            cur_node = EndNode()
            cur_node.set_elevation(elevations[cont], 'm')
            cur_node.name = cont
            self.pipe_network.add_node(cur_node)

    def set_4_reservoir_edges(self):
        lengths = [1000, 1200, 900, 500, 600]
        inner_diameters = [10.02, 7.981, 7.981, 6.065, 6.065]
        pipe_count = len(lengths)
        for pipe_index in range(pipe_count):
            cur_pipe = Pipe()
            cur_pipe.set_length(lengths[pipe_index], 'm')
            cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
            cur_pipe.set_c_coefficient(100)
            cur_pipe.name = pipe_index
            self.pipe_network.add_edge(cur_pipe)

    def check_4_reservoir_flow(self):
        number_of_edges = len(self.pipe_network.get_edges())
        test_flows = [1041.6261, -318.1786, 723.44747, 379.51588, 343.9316]
        for cont in range(number_of_edges):
            cur_edge = self.pipe_network.edge_at(cont)
            cur_flow = cur_edge.get_gpm_flow()
            self.assertAlmostEquals(cur_flow, test_flows[cont], 4)

    def check_4_reservoir_pressures(self):
        number_of_nodes = len(self.pipe_network.get_nodes())
        test_press = [0, 0, 0, 0, 27.4694, 6.39082]
        for cont in range(number_of_nodes):
            cur_node = self.pipe_network.node_at(cont)
            cur_pressure = cur_node.get_pressure('psi')
            self.assertAlmostEquals(cur_pressure, test_press[cont], 3)

    def set_4_reservoir_connectivity(self):
        self.connect_edge_to_up_node_and_down_node(2, 4, 5)
        self.connect_edge_to_up_node_and_down_node(1, 1, 4)
        self.connect_edge_to_up_node_and_down_node(0, 0, 4)
        self.connect_edge_to_up_node_and_down_node(3, 5, 2)
        self.connect_edge_to_up_node_and_down_node(4, 5, 3)

    def test_reservoir_nozzle(self):
        self.set_reservoir_nozzles_network()
        user_defined = UserSolver(self.pipe_network)
        user_defined.solve_system()
        self.check_reservoir_nozzle_nodes_energy()
        self.check_reservoir_nozzle_edge_flows()

    def set_reservoir_nozzles_network(self):
        self.pipe_network = PNetwork()
        self.set_reservoir_nozzles_nodes()
        self.set_reservoir_nozzles_pipes()
        self.set_reservoir_nozzle_nozzles()
        self.set_nozzle_network_connectivity()

    def set_reservoir_nozzles_nodes(self):
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

    def set_reservoir_nozzles_pipes(self):
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

    def set_reservoir_nozzle_nozzles(self):
        for index in range(5, 8):
            cur_pipe = Nozzle()
            cur_pipe.set_factor(2, 'gpm/psi^0.5')
            cur_pipe.name = index
            self.pipe_network.add_edge(cur_pipe)

    def set_nozzle_network_connectivity(self):
        self.connect_edge_to_up_node_and_down_node(0, 0, 2)
        self.connect_edge_to_up_node_and_down_node(1, 1, 2)
        self.connect_edge_to_up_node_and_down_node(2, 2, 3)
        self.connect_edge_to_up_node_and_down_node(5, 3, 5)
        self.connect_edge_to_up_node_and_down_node(3, 3, 4)
        self.connect_edge_to_up_node_and_down_node(4, 4, 8)
        self.connect_edge_to_up_node_and_down_node(6, 4, 6)
        self.connect_edge_to_up_node_and_down_node(7, 8, 7)

    def check_reservoir_nozzle_nodes_energy(self):
        node_psi_energies = [42.6591, 49.76896, 41.85877, 39.99165, 37.31384,
                             0, 0, 0, 36.57881]
        for node_index in range(len(self.pipe_network.get_nodes())):
            cur_node = self.pipe_network.get_nodes()[node_index]
            cur_energy = cur_node.get_energy('psi')
            self.assertAlmostEqual(cur_energy, node_psi_energies[node_index], 4)

    def check_reservoir_nozzle_edge_flows(self):
        edge_flows = [9.80918, 27.1517, 36.96088, 24.31309, 12.09608,
                      12.64779, 12.21701, 12.09608]
        for edge_index in range(8):
            cur_flow = self.pipe_network.edge_at(edge_index).get_gpm_flow()
            self.assertAlmostEqual(cur_flow, edge_flows[edge_index], 4)

    def connect_edge_to_up_node_and_down_node(self, edge_index, up_node,
                                              down_node):
        self.pipe_network.connect_node_downstream_edge(up_node, edge_index)
        self.pipe_network.connect_node_upstream_edge(down_node, edge_index)

    def test_remote_nozzle_with_3_nozzle_solution(self):
        self.set_remote_3_nozzles_network()
        three_nozzles = RemoteNozzleSolver(self.pipe_network)
        three_nozzles.solve_system()
        self.check_3_nozzles_nodes_pressure()
        self.check_3_nozzles_edges_gpm_flow()

    def set_remote_3_nozzles_network(self):
        self.pipe_network = PNetwork()
        self.set_remote_3_nozzles_nodes()
        self.set_remote_nozzles_pipes()
        self.describe_nozzles()
        self.set_remote_nozzle_connectivity()

    def set_remote_3_nozzles_nodes(self):
        system_nodes = ['i', 'c', 'c', 'c', 'e', 'e', 'e']
        elevations = [0, 0, 0, 0, 0, 0, 0]
        for index in range(len(system_nodes)):
            if system_nodes[index] == 'e':
                cur_node = EndNode()
            if system_nodes[index] == 'c':
                cur_node = ConnectionNode()
                cur_node.set_pressure(0, 'psi')
            if system_nodes[index] == 'i':
                cur_node = InputNode()
            cur_node.set_elevation(elevations[index], 'm')
            cur_node.name = "%s%d" % (system_nodes[index], index)
            self.pipe_network.add_node(cur_node)

    def set_remote_nozzles_pipes(self):
        for pipe_index in range(3):
            cur_pipe = Pipe()
            cur_pipe.set_length(2, 'm')
            cur_pipe.set_inner_diam(.957, 'in')
            cur_pipe.set_c_coefficient(100)
            self.pipe_network.add_edge(cur_pipe)
            self.pipe_network.set_pipe_name(pipe_index, pipe_index)

    def describe_nozzles(self):
        for edge_index in range(3, 6):
            cur_pipe = Nozzle()
            cur_pipe.set_factor(2, 'gpm/psi^0.5')
            cur_pipe.set_required_pressure(25, 'psi')
            self.pipe_network.add_edge(cur_pipe)
            self.pipe_network.set_pipe_name(edge_index, edge_index)

    def set_remote_nozzle_connectivity(self):
        self.connect_edge_to_up_node_and_down_node(0, 0, 1)
        self.connect_edge_to_up_node_and_down_node(1, 1, 2)
        self.connect_edge_to_up_node_and_down_node(2, 2, 3)
        self.connect_edge_to_up_node_and_down_node(3, 1, 4)
        self.connect_edge_to_up_node_and_down_node(4, 2, 5)
        self.connect_edge_to_up_node_and_down_node(5, 3, 6)

    def check_3_nozzles_nodes_pressure(self):
        checked_pressures = [31.4923, 27.3997, 25.5167, 25]
        for cont in range(4):
            pressure = self.pipe_network.node_at(cont).get_pressure('psi')
            self.assertAlmostEqual(pressure, checked_pressures[cont], 4)

    def check_3_nozzles_edges_gpm_flow(self):
        checked_flows = [30.5718, 20.1028, 10, 10.4689, 10.1028, 10]
        edges = self.pipe_network.get_edges()
        for cont in range(len(edges)):
            cur_flow = edges[cont].get_gpm_flow()
            self.assertAlmostEqual(cur_flow, checked_flows[cont], 4)


class NozzleNetworkTest(unittest.TestCase):
    def setUp(self):
        self.nozzle_network = PNetwork()
        self.input_node = InputNode()
        self.input_node.set_elevation(10, 'm')
        self.input_node.name = 'input'
        self.nozzle0 = Nozzle()
        self.nozzle0.name = "nozzle0"
        self.nozzle0.set_factor(2, 'gpm/psi^0.5')
        self.nozzle0.set_required_pressure(25, 'psi')
        self.end_node0 = EndNode()
        self.end_node0.set_elevation(10, 'm')
        self.end_node0.name = 'end'

    def test_delete_nozzle(self):
        self.set_single_nozzle()
        nozzle2 = Nozzle()
        nozzle2.name = "nozzle2"
        self.nozzle_network.add_edge(nozzle2)
        self.nozzle_network.connect_node_downstream_edge(0, 1)
        nozzle_solver = RemoteNozzleSolver(self.nozzle_network)
        nozzle_solver.hold_nozzle(0)
        self.assertEqual(len(self.nozzle_network.get_edges()), 1)
        self.assert_nozzle_deletion(nozzle2, nozzle_solver)
        nozzle_solver.reinsert_nozzle()
        self.assert_nozzle_insertion()

    def assert_nozzle_insertion(self):
        self.assertEqual(len(self.nozzle_network.get_edges()), 2)
        self.assertTrue(self.nozzle_network.edge_at(0) is self.nozzle0)
        output_flow = self.nozzle_network.node_at(0).get_output_flow('gpm')
        self.assertEqual(output_flow, 0)

    def assert_nozzle_deletion(self, nozzle2, nozzle_solver):
        self.assertEqual(nozzle_solver.detached_nozzle_index, 0)
        input_node = self.nozzle_network.node_at(0)
        self.assertEqual(input_node.get_output_pipes(), [nozzle2])
        self.assertEqual(input_node.get_output_flow('gpm'), 10)
        self.assertEqual(input_node.get_pressure('psi'), 25)

    def test_single_nozzle(self):
        self.set_single_nozzle()
        nozzle_solver = RemoteNozzleSolver(self.nozzle_network)
        nozzle_solver.solve_system()
        self.check_nozzle_flow(0, 10)
        self.assertAlmostEqual(self.input_node.get_output_flow('gpm'), -10)
        self.nozzle0.set_factor(3, 'gpm/psi^0.5')
        nozzle_solver.solve_system()
        self.check_nozzle_flow(0, 15)
        self.assertAlmostEqual(self.input_node.get_output_flow('gpm'), -15)
        self.assertEqual(self.input_node.get_pressure('psi'), 25)

    def check_nozzle_flow(self, nozzle_index, vol_flow):
        nozzle = self.nozzle_network.edge_at(nozzle_index)
        self.assertAlmostEqual(nozzle.get_vol_flow('gpm'), vol_flow)

    def set_single_nozzle(self):
        self.nozzle_network.add_node(self.input_node)
        self.nozzle_network.add_node(self.end_node0)
        self.nozzle_network.add_edge(self.nozzle0)
        self.nozzle_network.connect_node_downstream_edge(0, 0)
        self.nozzle_network.connect_node_upstream_edge(1, 0)

    def test_two_nozzles(self):
        self.set_single_nozzle()
        end_node1 = EndNode()
        end_node1.set_elevation(10, 'm')
        self.nozzle_network.add_node(end_node1)
        nozzle1 = Nozzle()
        nozzle1.set_factor(1, 'gpm/psi^0.5')
        nozzle1.set_required_pressure(36, 'psi')
        self.nozzle_network.add_edge(nozzle1)
        self.nozzle_network.connect_node_downstream_edge(0, 1)
        self.nozzle_network.connect_node_upstream_edge(2, 1)
        nozzle_solver = RemoteNozzleSolver(self.nozzle_network)
        nozzle_solver.solve_system()
        self.check_nozzle_flow(1, 6)
        self.check_nozzle_flow(0, 12)
        self.assertEqual(self.input_node.get_output_flow('gpm'), -18)
        self.nozzle0.set_required_pressure(49, 'psi')
        nozzle_solver.solve_system()
        self.assertAlmostEqual(self.input_node.get_output_flow('gpm'), -21)

    def test_input_index_not_0(self):
        self.nozzle_network.add_node(self.end_node0)
        self.nozzle_network.add_node(self.input_node)
        self.nozzle_network.add_edge(self.nozzle0)
        self.nozzle_network.connect_node_downstream_edge(1, 0)
        self.nozzle_network.connect_node_upstream_edge(0, 0)
        nozzle_solver = RemoteNozzleSolver(self.nozzle_network)
        nozzle_solver.solve_system()
        self.check_nozzle_flow(0, 10)
        self.assertAlmostEqual(self.input_node.get_output_flow('gpm'), -10)
        self.nozzle0.set_factor(3, 'gpm/psi^0.5')
        nozzle_solver.solve_system()
        self.check_nozzle_flow(0, 15)
        self.assertAlmostEqual(self.input_node.get_output_flow('gpm'), -15)
        self.assertEqual(self.input_node.get_pressure('psi'), 25)

    def test_double_input(self):
        self.set_single_nozzle()
        input2 = InputNode()
        self.assertRaises(AttributeError,
                          lambda: self.nozzle_network.add_node(input2))


if __name__ == '__main__':
    unittest.main()
