from hydraulics.edges import ANSIPipe
from hydraulics.pipe_network import PNetwork
import pandas as pd


class PandaReader(object):
    headers = {}
    pipe_df = None
    network = None
    pipe_units = None
    dim_header = None

    @classmethod
    def invoke(cls, file_address):
        cls.network = PNetwork()
        cls.pipe_units = {}
        data_frames = pd.read_excel(file_address, sheetname=None)
        cls.pipe_df = data_frames['Pipe']
        cls.headers['diam'] = cls.pipe_df.columns[1]
        cls.headers['length'] = cls.pipe_df.columns[3]
        cls.headers['sch'] = cls.pipe_df.columns[2]
        cls.pipe_units['diam'] = cls.get_unit(cls.headers['diam'])
        cls.pipe_units['length'] = cls.get_unit(cls.headers['length'])
        for cont in xrange(len(cls.pipe_df.index)):
            cls.add_ith_pipe(cont)
        return cls.network

    @classmethod
    def add_ith_pipe(cls, cont):
        this_pipe = ANSIPipe()
        this_pipe.schedule = cls.pipe_df[cls.headers['sch']][cont]
        this_pipe.nominal_diameter = cls.pipe_df[cls.headers['diam']][cont]
        this_pipe.diam_unit = cls.pipe_units['diam']
        # this_pipe.set_inner_diam(cls.pipe_df[cls.headers['diam']][cont],
        #                          cls.pipe_units['diam'])
        this_pipe.set_length(cls.pipe_df[cls.headers['length']][cont],
                             cls.pipe_units['length'])
        cls.network.add_edge(this_pipe)
        cls.network.set_pipe_name(cont, cls.pipe_df['Pipe'][cont])

    @staticmethod
    def get_unit(header):
        return header[header.find('(') + 1:header.find(')')]
