from hydraulics.edges import ANSIPipe
from hydraulics.nodes import ConnectionNode, InputNode
from hydraulics.pipe_network import PNetwork
import pandas as pd


class PandaReader(object):
    headers = {}
    node_df = None
    pipe_df = None
    network = None
    pipe_units = None
    node_units = None
    dim_header = None

    @classmethod
    def invoke(cls, file_address):
        cls.network = PNetwork()
        cls.pipe_units = {}
        cls.node_units = {}
        cls.add_nodes(file_address)
        cls.add_edges(file_address)
        return cls.network

    @classmethod
    def add_nodes(cls, file_address):
        cls.node_df = pd.read_excel(file_address, sheetname='Nodes')
        cls.headers['elevation'] = cls.node_df.columns[1]
        cls.node_units['elevation'] = cls.get_unit(cls.headers['elevation'])
        for cont in xrange(len(cls.node_df.index)):
            cls.add_ith_node(cont)
        for cont in xrange(len(cls.network.get_nodes())):
            cls.network.set_node_name(cont, cls.node_df['Node'][cont])

    @classmethod
    def add_ith_node(cls, cont):
        if cls.node_df['Input'][cont] == 'Y':
            this_node = InputNode()
        else:
            this_node = ConnectionNode()
        this_elevation = cls.node_df[cls.headers['elevation']][cont]
        this_node.set_elevation(this_elevation, cls.node_units['elevation'])
        cls.network.add_node(this_node)

    @classmethod
    def add_edges(cls, file_address):
        cls.pipe_df = pd.read_excel(file_address, sheetname='Pipe')
        cls.headers['diam'] = cls.pipe_df.columns[1]
        cls.headers['length'] = cls.pipe_df.columns[3]
        cls.headers['sch'] = cls.pipe_df.columns[2]
        cls.headers['in_node'] = cls.pipe_df.columns[4]
        cls.pipe_units['diam'] = cls.get_unit(cls.headers['diam'])
        cls.pipe_units['length'] = cls.get_unit(cls.headers['length'])
        for cont in xrange(len(cls.pipe_df.index)):
            cls.add_ith_pipe(cont)

    @classmethod
    def add_ith_pipe(cls, cont):
        this_pipe = ANSIPipe()
        this_pipe.schedule = cls.pipe_df[cls.headers['sch']][cont]
        this_pipe.nominal_diameter = cls.pipe_df[cls.headers['diam']][cont]
        this_pipe.diam_unit = cls.pipe_units['diam']
        this_pipe.set_length(cls.pipe_df[cls.headers['length']][cont],
                             cls.pipe_units['length'])
        cls.network.add_edge(this_pipe)
        node_index = cls.pipe_df['In'][cont] - 1
        cls.network.connect_node_downstream_edge(node_index, cont)
        cls.network.set_pipe_name(cont, cls.pipe_df['Pipe'][cont])

    @staticmethod
    def get_unit(header):
        return header[header.find('(') + 1:header.find(')')]
