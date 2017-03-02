import random
import numpy as np

from pipe_network import PNetwork
from nodes import ConnectionNode


class UserSolver(object):
    def __init__(self, network):
        assert isinstance(network, PNetwork)
        self.network = network
        self.size = None
        self.jacobian = None

    def solve_system(self):
        self.prepare_solving_conditions()
        self._iterate(self.first_guess())

    def prepare_solving_conditions(self):
        self._set_active_nodes_indexes()
        self.size = len(self._active_indexes)
        self.jacobian = np.zeros([self.size, self.size])
        self._set_active_nodes_indexes()

    def _set_active_nodes_indexes(self):
        self._active_indexes = []
        node_count = 0
        for node in self.network.get_nodes():
            if isinstance(node, ConnectionNode):
                self._active_indexes.append(node_count)
            node_count += 1

    def first_guess(self):
        max_energy = self._get_max_energy()
        min_energy = self._get_min_energy()
        guess = np.zeros([self.size, 1])
        for cont in range(self.size):
            guess[cont][0] = random.uniform(min_energy, max_energy)
            cur_node = self.network.get_nodes()[self._active_indexes[cont]]
            cur_node.set_energy(guess[cont][0], 'psi')
        return guess

    def _get_max_energy(self):
        max_energy = self.network.get_nodes()[0].get_energy('psi')
        for node in self.network.get_nodes():
            max_energy = max(max_energy, node.get_energy('psi'))
        return max_energy

    def _get_min_energy(self):
        min_energy = self.network.get_nodes()[0].get_energy('psi')
        for node in self.network.get_nodes():
            min_energy = min(min_energy, node.get_energy('psi'))
        return min_energy

    def _iterate(self, energy_vector):
        iteration = 0
        f_results = self.f_equations()
        while not self.has_converged(f_results):
            self.fill_jacobian()
            f_results = self.f_equations()
            delta = -np.linalg.solve(self.jacobian, f_results)
            energy_vector = np.add(energy_vector, delta)
            self._update_energies(energy_vector)
            # self._inspect(energy_vector)
            iteration += 1
        # print iteration

    def f_equations(self):
        resp = np.zeros([self.size, 1])
        self._set_active_nodes_indexes()
        for node_index in self._active_indexes:
            input_flow = self.get_node_input_flow(node_index)
            resp[self._active_indexes.index(node_index)][0] = input_flow
        return resp

    def get_node_input_flow(self, node_index):
        partial_flow = 0
        cur_node = self.network.get_nodes()[node_index]
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
            for cont2 in range(self.size):
                col_index = self._active_indexes[cont2]
                self.jacobian[cont1][cont2] = self._cell_jacob(row_index,
                                                               col_index)

    def _update_energies(self, energy_vector):
        for index in range(self.size):
            this_node = self.network.get_nodes()[self._active_indexes[index]]
            this_node.set_energy(energy_vector[index][0], 'psi')

    def _cell_jacob(self, row_index, col_index):
        partial_jac = 0
        all_nodes = self.network.get_nodes()
        evaluated_node = all_nodes[col_index]
        for connected_pipe in all_nodes[row_index].get_input_pipes():
            partial_jac += connected_pipe.get_node_jacobian(evaluated_node)
        for connected_pipe in all_nodes[row_index].get_output_pipes():
            partial_jac -= connected_pipe.get_node_jacobian(evaluated_node)
        return partial_jac

    def get_active_nodes(self):
        self._set_active_nodes_indexes()
        return self._active_indexes

    def _inspect(self, vector):
        format_string = ""
        energies = []
        for item in range(self.size):
            format_string += "%8.4f  "
            energies.append(vector[item][0])
        print format_string % tuple(energies)
