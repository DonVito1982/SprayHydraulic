class NameException(Exception):
    pass


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
        raise NameException

    @staticmethod
    def node_upstream_pipe(node, pipe):
        node.set_input_pipe(pipe)
        pipe.output_node = node

    @staticmethod
    def node_downstream_pipe(node, pipe):
        node.set_output_pipe(pipe)
        pipe.input_node = node
