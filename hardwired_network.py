import pipes
import nodes
import numpy

network_nodes = []

elevations = [100, 90, 65, 85]

for x in range(4):
    cur_node = nodes.Node()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[x], 'm')
    network_nodes.append(cur_node)

lengths = [1500, 1500, 1500]
diameters = [7.981, 6.065, 6.065]
network_pipes = []
for x in range(3):
    cur_pipe = pipes.Pipe()
    cur_pipe.set_length(lengths[x], 'm')
    cur_pipe.set_inner_diam(diameters[x], 'in')
    cur_pipe.set_c_coefficient(100)
    network_pipes.append(cur_pipe)

vol_flows = numpy.array([10, -10, 20])

flow_vector = numpy.zeros([4, 1])
for cont in range(3):
    flow_vector[cont][0] = vol_flows[cont]

flow_vector[3][0] = 1


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
    diam = pipe.get_inner_diam('in')
    factor = (4.52 * length * abs(flow) ** 0.852) / (c ** 1.852 * diam ** 4.87)
    return factor


def flow_jacob(pipe):
    length = pipe.get_length('ft')
    flow = pipe.get_vol_flow('gpm')
    c = pipe.get_c_coefficient()
    diam = pipe.get_inner_diam('in')
    factor = (8.37104 * abs(flow) ** 0.852 * length) / \
             (c ** 1.852 * diam ** 4.87)
    return factor

jacobian = numpy.zeros([3, 3])


def f_module(vertical_vector):
    total = 0
    for module_counter in range(vertical_vector.shape[0]):
        total += vertical_vector[module_counter][0] ** 2
    return total

iterations = 0
f_results = numpy.array([[2], [2]])
print f_module(f_results)

while f_module(f_results) > 0.00001:

    for x in range(3):
        network_pipes[x].set_vol_flow(flow_vector[x][0], 'gpm')

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

    f_results = numpy.dot(f_matrix, flow_vector)
    print "f-results %d" % iterations
    print f_module(f_results)
    print

    flow_equation = [1, -1, -1]
    for x in range(3):
        jacobian[0][x] = flow_equation[x]

    row_1 = [-flow_jacob(network_pipes[0]), -flow_jacob(network_pipes[1]), 0]
    row_2 = [-flow_jacob(network_pipes[0]), 0, -flow_jacob(network_pipes[2])]

    for x in range(3):
        jacobian[1][x] = row_1[x]
        jacobian[2][x] = row_2[x]

    delta = -numpy.linalg.solve(jacobian, f_results)

    delta = numpy.append(delta, [[0]], axis=0)

    flow_vector = numpy.add(flow_vector, delta)
    iterations += 1

print flow_vector
