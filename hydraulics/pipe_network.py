from nodes import ConnectionNode


class PNetwork (object):
    def __init__(self):
        self.net_nodes = []
        self.net_pipes = []
        self._active_nodes = []

    def add_node(self, node):
        self.net_nodes.append(node)
        if isinstance(node, ConnectionNode):
            self._active_nodes = []

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
