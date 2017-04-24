from nodes import InputNode, EndNode


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
        raise ValueError

    def get_edge_index_by_name(self, name):
        cont = 0
        for edge in self.get_edges():
            if edge.name == name:
                return cont
            cont += 1
        raise IndexError

    def connect_node_upstream_edge(self, node_index, edge_index):
        node = self.node_at(node_index)
        edge = self.edge_at(edge_index)
        node.set_input_pipe(edge)
        edge.output_node = node

    def connect_node_downstream_edge(self, node_index, edge_index):
        node = self.node_at(node_index)
        edge = self.edge_at(edge_index)
        node.set_output_pipe(edge)
        edge.input_node = node

    def set_node_name(self, index, name):
        for node in self._net_nodes:
            if node.name == name:
                raise IndexError
        self._net_nodes[index].name = name

    def set_pipe_name(self, index, name):
        for pipe in self._net_edges:
            if pipe.name == str(name):
                raise IndexError('Nombre %s usado para %d' % (str(name), index))
        self.edge_at(index).name = name

    def separate_node_from_edge(self, node_index, edge_index):
        edge = self.edge_at(edge_index)
        node = self.node_at(node_index)
        if node is edge.input_node:
            self._separate_edge_from_input(edge_index, node_index)
        elif node is edge.output_node:
            self._separate_edge_from_output(edge_index, node_index)
        else:
            raise IndexError

    def _separate_edge_from_output(self, edge_index, node_index):
        connected_pipes = self.node_at(node_index).get_input_pipes()
        for e_index in range(len(connected_pipes)):
            if connected_pipes[e_index] is self.edge_at(edge_index):
                self.node_at(node_index).remove_input(e_index)
                break
        self.edge_at(edge_index).clear_output()

    def _separate_edge_from_input(self, edge_index, node_index):
        connected_pipes = self.node_at(node_index).get_output_pipes()
        for e_index in range(len(connected_pipes)):
            separated_edge = self.edge_at(edge_index)
            if connected_pipes[e_index] is separated_edge:
                self.node_at(node_index).remove_output(e_index)
                break
        self.edge_at(edge_index).clear_input()

    def search_input_index(self):
        for cont in range(len(self._net_nodes)):
            if isinstance(self.node_at(cont), InputNode):
                return cont

    def show_network(self):
        print "Node Pressure"
        for node in self._net_nodes:
            if not isinstance(node, EndNode):
                print "%s: %.4f psi" % (node.name, node.get_pressure('psi'))
        print "\nEdge Volumetric Flow (psi)"
        for edge in self._net_edges:
            print "%s: %.4f gpm" % (edge.name, edge.get_gpm_flow())
