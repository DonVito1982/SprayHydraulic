from pipes import C_POWER


class PNetwork (object):
    def __init__(self):
        self.net_nodes = []
        self.net_pipes = []

    def add_node(self, node):
        self.net_nodes.append(node)

    def get_nodes(self):
        return self.net_nodes

    def add_pipe(self, pipe):
        self.net_pipes.append(pipe)

    def get_pipes(self):
        return self.net_pipes

    def node_by_name(self, name):
        for node in self.get_nodes():
            if node.name == name:
                return node
        raise IndexError

    @staticmethod
    def node_upstream_pipe(node, pipe):
        node.set_input_pipe(pipe)
        pipe.output_node = node

    @staticmethod
    def node_downstream_pipe(node, pipe):
        node.set_output_pipe(pipe)
        pipe.input_node = node

    @staticmethod
    def k_factor(pipe):
        length = pipe.get_length('ft')
        c = pipe.get_c_coefficient()
        diam = pipe.get_inner_diam('in')
        factor = (4.52 * length) / (c ** C_POWER * diam ** 4.87)
        return factor
