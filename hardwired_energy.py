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
lengths = [1000, 1200, 900, 500, 600]
inner_diameters = [10.75, 7.981, 7.981, 6.065, 6.065]
network_pipes = []
pipe_count = len(lengths)
for pipe_index in range(pipe_count):
    cur_pipe = pipes.Pipe()
    cur_pipe.set_length(lengths[pipe_index], 'm')
    cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
    cur_pipe.set_c_coefficient(100)
    cur_pipe.name = pipe_index
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
energy_4 = 90.01
energy_5 = 90.0
energy_vector = np.array([[energy_4], [energy_5]])
network_nodes[4].set_energy(energy_4, 'psi')
network_nodes[5].set_energy(energy_5, 'psi')


def k_factor(pipe, is_printed=False):
    length = pipe.get_length('ft')
    c = pipe.get_c_coefficient()
    diam = pipe.get_inner_diam('in')
    factor = (4.52 * length) / (c ** pipes.C_POWER * diam ** 4.87)
    if is_printed:
        print length
        # print c
        print diam
    return factor


vol_equations = np.array([0, 0])


def pipe_flow(pipe):
    input_energy = pipe.input_node.get_energy('psi')
    output_energy = pipe.output_node.get_energy('psi')
    if input_energy - output_energy == 0:
        return 0
    energy_ratio = (input_energy - output_energy) / k_factor(pipe)
    q_flow = energy_ratio * abs(energy_ratio) ** (1 / pipes.C_POWER - 1)
    return q_flow


print pipe_flow(network_pipes[0])
print "That was pipe #0"
print

active_nodes = [4, 5]
problem_size = len(active_nodes)


def f_equations():
    resp = np.zeros([problem_size, 1])
    for active_node in active_nodes:
        partial_flow = 0
        f_node = network_nodes[active_node]
        for pipe in f_node.get_input_pipes():
            partial_flow += pipe_flow(pipe)
        for pipe in f_node.get_output_pipes():
            partial_flow -= pipe_flow(pipe)
        resp[active_nodes.index(active_node)][0] = partial_flow
    return resp


jacobian = np.zeros([problem_size, problem_size])


def cell_jacob(current_pipes, evaluated_node):
    partial_jac = 0
    current_energy = evaluated_node.get_energy('psi')
    exponent = 1 / pipes.C_POWER - 1
    for connected_pipe in current_pipes['input']:
        k_fac = k_factor(connected_pipe)
        if connected_pipe.output_node == evaluated_node:
            input_energy = connected_pipe.input_node.get_energy('psi')
            partial_jac -= (1 / (pipes.C_POWER * k_fac)) * abs(
                (input_energy - current_energy) / k_fac) ** exponent
        if connected_pipe.input_node == evaluated_node:
            output_energy = connected_pipe.output_node.get_energy('psi')
            partial_jac += (1 / (pipes.C_POWER * k_fac)) * abs(
                (current_energy - output_energy) / k_fac) ** exponent
    for connected_pipe in current_pipes['output']:
        k_fac = k_factor(connected_pipe)
        if connected_pipe.output_node == evaluated_node:
            input_energy = connected_pipe.input_node.get_energy('psi')
            partial_jac += (1 / (pipes.C_POWER * k_fac)) * abs(
                (input_energy - current_energy) / k_fac) ** exponent
        if connected_pipe.input_node == evaluated_node:
            output_energy = connected_pipe.output_node.get_energy('psi')
            partial_jac -= (1 / (pipes.C_POWER * k_fac)) * abs(
                (current_energy - output_energy) / k_fac) ** exponent
    return partial_jac


energies = []
cont4 = 0

while cont4 < 5:
    for cont1 in range(problem_size):
        row_node = network_nodes[active_nodes[cont1]]
        connected_pipes = {'input': row_node.get_input_pipes(),
                           'output': row_node.get_output_pipes()}
        for cont2 in range(problem_size):
            col_node = network_nodes[active_nodes[cont2]]
            jacobian[cont1][cont2] = cell_jacob(connected_pipes, col_node)

    f_results = f_equations()
    delta = -np.linalg.solve(jacobian, f_results)
    energy_vector = np.add(energy_vector, delta)
    meter_energy = []
    for active_node_index in range(problem_size):
        this_node = network_nodes[active_nodes[active_node_index]]
        this_node.set_energy(energy_vector[active_node_index][0], 'psi')
        meter_energy.append(this_node.get_energy('mH2O'))
    energies.append(meter_energy)
    cont4 += 1
print
print "Energy 4 | Energy 5"
for linea in energies:
    print "%7.3f  | %7.3f" % (linea[0], linea[1])


def set_q(pipe, is_printed=False):
    up_energy = pipe.input_node.get_energy('psi')
    down_energy = pipe.output_node.get_energy('psi')
    if is_printed:
        print "Up energy (%s):%.2f psi" % (pipe.input_node.name, up_energy)
        print "Down energy (%s):%.2f psi" % (pipe.output_node.name, down_energy)
        print k_factor(pipe, True)
        print
    energy_ratio = (up_energy - down_energy) / k_factor(pipe)
    flow = energy_ratio * abs(energy_ratio) ** (1 / pipes.C_POWER - 1)
    pipe.set_vol_flow(flow, 'gpm')


end_flows = []
for cont5 in range(pipe_count):
    set_q(network_pipes[cont5])
    end_flows.append(network_pipes[cont5].get_vol_flow('gpm'))

print
print "Vol flows    0        1        2"
print "(gpm)    %8.3f %8.3f %8.3f" % (end_flows[0], end_flows[1], end_flows[2])
print "Flow from 4: %.3f gpm" % (end_flows[0] + end_flows[1] - end_flows[2])
print
print "(3):%f, (4):%f" % (end_flows[3], end_flows[4])
print end_flows[2] - end_flows[3] - end_flows[4]
