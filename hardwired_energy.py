import numpy as np

from hydraulics import edges, nodes

network_nodes = []

elevations = [100, 85, 65, 65, 70, 70]
names = [0, 1, 2, 3, 4, 5]

# SET NODES
#  END NODES
for cont6 in range(4):
    cur_node = nodes.EndNode()
    cur_node.set_elevation(elevations[cont6], 'm')
    cur_node.name = names[cont6]
    network_nodes.append(cur_node)

node_count = len(elevations)
end_count = 4

for node_index in range(end_count, node_count):
    cur_node = nodes.ConnectionNode()
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
    cur_pipe = edges.Pipe()
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
    :type node: nodes.ConnectionNode
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


print network_pipes[0].calculate_gpm_flow()
print "That was pipe #0"
print

active_nodes = []
for cont in range(node_count):
    if isinstance(network_nodes[cont], nodes.ConnectionNode):
        active_nodes.append(cont)

problem_size = len(active_nodes)


def f_equations():
    resp = np.zeros([problem_size, 1])
    for active_node in active_nodes:
        partial_flow = 0
        f_node = network_nodes[active_node]
        for pipe in f_node.get_input_pipes():
            partial_flow += pipe.calculate_gpm_flow()
        for pipe in f_node.get_output_pipes():
            partial_flow -= pipe.calculate_gpm_flow()
        resp[active_nodes.index(active_node)][0] = partial_flow
    return resp


jacobian = np.zeros([problem_size, problem_size])


def cell_jacob(main_node, evaluated_node):
    partial_jac = 0
    for connected_pipe in main_node.get_input_pipes():
        partial_jac += connected_pipe.get_node_jacobian(evaluated_node)
    for connected_pipe in main_node.get_output_pipes():
        partial_jac -= connected_pipe.get_node_jacobian(evaluated_node)
    return partial_jac


energies = []
cont4 = 0

while cont4 < 5:
    for cont1 in range(problem_size):
        row_node = network_nodes[active_nodes[cont1]]
        for cont2 in range(problem_size):
            col_node = network_nodes[active_nodes[cont2]]
            jacobian[cont1][cont2] = cell_jacob(row_node, col_node)

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
        print pipe.k_flow()
        print
    energy_ratio = (up_energy - down_energy) / pipe.k_flow()
    flow = energy_ratio * abs(energy_ratio) ** (1 / edges.Pipe.C_POWER - 1)
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
