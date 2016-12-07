from nodes import ConnectionNode
import numpy as np
import random


class PNetwork(object):
    def __init__(self):
        self.net_nodes = []
        self.net_pipes = []
        self._active_nodes = []

    def add_node(self, node):
        self.net_nodes.append(node)
        if isinstance(node, ConnectionNode):
            self._active_nodes.append(len(self.get_nodes()) - 1)

    def get_nodes(self):
        return self.net_nodes

    def add_pipe(self, pipe):
        self.net_pipes.append(pipe)

    def get_pipes(self):
        return self.net_pipes

    def get_node_index_by_name(self, name):
        cont = 0
        for node in self.get_nodes():
            if node.name == name:
                return cont
        cont += 1
        raise IndexError

    def get_pipe_index_by_name(self, name):
        cont = 0
        for pipe in self.get_pipes():
            if pipe.name == name:
                return cont
        cont += 1
        raise IndexError

    def connect_node_upstream_pipe(self, node_index, pipe_index):
        node = self.get_nodes()[node_index]
        pipe = self.get_pipes()[pipe_index]
        node.set_input_pipe(pipe)
        pipe.output_node = node

    def connect_node_downstream_pipe(self, node_index, pipe_index):
        node = self.get_nodes()[node_index]
        pipe = self.get_pipes()[pipe_index]
        node.set_output_pipe(pipe)
        pipe.input_node = node

    def get_active_nodes(self):
        if not self._active_nodes:
            cont = 0
            for node in self.get_nodes():
                if isinstance(node, ConnectionNode):
                    self._active_nodes.append(cont)
                cont += 1
        return self._active_nodes

    def get_problem_size(self):
        return len(self._active_nodes)

    def set_node_name(self, index, name):
        for node in self.net_nodes:
            if node.name == name:
                raise IndexError
        self.net_nodes[index].name = name

    def set_pipe_name(self, index, name):
        for pipe in self.net_pipes:
            if pipe.name == name:
                raise IndexError
        self.net_pipes[index].name = name

    def f_equations(self):
        size = self.get_problem_size()
        resp = np.zeros([size, 1])
        for active_node in self.get_active_nodes():
            partial_flow = 0
            f_node = self.get_nodes()[active_node]
            for pipe in f_node.get_input_pipes():
                partial_flow += pipe.get_gpm_flow()
            for pipe in f_node.get_output_pipes():
                partial_flow -= pipe.get_gpm_flow()
            resp[self.get_active_nodes().index(active_node)][0] = partial_flow
        return resp

    def cell_jacob(self, row_index, col_index):
        partial_jac = 0
        evaluated_node = self.get_nodes()[col_index]
        for connected_pipe in self.get_nodes()[row_index].get_input_pipes():
            partial_jac += connected_pipe.get_node_jacobian(evaluated_node)
        for connected_pipe in self.get_nodes()[row_index].get_output_pipes():
            partial_jac -= connected_pipe.get_node_jacobian(evaluated_node)
        return partial_jac

    def first_guess(self):
        max_energy = 95
        min_energy = 90
        guess = np.zeros([self.get_problem_size(), 1])
        actives = self.get_active_nodes()
        for cont in range(self.get_problem_size()):
            guess[cont][0] = random.uniform(min_energy, max_energy)
            self.get_nodes()[actives[cont]].set_energy(guess[cont][0], 'psi')
        return guess

    def solve_shit(self):
        problem_size = self.get_problem_size()
        jacobian = np.zeros([problem_size, problem_size])
        iteration = 0
        active_nodes = self.get_active_nodes()
        energy_vector = self.first_guess()

        while iteration < 5:
            for cont1 in range(problem_size):
                row_index = active_nodes[cont1]
                for cont2 in range(problem_size):
                    col_index = active_nodes[cont2]
                    jacobian[cont1][cont2] = self.cell_jacob(row_index,
                                                             col_index)

            f_results = self.f_equations()
            delta = -np.linalg.solve(jacobian, f_results)
            energy_vector = np.add(energy_vector, delta)
            meter_energy = []
            for active_node_index in range(problem_size):
                this_node = self.get_nodes()[active_nodes[active_node_index]]
                this_node.set_energy(energy_vector[active_node_index][0], 'psi')
                meter_energy.append(this_node.get_energy('mH2O'))
            iteration += 1
