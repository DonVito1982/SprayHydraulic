import random
from abc import abstractmethod, ABCMeta
from math import sqrt

import numpy as np

from edges import Nozzle
from nodes import ConnectionNode, InputNode
from pipe_network import PNetwork


class Solver(object):
    __metaclass__ = ABCMeta

    def __init__(self, network, is_inspectable=False):
        # type: (PNetwork) -> None
        assert isinstance(network, PNetwork)
        self.network = network
        self.size = None
        self.jacobian = None
        self._is_inspectable = is_inspectable
        self.active_energy_vectors = []

    @abstractmethod
    def solve_system(self):
        pass

    def get_node_input_flow(self, node_index):
        partial_flow = 0
        cur_node = self.network.node_at(node_index)
        for pipe in cur_node.get_input_pipes():
            partial_flow += pipe.calculate_gpm_flow()
        for pipe in cur_node.get_output_pipes():
            partial_flow -= pipe.calculate_gpm_flow()
        partial_flow -= cur_node.get_output_flow('gpm')
        return partial_flow

    def has_converged(self, vector):
        deviation = 0
        for cont in range(self.size):
            deviation += abs(vector[cont][0])
        return deviation < 1e-4

    def _set_active_nodes_indexes(self):
        all_nodes = self.network.get_nodes()
        self._active_indexes = [index for index in xrange(len(all_nodes))
                                if isinstance(all_nodes[index], ConnectionNode)]

    def f_equations(self):
        resp = np.zeros([self.size, 1])
        for node_index in self._active_indexes:
            input_flow = self.get_node_input_flow(node_index)
            resp[self._active_indexes.index(node_index)][0] = input_flow
        return resp

    def _cell_jacob(self, row_index, col_index):
        partial_jac = 0
        evaluated_node = self.network.node_at(col_index)
        reference_node = self.network.node_at(row_index)
        for connected_pipe in reference_node.get_input_pipes():
            partial_jac += connected_pipe.get_node_jacobian(evaluated_node)
        for connected_pipe in reference_node.get_output_pipes():
            partial_jac -= connected_pipe.get_node_jacobian(evaluated_node)
        return partial_jac

    def prepare_solving_conditions(self):
        self._set_active_nodes_indexes()
        self.size = len(self._active_indexes)
        self.jacobian = np.zeros([self.size, self.size])

    def _get_max_energy(self):
        max_energy = self.network.node_at(0).get_energy('psi')
        for node in self.network.get_nodes():
            max_energy = max(max_energy, node.get_energy('psi'))
        return max_energy

    def _get_min_energy(self):
        min_energy = self.network.node_at(0).get_energy('psi')
        for node in self.network.get_nodes():
            min_energy = min(min_energy, node.get_energy('psi'))
        return min_energy


class UserSolver(Solver):
    def __init__(self, network, is_inspectable=False):
        # type: (PNetwork) -> None
        Solver.__init__(self, network, is_inspectable)

    def solve_system(self):
        self.prepare_solving_conditions()
        self._iterate(self.first_guess())

    def first_guess(self):
        max_energy = self._get_max_energy()
        min_energy = self._get_min_energy()
        guess = np.zeros([self.size, 1])
        for cont in range(self.size):
            guess[cont][0] = random.uniform(min_energy, max_energy)
            cur_node = self.network.node_at(self._active_indexes[cont])
            cur_node.set_energy(guess[cont][0], 'psi')
        return guess

    def _iterate(self, energy_vector):
        iteration = 0
        f_results = self.f_equations()
        while not self.has_converged(f_results) and iteration < 35:
            self.fill_jacobian()
            f_results = self.f_equations()
            delta = -np.linalg.solve(self.jacobian, f_results)
            energy_vector = np.add(energy_vector, delta)
            self.feed_partial_results(energy_vector)
            self._update_energies(energy_vector)
            iteration += 1
        if self._is_inspectable:
            print iteration
            self.print_f(f_results)

    def feed_partial_results(self, vector):
        energy_vector = [pair[0] for pair in vector]
        self.active_energy_vectors.append(energy_vector)

    def print_f(self, vertical_v):
        print vertical_v
        deviation = 0
        for cont in range(self.size):
            deviation += abs(vertical_v[cont][0])
        print deviation

    def fill_jacobian(self):
        for cont1 in range(self.size):
            row_index = self._active_indexes[cont1]
            for cont2 in range(self.size):
                col_index = self._active_indexes[cont2]
                self.jacobian[cont1][cont2] = self._cell_jacob(row_index,
                                                               col_index)
        if self._is_inspectable:
            self.print_jacobian()

    def print_jacobian(self):
        # print len(self.jacobian)
        print "        ",
        for x_index in range(self.size):
            this_index = self._active_indexes[x_index]
            print "{:7}".format(self.network.node_at(this_index).name),
        print
        x_index = 0
        for row in self.jacobian:
            this_index = self._active_indexes[x_index]
            print "{:3} [".format(self.network.node_at(this_index).name),
            for elem in row:
                print "{:7.2f}".format(elem),
            print "]"
            x_index += 1
        print

    def _update_energies(self, energy_vector):
        for index in range(self.size):
            this_node = self.network.node_at(self._active_indexes[index])
            this_node.set_energy(energy_vector[index][0], 'psi')

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


