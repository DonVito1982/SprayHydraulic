import unittest

from pipes import Pipe, Nozzle
from nodes import EndNode, ConnectionNode
from pipe_network import PNetwork


class ExampleTests(unittest.TestCase):
    def test_four_reservoir(self):
        elevations = [100, 85, 65, 65, 70, 70]
        names = [0, 1, 2, 3, 4, 5]
        res_problem = PNetwork()

        # SET END NODES
        for cont in range(4):
            cur_node = EndNode()
            cur_node.set_elevation(elevations[cont], 'm')
            cur_node.name = names[cont]
            res_problem.add_node(cur_node)

        # SET CONNECTION NODES
        node_count = len(elevations)
        end_count = 4

        for node_index in range(end_count, node_count):
            cur_node = ConnectionNode()
            cur_node.set_pressure(0, 'psi')
            cur_node.set_elevation(elevations[node_index], 'm')
            cur_node.name = names[node_index]
            res_problem.add_node(cur_node)

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
            res_problem.add_edge(cur_pipe)

        # SET CONNECTIVITY
        res_problem.connect_node_downstream_edge(4, 2)
        res_problem.connect_node_upstream_edge(4, 1)
        res_problem.connect_node_upstream_edge(4, 0)
        res_problem.connect_node_downstream_edge(0, 0)
        res_problem.connect_node_downstream_edge(1, 1)
        res_problem.connect_node_upstream_edge(5, 2)
        res_problem.connect_node_downstream_edge(5, 3)
        res_problem.connect_node_downstream_edge(5, 4)
        res_problem.connect_node_upstream_edge(2, 3)
        res_problem.connect_node_upstream_edge(3, 4)

        res_problem.solve_system()

        end_flows = []

        for cont5 in range(pipe_count):
            end_flows.append(res_problem.get_edges()[cont5].get_gpm_flow())

        # FLOW CHECK
        test_flows = [1135.2443, -383.5847, 751.6596, 394.3143, 357.3453]
        for cont in range(pipe_count):
            self.assertAlmostEquals(end_flows[cont], test_flows[cont], 4)

        # PRESSURE CHECK
        test_press = [0, 0, 0, 0, 30.016, 7.383]
        for cont in range(node_count):
            cur_pressure = res_problem.get_nodes()[cont].get_pressure('psi')
            self.assertAlmostEquals(cur_pressure, test_press[cont], 3)

    def test_reservoir_nozzle(self):
        noz_problem = PNetwork()

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
            noz_problem.add_node(cur_node)

        # SET PIPES
        lengths = [100, 150, 20, 2, 2]
        inner_diameters = [1.939, 1.939, 1.939, .957, .957]
        pipe_count = len(lengths)

        for pipe_index in range(pipe_count):
            cur_pipe = Pipe()
            cur_pipe.set_length(lengths[pipe_index], 'm')
            cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
            cur_pipe.set_c_coefficient(100)
            noz_problem.add_edge(cur_pipe)
            noz_problem.set_pipe_name(pipe_index, pipe_index)

        #   SET NOZZLES
        for index in range(5, 8):
            cur_pipe = Nozzle()
            cur_pipe.set_factor(2, 'gpm/psi^0.5')
            cur_pipe.name = index
            noz_problem.add_edge(cur_pipe)

        # SET CONNECTIVITY
        noz_problem.connect_node_downstream_edge(0, 0)
        noz_problem.connect_node_downstream_edge(1, 1)
        noz_problem.connect_node_downstream_edge(2, 2)
        noz_problem.connect_node_upstream_edge(2, 0)
        noz_problem.connect_node_upstream_edge(2, 1)
        noz_problem.connect_node_downstream_edge(3, 5)
        noz_problem.connect_node_downstream_edge(3, 3)
        noz_problem.connect_node_upstream_edge(3, 2)
        noz_problem.connect_node_downstream_edge(4, 4)
        noz_problem.connect_node_downstream_edge(4, 6)
        noz_problem.connect_node_upstream_edge(4, 3)
        noz_problem.connect_node_upstream_edge(5, 5)
        noz_problem.connect_node_upstream_edge(6, 6)
        noz_problem.connect_node_upstream_edge(7, 7)
        noz_problem.connect_node_downstream_edge(8, 7)
        noz_problem.connect_node_upstream_edge(8, 4)

        noz_problem.solve_system()

        node_psi_energies = [42.6689, 49.7803, 41.8689, 40.0016, 37.3237,
                             0, 0, 0, 36.5887]
        for node_index in range(len(elevations)):
            cur_energy = noz_problem.get_nodes()[node_index].get_energy('psi')
            self.assertAlmostEqual(cur_energy, node_psi_energies[node_index], 4)

        edge_flows = [9.8088, 27.1569, 36.9657, 24.3163, 12.0977,
                      12.6494, 12.2186, 12.0977]
        for edge_index in range(8):
            cur_flow = noz_problem.get_edges()[edge_index].get_gpm_flow()
            self.assertAlmostEqual(cur_flow, edge_flows[edge_index], 4)


if __name__ == '__main__':
    unittest.main()
