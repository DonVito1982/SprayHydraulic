import pipes
import nodes
import numpy

network_nodes = []

elevations = [100, 85, 60, 85]

for x in range(4):
    cur_node = nodes.Node()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[x], 'm')
    network_nodes.append(cur_node)

lengths = [100, 150, 150]
diameters = [12, 10, 10]
network_pipes = []
for x in range(3):
    cur_pipe = pipes.Pipe()
    cur_pipe.set_length(lengths[x], 'm')
    cur_pipe.set_inner_diam(diameters[x], 'in')
    cur_pipe.set_c_coefficient(100)
    network_pipes.append(cur_pipe)

vol_flows = numpy.array([1, 2, 3])


def k_factor(pipe):
    """
    Determine "K" factor for pipe
    :param pipe: Pipe to be evaluated
    :type pipe: pipes.Pipe
    :return: The K factor
    :rtype :float
    """
    length = pipe.get_length('ft')
    flow = pipe.get_vol_flow('gpm')
    c = pipe.get_c_coefficient()
    diam_in = pipe.get_inner_diam('in')
    factor = (4.52 * length * abs(flow) ** 0.85) / (c ** 1.85 * diam_in ** 4.87)
    return factor


def flow_jacob(pipe):
    length = pipe.get_length('ft')
    flow = pipe.get_vol_flow('gpm')
    c = pipe.get_c_coefficient()
    diam = pipe.get_inner_diam('in')
    factor = (8.362 * abs(flow) ** 0.85 * length) / (c ** 1.85 * diam ** 4.87)
    return factor


for x in range(3):
    network_pipes[x].set_vol_flow(vol_flows[x], 'gpm')

f_matrix = numpy.array([[1, -1, -1, 0]])
n1_energy = network_nodes[0].get_energy('psi')
n2_energy = network_nodes[1].get_energy('psi')
n3_energy = network_nodes[2].get_energy('psi')
first_eq = [-k_factor(network_pipes[0]), -k_factor(network_pipes[1]), 0,
            n1_energy - n2_energy]
second_eq = [-k_factor(network_pipes[0]), 0, -k_factor(network_pipes[2]),
             n1_energy - n3_energy]

f_matrix = numpy.append(f_matrix, [first_eq], axis=0)
f_matrix = numpy.append(f_matrix, [second_eq], axis=0)

# print f_matrix

flow_vector = numpy.array([[1]])
for x in range(2, -1, -1):
    flow_vector = numpy.insert(flow_vector, [0],
                               [[network_pipes[x].get_vol_flow('gpm')]], axis=0)

f_results = numpy.dot(f_matrix, flow_vector)
# print f_results