class RemoteNozzleSolver(Solver):
    def __init__(self, network):
        Solver.__init__(self, network)
        self.unplugged_node_index = None
        self.detached_nozzle_index = None
        self._deleted_edge = None

    def solve_system(self):
        output_flow = 0
        self.remote_nozzle_initialize()
        self._initialize_solved_nozzles()
        cont = 0
        while not self._all_nozzles_solved():
            pair = self._nozzle_index_solved_status_hash[cont]
            if not pair[1]:
                self._solve_this_one(pair[0])
                pair[1] = True
                self._update_solved_nozzles()
            cont += 1
        for pair in self._nozzle_index_solved_status_hash:
            output_flow -= self.network.edge_at(pair[0]).calculate_gpm_flow()
        input_index = self.network.search_input_index()
        self.network.node_at(input_index).set_output_flow(output_flow, 'gpm')

    def remote_nozzle_initialize(self):
        for node in self.network.get_nodes():
            if isinstance(node, ConnectionNode):
                node.set_pressure(0, 'psi')

    def _initialize_solved_nozzles(self):
        self._nozzle_index_solved_status_hash = []
        for noz_index in range(len(self.network.get_edges())):
            if isinstance(self.network.edge_at(noz_index), Nozzle):
                self._nozzle_index_solved_status_hash.append([noz_index, False])

    def _all_nozzles_solved(self):
        for nozzle_number_status_pair in self._nozzle_index_solved_status_hash:
            if not nozzle_number_status_pair[1]:
                return False
        return True

    def _solve_this_one(self, nozzle_index):
        self.hold_nozzle(nozzle_index)
        self.prepare_solving_conditions()
        initial_guess = self.first_guess()
        self._iterate(initial_guess)
        self.reinsert_nozzle()

    def hold_nozzle(self, noz_index):
        assert isinstance(self.network.edge_at(noz_index), Nozzle)
        input_node_name = self.network.edge_at(noz_index).input_node.name
        input_index = self.network.get_node_index_by_name(input_node_name)
        assert isinstance(self.network.node_at(input_index), ConnectionNode)
        self._set_nozzle_output_flow(noz_index, input_index)
        self.unplugged_node_index = input_index
        self.network.separate_node_from_edge(input_index, noz_index)
        self.detached_nozzle_index = noz_index
        self._deleted_edge = self.network.get_edges().pop(noz_index)  # CHECK
        req_pressure = self._deleted_edge.get_required_pressure('psi')
        self.network.node_at(input_index).set_pressure(req_pressure, 'psi')

    def _set_nozzle_output_flow(self, noz_index, input_index):
        detached_nozzle = self.network.edge_at(noz_index)
        k_factor = detached_nozzle.get_factor('gpm/psi^0.5')
        pressure = detached_nozzle.get_required_pressure('psi')
        out_flow = k_factor * sqrt(pressure)
        self.network.node_at(input_index).set_output_flow(out_flow, 'gpm')

    def get_problem_size(self):
        return len(self._active_indexes)

    def first_guess(self):
        max_energy = self._get_max_energy()
        min_energy = self._get_min_energy()
        guess = np.zeros([self.size, 1])
        for cont in range(self.size):
            if self._active_indexes[cont] == self.unplugged_node_index:
                out_node = self.network.node_at(self.unplugged_node_index)
                guess[cont][0] = out_node.get_output_flow('gpm')
            else:
                guess[cont][0] = random.uniform(min_energy, max_energy)
                cur_node = self.network.node_at(self._active_indexes[cont])
                cur_node.set_energy(guess[cont][0], 'psi')
        return guess

    def _iterate(self, energy_vector):
        iteration = 0
        f_results = self.f_equations()
        while not self.has_converged(f_results):
            self.fill_jacobian()
            f_results = self.f_equations()
            delta = -np.linalg.solve(self.jacobian, f_results)
            energy_vector = np.add(energy_vector, delta)
            self._update_energies(energy_vector)
            iteration += 1
        # print "There were %d iterations" % iteration

    def fill_jacobian(self):
        for cont1 in range(self.size):
            row_index = self._active_indexes[cont1]
            is_row_input = row_index == self.network.search_input_index()
            for cont2 in range(self.size):
                col_index = self._active_indexes[cont2]
                if col_index == self.unplugged_node_index:
                    self.jacobian[cont1][cont2] = 1 if is_row_input else 0
                else:
                    self.jacobian[cont1][cont2] = self._cell_jacob(row_index,
                                                                   col_index)

    def _update_energies(self, energy_vector):
        for index in range(self.size):
            if self._active_indexes[index] == self.unplugged_node_index:
                input_index = self.network.search_input_index()
                this_node = self.network.node_at(input_index)
                assert isinstance(this_node, InputNode)
                this_node.set_output_flow(-energy_vector[index][0], 'gpm')
            else:
                this_node = self.network.node_at(self._active_indexes[index])
                this_node.set_energy(energy_vector[index][0], 'psi')

    def reinsert_nozzle(self):
        ins_index = self.detached_nozzle_index
        self.network.get_edges().insert(ins_index, self._deleted_edge)
        unplugged_index = self.unplugged_node_index
        self.network.node_at(unplugged_index).set_output_flow(0, 'gpm')
        self.network.connect_node_downstream_edge(unplugged_index, ins_index)
        self._deleted_edge = None
        self.detached_nozzle_index = None

    def _update_solved_nozzles(self):
        for pair in self._nozzle_index_solved_status_hash:
            cur_nozzle = self.network.edge_at(pair[0])
            required_pressure = cur_nozzle.get_required_pressure('psi')
            if cur_nozzle.input_node.get_pressure('psi') >= required_pressure:
                pair[1] = True
