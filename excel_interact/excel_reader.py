from xlrd.biffh import XL_CELL_TEXT

from hydraulics.edges import Pipe
from hydraulics.pipe_network import PNetwork
from xlrd import open_workbook


class ExcelReader(object):
    network = None
    pipe_sheet = None
    units = {}

    @classmethod
    def invoke(cls, file_address):
        """

        :rtype: PNetwork
        :param file_address: the location of the file to be analyzed
        :return: The Network
        """
        cls.network = PNetwork()
        network_file = open_workbook(file_address)
        cls.pipe_sheet = network_file.sheet_by_name('Pipe')
        diam_header = cls.pipe_sheet.cell_value(0, 1)
        cls.units['inner_diam'] = ExcelReader.get_unit(diam_header)
        length_header = cls.pipe_sheet.cell_value(0, 3)
        length_unit = cls.get_unit(length_header)
        for cont in range(1, cls.pipe_sheet.nrows):
            cls.add_some_pipe(length_unit, cont)
        return cls.network

    @classmethod
    def add_some_pipe(cls, length_unit, pipe_index):
        pipe = Pipe()
        this_diam = cls.pipe_sheet.cell_value(pipe_index, 1)
        pipe.set_inner_diam(this_diam, cls.units['inner_diam'])
        this_length = cls.pipe_sheet.cell_value(pipe_index, 3)
        pipe.set_length(this_length, length_unit)
        name_cell = cls.pipe_sheet.cell(pipe_index, 0)
        if name_cell.ctype == XL_CELL_TEXT:
            pipe.name = cls.pipe_sheet.cell_value(pipe_index, 0)
        else:
            pipe.name = '%d' % cls.pipe_sheet.cell_value(pipe_index, 0)
        cls.network.add_edge(pipe)

    @staticmethod
    def get_unit(header_string):
        start_parenthesis = header_string.find('(') + 1
        length_unit = header_string[start_parenthesis: -1]
        return length_unit
