import pipes
import nodes
import numpy as np

network_nodes = []

elevations = [100, 85, 65, 65, 70, 70]

# SET NODES
node_count = len(elevations)
for node_index in range(node_count):
    cur_node = nodes.Node()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[node_index], 'm')
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
energy_4 = 100
energy_5 = 100


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
    output_energy = pipe.output_node.get_energy('psi')
    energy_ratio = (input_energy - output_energy) / k_factor(pipe)
    q_flow = (energy_ratio) * abs(energy_ratio) ** (1 / pipes.C_POWER - 1)
    return q_flow

def f_equations():
    resp = []
    active_nodes = [4, 5]
    for index in active_nodes:
        partial_flow = 0
        for pipe in network_nodes[index].get_input_pipes():
            partial_flow += pipe_flow(pipe)
        for pipe in network_nodes[index].get_output_pipes():
            partial_flow -= pipe_flow(pipe)
        resp.append(partial_flow)
    return resp
