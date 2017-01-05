from pipes import ConnectionNode
import numpy as np
import random


class PNetwork(object):
    def __init__(self):
        self.net_nodes = []
        self.net_edges = []
        self._active_nodes = []
        self.jacobian = None
        self.size = None

    def add_node(self, node):
        self.net_nodes.append(node)

    def get_nodes(self):
        return self.net_nodes

    def add_edge(self, edge):
        self.net_edges.append(edge)

    def get_edges(self):
        return self.net_edges

    def get_node_index_by_name(self, name):
        cont = 0
        for node in self.get_nodes():
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
        node = self.get_nodes()[node_index]
        edge = self.get_edges()[edge_index]
        node.set_input_pipe(edge)
        edge.output_node = node

    def connect_node_downstream_edge(self, node_index, edge_index):
        node = self.get_nodes()[node_index]
        edge = self.get_edges()[edge_index]
        node.set_output_pipe(edge)
        edge.input_node = node

    def _set_active_nodes(self):
        self._active_nodes = []
        node_count = 0
        for node in self.get_nodes():
            if isinstance(node, ConnectionNode):
                self._active_nodes.append(node_count)
            node_count += 1

    def get_active_nodes(self):
        self._set_active_nodes()
        return self._active_nodes

    def get_problem_size(self):
        self._set_active_nodes()
        return len(self._active_nodes)

    def set_node_name(self, index, name):
        for node in self.net_nodes:
            if node.name == name:
                raise IndexError
        self.net_nodes[index].name = name

    def set_pipe_name(self, index, name):
        for pipe in self.net_edges:
            if pipe.name == name:
                raise IndexError
        self.net_edges[index].name = name

    def f_equations(self):
        size = self.get_problem_size()
        resp = np.zeros([size, 1])
        self._set_active_nodes()
        for active_node in self._active_nodes:
            partial_flow = 0
            f_node = self.get_nodes()[active_node]
            for pipe in f_node.get_input_pipes():
                partial_flow += pipe.get_gpm_flow()
            for pipe in f_node.get_output_pipes():
                partial_flow -= pipe.get_gpm_flow()
            resp[self._active_nodes.index(active_node)][0] = partial_flow
        return resp

    def _cell_jacob(self, row_index, col_index):
        partial_jac = 0
        evaluated_node = self.get_nodes()[col_index]
        for connected_pipe in self.get_nodes()[row_index].get_input_pipes():
            partial_jac += connected_pipe.get_node_jacobian(evaluated_node)
        for connected_pipe in self.get_nodes()[row_index].get_output_pipes():
            partial_jac -= connected_pipe.get_node_jacobian(evaluated_node)
        return partial_jac

    def first_guess(self):
        max_energy = self._get_max_energy()
        # print max_energy
        min_energy = self._get_min_energy()
        # print min_energy
        guess = np.zeros([self.get_problem_size(), 1])
        for cont in range(self.get_problem_size()):
            guess[cont][0] = random.uniform(min_energy, max_energy)
            cur_node = self.get_nodes()[self._active_nodes[cont]]
            cur_node.set_energy(guess[cont][0], 'psi')
        return guess

    def fill_jacobian(self):
        for cont1 in range(self.size):
            row_index = self._active_nodes[cont1]
            for cont2 in range(self.size):
                col_index = self._active_nodes[cont2]
                self.jacobian[cont1][cont2] = self._cell_jacob(row_index,
                                                               col_index)

    def solve_system(self):
        self.size = self.get_problem_size()
        self.jacobian = np.zeros([self.size, self.size])
        self._set_active_nodes()
        initial_guess = self.first_guess()
        self._iterate(initial_guess)

    def _iterate(self, energy_vector):
        iteration = 0
        f_results = self.f_equations()
        while not self.has_converged(f_results):
            self.fill_jacobian()
            f_results = self.f_equations()
            delta = -np.linalg.solve(self.jacobian, f_results)
            energy_vector = np.add(energy_vector, delta)
            self.update_energies(energy_vector)
            # self._inspect(energy_vector)
            iteration += 1
        # print iteration

    def has_converged(self, vector):
        deviation = 0
        for cont in range(self.size):
            deviation += abs(vector[cont][0])
        return deviation < 1e-4

    def _inspect(self, vector):
        format_string = ""
        energies = []
        for item in range(self.size):
            format_string += "%8.4f  "
            energies.append(vector[item][0])
        print format_string % tuple(energies)

    def update_energies(self, energy_vector):
        for active_index in range(self.size):
            this_node = self.get_nodes()[self._active_nodes[active_index]]
            this_node.set_energy(energy_vector[active_index][0], 'psi')

    def _get_max_energy(self):
        max_energy = self.get_nodes()[0].get_energy('psi')
        for node in self.get_nodes():
            max_energy = max(max_energy, node.get_energy('psi'))
        return max_energy

    def _get_min_energy(self):
        min_energy = self.get_nodes()[0].get_energy('psi')
        for node in self.get_nodes():
            min_energy = min(min_energy, node.get_energy('psi'))
        return min_energy
