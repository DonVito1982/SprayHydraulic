import pipes
import nodes
import numpy as np

network_nodes = []

elevations = [100, 85, 65, 65, 70, 70]
names = [0, 1, 2, 3, 4, 5]

# SET NODES
node_count = len(elevations)
for node_index in range(node_count):
    cur_node = nodes.Node()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[node_index], 'm')
    cur_node.name = names[node_index]
    network_nodes.append(cur_node)

# SET PIPES
lengths = [1000, 700, 300, 500, 600]
inner_diameters = [10.75, 7.981, 7.981, 6.065, 6.065]
network_pipes = []
pipe_count = len(lengths)
for pipe_index in range(pipe_count):
    cur_pipe = pipes.Pipe()
    cur_pipe.set_length(lengths[pipe_index], 'm')
    cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
    cur_pipe.set_c_coefficient(100)
    network_pipes.append(cur_pipe)


# SET CONNECTIVITY
def node_upstream_pipe(node, pipe):
    """
    Takes a node ans sets an upstream pipe
    :param node: The node in question
    :type node: nodes.Node
    :param pipe: The upstream pipe
    :return:
    """
    node.set_input_pipe(pipe)
    pipe.output_node = node


def node_downstream_pipe(node, pipe):
    node.set_output_pipe(pipe)
    pipe.input_node = node


node_downstream_pipe(network_nodes[4], network_pipes[2])
node_upstream_pipe(network_nodes[4], network_pipes[1])
node_upstream_pipe(network_nodes[4], network_pipes[0])
node_downstream_pipe(network_nodes[0], network_pipes[0])
node_downstream_pipe(network_nodes[1], network_pipes[1])
node_upstream_pipe(network_nodes[5], network_pipes[2])
node_downstream_pipe(network_nodes[5], network_pipes[3])
node_downstream_pipe(network_nodes[5], network_pipes[4])
node_upstream_pipe(network_nodes[2], network_pipes[3])
node_upstream_pipe(network_nodes[3], network_pipes[4])

# SET INITIAL HEAD GUESS
energy_4 = 90
energy_5 = 90
energy_vector = np.array([[energy_4], [energy_5]])
network_nodes[4].set_energy(energy_4, 'mH2O')
network_nodes[5].set_energy(energy_5, 'mH2O')


def k_factor(pipe):
    length = pipe.get_length('ft')
    c = pipe.get_c_coefficient()
    diam = pipe.get_inner_diam('in')
    factor = (4.52 * length) / (c ** pipes.C_POWER * diam ** 4.87)
    return factor


def vol_flow(pipe):
    input_node = pipe.input_node
    output_node = pipe.output_node
    numerator = (input_node.get_energy('psi') - output_node.get_energy('psi'))
    flow = (numerator / k_factor(pipe)) ** (1 / pipes.C_POWER)
    return flow


vol_equations = np.array([0, 0])


def pipe_flow(pipe):
    input_energy = pipe.input_node.get_energy('psi')
    # print pipe.input_node.name
    output_energy = pipe.output_node.get_energy('psi')
    # print pipe.output_node.name
    if input_energy-output_energy == 0:
        return 0
    energy_ratio = (input_energy - output_energy) / k_factor(pipe)
    q_flow = energy_ratio * abs(energy_ratio) ** (1 / pipes.C_POWER - 1)
    return q_flow


active_nodes = [4, 5]
problem_size = len(active_nodes)


def f_equations():
    resp = np.zeros([problem_size, 1])
    for node_index in active_nodes:
        partial_flow = 0
        for pipe in network_nodes[node_index].get_input_pipes():
            partial_flow += pipe_flow(pipe)
        for pipe in network_nodes[node_index].get_output_pipes():
            partial_flow -= pipe_flow(pipe)
        resp[active_nodes.index(node_index)][0] = partial_flow
    return resp


jacobian = np.zeros([problem_size, problem_size])


def partial_jacobian(current_pipes, this_node):
    partial_jac = 0
    current_energy = this_node.get_energy('psi')
    for connected_pipe in current_pipes:
        k_fac = k_factor(connected_pipe)
        exponent = 1 / pipes.C_POWER - 1
        if connected_pipe.output_node == this_node:
            input_energy = connected_pipe.input_node.get_energy('psi')
            partial_jac += (1 / (pipes.C_POWER * k_fac)) * abs(
                (input_energy - current_energy) / k_fac) ** exponent
        if connected_pipe.input_node == this_node:
            output_energy = connected_pipe.output_node.get_energy('psi')
            partial_jac -= (1 / (pipes.C_POWER * k_fac)) * abs(
                (current_energy - output_energy) / k_fac) ** exponent
    return partial_jac


for cont1 in range(problem_size):
    row_node = network_nodes[cont1]
    for cont2 in range(problem_size):
        col_node = network_nodes[cont2]
        connected_pipes = row_node.get_input_pipes()
        connected_pipes += row_node.get_output_pipes()
        jacobian[cont1][cont2] = partial_jacobian(connected_pipes, col_node)

delta = -np.linalg.solve(jacobian, f_equations())
print delta
print
print energy_vector
energy_vector = np.add(energy_vector, delta)
print energy_vector

for cont3 in range(problem_size):
    este_nodo = network_nodes[active_nodes[cont3]]
    este_nodo.set_energy(energy_vector[cont3][0], 'psi')
