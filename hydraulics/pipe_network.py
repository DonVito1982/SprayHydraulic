from edges import Nozzle
from nodes import ConnectionNode, InputNode, EndNode
from math import sqrt


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

    def node_at(self, node_index):
        return self._net_nodes[node_index]

    def add_edge(self, edge):
        assert edge not in self._net_edges
        self._net_edges.append(edge)

    def get_edges(self):
        return self._net_edges

    def edge_at(self, edge_index):
        return self._net_edges[edge_index]

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
        self.edge_at(edge_index).clear_input()

    def _set_nozzle_output_flow(self, noz_index, input_index):
        detached_nozzle = self.get_edges()[noz_index]
        k_factor = detached_nozzle.get_factor('gpm/psi^0.5')
        pressure = detached_nozzle.get_required_pressure('psi')
        out_flow = k_factor * sqrt(pressure)
        self.get_nodes()[input_index].set_output_flow(out_flow, 'gpm')

    def search_input_index(self):
        for cont in range(len(self._net_nodes)):
            if isinstance(self._net_nodes[cont], InputNode):
                return cont

    def show_network(self):
        print "Node Pressure"
        for node in self._net_nodes:
            if not isinstance(node, EndNode):
                print "%s: %.4f psi" % (node.name, node.get_pressure('psi'))
        print "\nEdge Volumetric Flow (psi)"
        for edge in self._net_edges:
            print "%s: %.4f gpm" % (edge.name, edge.get_gpm_flow())
