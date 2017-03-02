from edges import Nozzle
from nodes import ConnectionNode, InputNode, EndNode
from math import sqrt

import numpy as np
import random


class PNetwork(object):
    def __init__(self):
        self._net_nodes = []
        self._net_edges = []
        self._deleted_edge = None
        self.detached_nozzle_index = None
        self.unplugged_node_index = None

    def add_node(self, node):
        assert node not in self._net_nodes
        if isinstance(node, InputNode):
            for each_node in self._net_nodes:
                if isinstance(each_node, InputNode):
                    raise AttributeError
        self._net_nodes.append(node)

    def get_nodes(self):
        return self._net_nodes

    def add_edge(self, edge):
        assert edge not in self._net_edges
        self._net_edges.append(edge)

    def get_edges(self):
        return self._net_edges

    def get_node_index_by_name(self, name):
        cont = 0
        for node in self._net_nodes:
            if node.name == name:
                return cont
            cont += 1
        raise IndexError

    def get_edge_index_by_name(self, name):
        cont = 0
        for edge in self.get_edges():
            if edge.name == name:
                return cont
            cont += 1
        raise IndexError

    def connect_node_upstream_edge(self, node_index, edge_index):
        node = self._net_nodes[node_index]
        edge = self.get_edges()[edge_index]
        node.set_input_pipe(edge)
        edge.output_node = node

    def connect_node_downstream_edge(self, node_index, edge_index):
        node = self._net_nodes[node_index]
        edge = self.get_edges()[edge_index]
        node.set_output_pipe(edge)
        edge.input_node = node

    def set_node_name(self, index, name):
        for node in self._net_nodes:
            if node.name == name:
                raise IndexError
        self._net_nodes[index].name = name

    def set_pipe_name(self, index, name):
        for pipe in self._net_edges:
            if pipe.name == name:
                raise IndexError
        self._net_edges[index].name = name

    def separate_node_from_edge(self, node_index, edge_index):
        edge = self.get_edges()[edge_index]
        node = self.get_nodes()[node_index]
        if node is edge.input_node:
            self._separate_edge_from_input(edge_index, node_index)
        elif node is edge.output_node:
            self._separate_edge_from_output(edge_index, node_index)
        else:
            raise ValueError

    def _separate_edge_from_output(self, edge_index, node_index):
        connected_pipes = self.get_nodes()[node_index].get_input_pipes()
        for e_index in range(len(connected_pipes)):
            if connected_pipes[e_index] is self.get_edges()[edge_index]:
                self.get_nodes()[node_index].remove_input(e_index)
        self.get_edges()[edge_index].clear_output()

    def _separate_edge_from_input(self, edge_index, node_index):
        connected_pipes = self.get_nodes()[node_index].get_output_pipes()
        for e_index in range(len(connected_pipes)):
            separated_edge = self.get_edges()[edge_index]
            if connected_pipes[e_index] is separated_edge:
                self.get_nodes()[node_index].remove_output(e_index)
                break
        self.get_edges()[edge_index].clear_input()

    def hold_nozzle(self, noz_index):
        assert isinstance(self.get_edges()[noz_index], Nozzle)
        input_node_name = self.get_edges()[noz_index].input_node.name
        input_index = self.get_node_index_by_name(input_node_name)
        assert isinstance(self.get_nodes()[input_index], ConnectionNode)
        self._set_nozzle_output_flow(noz_index, input_index)
        self.unplugged_node_index = input_index
        self._separate_edge_from_input(noz_index, input_index)
        self.detached_nozzle_index = noz_index
        self._deleted_edge = self._net_edges.pop(noz_index)
        req_pressure = self._deleted_edge.get_required_pressure('psi')
        self.get_nodes()[input_index].set_pressure(req_pressure, 'psi')

    def _set_nozzle_output_flow(self, noz_index, node_index):
        detached_nozzle = self.get_edges()[noz_index]
        k_factor = detached_nozzle.get_factor('gpm/psi^0.5')
        pressure = detached_nozzle.get_required_pressure('psi')
        out_flow = k_factor * sqrt(pressure)
        self.get_nodes()[node_index].set_output_flow(out_flow, 'gpm')

    def reinsert_nozzle(self):
        self._net_edges.insert(self.detached_nozzle_index, self._deleted_edge)
        self._net_nodes[self.unplugged_node_index].set_output_flow(0, 'gpm')
        self.connect_node_downstream_edge(self.unplugged_node_index,
                                          self.detached_nozzle_index)
        self._deleted_edge = None
        self.detached_nozzle_index = None

    def _all_nozzles_solved(self):
        for this_nozzle_done in self._nozzle_index_solved_status_hash:
            if not this_nozzle_done[1]:
                return False
        return True

    def solve_remote_nozzle(self):
        output_gpm_flow = 0
        self.remote_nozzle_initialize()
        self._initialize_solved_nozzles()
        cont = 0
        while not self._all_nozzles_solved():
            pair = self._nozzle_index_solved_status_hash[cont]
            if not pair[1]:
                self._solve_this_one(pair[0])
                # self._solve_for_this_nozzle(pair[0])
                pair[1] = True
                self._update_solved_nozzles()
            cont += 1
        for pair in self._nozzle_index_solved_status_hash:
            output_gpm_flow -= self._net_edges[pair[0]].get_gpm_flow()
        input_index = self._search_input_index()
        self._net_nodes[input_index].set_output_flow(output_gpm_flow, 'gpm')

    def _search_input_index(self):
        for cont in range(len(self._net_nodes)):
            if isinstance(self._net_nodes[cont], InputNode):
                return cont

    def _initialize_solved_nozzles(self):
        self._nozzle_index_solved_status_hash = []
        for noz_index in range(len(self._net_edges)):
            if isinstance(self._net_edges[noz_index], Nozzle):
                self._nozzle_index_solved_status_hash.append([noz_index, False])

    def _solve_for_this_nozzle(self, nozzle_index):
        req_press = self._net_edges[nozzle_index].get_required_pressure('psi')
        self._net_edges[nozzle_index].input_node.set_pressure(req_press, 'psi')

    def _update_solved_nozzles(self):
        for pair in self._nozzle_index_solved_status_hash:
            cur_nozzle = self._net_edges[pair[0]]
            required_pressure = cur_nozzle.get_required_pressure('psi')
            if cur_nozzle.input_node.get_pressure('psi') >= required_pressure:
                pair[1] = True

    def remote_nozzle_initialize(self):
        for node in self._net_nodes:
            if isinstance(node, ConnectionNode):
                node.set_pressure(0, 'psi')

    def _solve_this_one(self, nozzle_index):
        self.hold_nozzle(nozzle_index)
        self.size = self.get_problem_size()
        self.jacobian = np.zeros([self.size, self.size])
        self._set_active_nodes_indexes()
        initial_guess = self.first_guess()
        self._iterate(initial_guess)
        self.reinsert_nozzle()

    def get_problem_size(self):
        self._set_active_nodes_indexes()
        return len(self._active_indexes)

    def _set_active_nodes_indexes(self):
        self._active_indexes = []
        node_count = 0
        for node in self.get_nodes():
            if isinstance(node, ConnectionNode):
                self._active_indexes.append(node_count)
            node_count += 1

    def first_guess(self):
        max_energy = self._get_max_energy()
        min_energy = self._get_min_energy()
        guess = np.zeros([self.get_problem_size(), 1])
        for cont in range(self.get_problem_size()):
            if self._active_indexes[cont] == self.unplugged_node_index:
                assert isinstance(self._deleted_edge, Nozzle)
                nozzle_pressure = self.get_nodes()[
                    self.unplugged_node_index].get_pressure('psi')
                nozzle_k_factor = self._deleted_edge.get_factor('gpm/psi^0.5')
                guess[cont][0] = sqrt(nozzle_pressure) * nozzle_k_factor
            else:
                guess[cont][0] = random.uniform(min_energy, max_energy)
                cur_node = self.get_nodes()[self._active_indexes[cont]]
                cur_node.set_energy(guess[cont][0], 'psi')
        return guess

    def _get_max_energy(self):
        max_energy = self.get_nodes()[0].get_energy('psi')
        for node in self.get_nodes():
            max_energy = max(max_energy, node.get_energy('psi'))
        return max_energy

    def _get_min_energy(self):
        min_energy = self.get_nodes()[0].get_energy('psi')-1
        for node in self.get_nodes():
            min_energy = min(min_energy, node.get_energy('psi'))
        return min_energy

    def _iterate(self, energy_vector):
        iteration = 0
        f_results = self.f_equations()
        while not self.has_converged(f_results):
            self.fill_jacobian()
            f_results = self.f_equations()
            delta = -np.linalg.solve(self.jacobian, f_results)
            # print iteration
            # print self.jacobian
            # print f_results
            energy_vector = np.add(energy_vector, delta)
            self._update_energies(energy_vector)
            # self._inspect(energy_vector)
            iteration += 1

    def f_equations(self):
        size = self.get_problem_size()
        resp = np.zeros([size, 1])
        self._set_active_nodes_indexes()
        for node_index in self._active_indexes:
            input_flow = self.get_node_input_flow(node_index)
            resp[self._active_indexes.index(node_index)][0] = input_flow
        return resp

    def get_node_input_flow(self, node_index):
        partial_flow = 0
        cur_node = self.get_nodes()[node_index]
        for pipe in cur_node.get_input_pipes():
            partial_flow += pipe.get_gpm_flow()
        for pipe in cur_node.get_output_pipes():
            partial_flow -= pipe.get_gpm_flow()
        partial_flow -= cur_node.get_output_flow('gpm')
        return partial_flow

    def has_converged(self, vector):
        deviation = 0
        for cont in range(self.size):
            deviation += abs(vector[cont][0])
        return deviation < 1e-4

    def fill_jacobian(self):
        for cont1 in range(self.size):
            row_index = self._active_indexes[cont1]
            is_row_input = row_index == self._search_input_index()
            for cont2 in range(self.size):
                col_index = self._active_indexes[cont2]
                if col_index == self.unplugged_node_index:
                    if is_row_input:
                        self.jacobian[cont1][cont2] = 1
                    else:
                        self.jacobian[cont1][cont2] = 0
                else:
                    self.jacobian[cont1][cont2] = self._cell_jacob(row_index,
                                                                   col_index)

    def _update_energies(self, energy_vector):
        for index in range(self.size):
            if self._active_indexes[index] == self.unplugged_node_index:
                this_node = self.get_nodes()[self._search_input_index()]
                assert isinstance(this_node, InputNode)
                this_node.set_output_flow(-energy_vector[index][0], 'gpm')
            else:
                this_node = self.get_nodes()[self._active_indexes[index]]
                this_node.set_energy(energy_vector[index][0], 'psi')

    def _cell_jacob(self, row_index, col_index):
        partial_jac = 0
        all_nodes = self.get_nodes()
        evaluated_node = all_nodes[col_index]
        for connected_pipe in all_nodes[row_index].get_input_pipes():
            partial_jac += connected_pipe.get_node_jacobian(evaluated_node)
        for connected_pipe in all_nodes[row_index].get_output_pipes():
            partial_jac -= connected_pipe.get_node_jacobian(evaluated_node)
        return partial_jac

    def _inspect(self, vector):
        format_string = ""
        energies = []
        for item in range(self.size):
            format_string += "%8.4f  "
            energies.append(vector[item][0])
        print format_string % tuple(energies)

    def show_network(self):
        print "Node Pressure"
        for node in self._net_nodes:
            if not isinstance(node, EndNode):
                print "%s: %.4f psi" % (node.name, node.get_pressure('psi'))
        print "\nEdge Volumetric Flow (psi)"
        for edge in self._net_edges:
            print "%s: %.4f gpm" % (edge.name, edge.get_gpm_flow())
