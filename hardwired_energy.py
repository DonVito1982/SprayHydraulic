import pipes
import nodes
import numpy as np

network_nodes = []

elevations = [100, 85, 60, 85]

# SET NODES
node_count = 4
for node_index in range(node_count):
    cur_node = nodes.Node()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[node_index], 'm')
    network_nodes.append(cur_node)

# SET PIPES
lengths = [1500, 1500, 1500]
inner_diams = [7.981, 6.065, 6.065]
network_pipes = []
pipe_count = 3
for pipe_index in range(pipe_count):
    cur_pipe = pipes.Pipe()
    cur_pipe.set_length(lengths[pipe_index], 'm')
    cur_pipe.set_inner_diam(inner_diams[pipe_index], 'in')
    cur_pipe.set_c_coefficient(100)
    network_pipes.append(cur_pipe)
