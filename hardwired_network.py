import numpy

from hydraulics import pipes, nodes

network_nodes = []

elevations = [100, 85, 60, 85]

# SET NODES
node_count = 4
for x in range(node_count):
    cur_node = nodes.ConnectionNode()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[x], 'm')
    network_nodes.append(cur_node)

# SET PIPES
lengths = [1500, 1500, 1500]
diameters = [7.981, 6.065, 6.065]
network_pipes = []
pipe_count = 3
for x in range(pipe_count):
    cur_pipe = pipes.Pipe()
    cur_pipe.set_length(lengths[x], 'm')
    cur_pipe.set_inner_diam(diameters[x], 'in')
    cur_pipe.set_c_coefficient(100)
    network_pipes.append(cur_pipe)

# SET CONNECTIVITY
pipe_puts = [[1, 0, 0, -1],
             [0, -1, 0, 1],
             [0, 0, -1, 1]]

for pipe_index in range(pipe_count):
    for node_index in range(len(pipe_puts[0])):
        if pipe_puts[pipe_index][node_index] == -1:
            network_nodes[node_index].set_input_pipe(network_pipes[pipe_index])
        if pipe_puts[pipe_index][node_index] == 1:
            network_nodes[node_index].set_output_pipe(network_pipes[pipe_index])

# SET NODE[3] AS FLOW CONTINUITY NODE
flow_equation = []
for pipe_index in range(pipe_count):
    if network_pipes[pipe_index] in network_nodes[3].get_input_pipes():
        flow_equation.append(1)
    elif network_pipes[pipe_index] in network_nodes[3].get_output_pipes():
        flow_equation.append(-1)
    else:
        flow_equation.append(0)
flow_equation.append(0)  # Add independent value

# SET INITIAL FLOW GUESSES
vol_flows = numpy.array([10, -10, 20])

flow_vector = numpy.zeros([pipe_count + 1, 1])
for cont in range(pipe_count):
    flow_vector[cont][0] = vol_flows[cont]

flow_vector[pipe_count][0] = 1


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

    factor = (4.52 * length * abs(flow) ** (pipes.C_POWER - 1)) / \
             (c ** pipes.C_POWER * diam ** 4.87)
    return factor


def flow_jacob(pipe):
    length = pipe.get_length('ft')
    flow = pipe.get_vol_flow('gpm')
    c = pipe.get_c_coefficient()
    diam = pipe.get_inner_diam('in')
    factor = (4.52 * pipes.C_POWER * abs(flow) ** (pipes.C_POWER - 1) * length)
    factor /= (c ** pipes.C_POWER * diam ** 4.87)
    return factor


def f_module(vertical_vector):
    total = 0
    for module_counter in range(vertical_vector.shape[0]):
        total += vertical_vector[module_counter][0] ** 2
    return total

jacobian = numpy.zeros([pipe_count, pipe_count])

for x in range(pipe_count):
    jacobian[0][x] = flow_equation[x]

f_results = numpy.array([[2], [2]])

f_matrix = numpy.zeros([pipe_count, pipe_count+1])

for cont in range(pipe_count+1):
    f_matrix[0][cont] = flow_equation[cont]

iterations = 0
while f_module(f_results) > 0.00001:

    for x in range(pipe_count):
        network_pipes[x].set_vol_flow(flow_vector[x][0], 'gpm')

    node_energies = []
    for cont in range(3):
        node_energies.append(network_nodes[cont].get_energy('psi'))

    first_eq = [-k_factor(network_pipes[0]), -k_factor(network_pipes[1]), 0,
                node_energies[0] - node_energies[1]]
    second_eq = [-k_factor(network_pipes[0]), 0, -k_factor(network_pipes[2]),
                 node_energies[0] - node_energies[2]]

    for cont in range(4):
        f_matrix[1][cont] = first_eq[cont]
        f_matrix[2][cont] = second_eq[cont]

    f_results = numpy.dot(f_matrix, flow_vector)

    row_1 = [-flow_jacob(network_pipes[0]), -flow_jacob(network_pipes[1]), 0]
    row_2 = [-flow_jacob(network_pipes[0]), 0, -flow_jacob(network_pipes[2])]

    for x in range(pipe_count):
        jacobian[1][x] = row_1[x]
        jacobian[2][x] = row_2[x]

    delta = -numpy.linalg.solve(jacobian, f_results)

    delta = numpy.append(delta, [[0]], axis=0)

    flow_vector = numpy.add(flow_vector, delta)
    iterations += 1

print flow_vector

n4_energy = network_nodes[0].get_energy('psi') - \
            network_pipes[0].hazen_williams_loss('psi')
network_nodes[3].set_energy(n4_energy, 'psi')
print
print network_nodes[3].get_pressure('psi')

n2_energy = n4_energy - network_pipes[1].hazen_williams_loss('psi')
network_nodes[1].set_energy(n2_energy, 'psi')
print
print network_nodes[1].get_pressure('psi')
