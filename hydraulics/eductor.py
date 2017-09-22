from edges import Edge
from nodes import ConnectionNode


class Eductor(Edge):
    def get_gpm_flow(self):
        pass

    def get_node_jacobian(self, node):
        pass

    def is_complete(self):
        pass

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        if self._input_node:
            raise IndexError("Already have input node")
        if not isinstance(node, ConnectionNode):
            raise ValueError
        self._input_node = node

    @property
    def output_node(self):
        return self._output_node

    @output_node.setter
    def output_node(self, node):
        if self._output_node:
            raise IndexError
        if not isinstance(node, ConnectionNode):
            raise ValueError
        self._output_node = node
