from hydraulics.pipe_network import PNetwork
from hydraulics.edges import Pipe, EndNode
from hydraulics.nodes import ConnectionNode
from hydraulics.solvers import UserSolver

elevations = [100, 85, 65, 65, 70, 70]
names = [0, 1, 2, 3, 4, 5]
network = PNetwork()
# SET NODES
#  END NODES
for cont in range(4):
    cur_node = EndNode()
    cur_node.set_elevation(elevations[cont], 'm')
    cur_node.name = names[cont]
    network.add_node(cur_node)

node_count = len(elevations)
end_count = 4

for node_index in range(end_count, node_count):
    cur_node = ConnectionNode()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[node_index], 'm')
    cur_node.name = names[node_index]
    network.add_node(cur_node)

# SET PIPES
lengths = [1000, 1200, 900, 500, 600]
inner_diameters = [10.75, 7.981, 7.981, 6.065, 6.065]

pipe_count = len(lengths)
for pipe_index in range(pipe_count):
    cur_pipe = Pipe()
    cur_pipe.set_length(lengths[pipe_index], 'm')
    cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
    cur_pipe.set_c_coefficient(100)
    cur_pipe.name = pipe_index
    network.add_edge(cur_pipe)

# SET CONNECTIVITY
network.connect_node_downstream_edge(4, 2)
network.connect_node_upstream_edge(4, 1)
network.connect_node_upstream_edge(4, 0)
network.connect_node_downstream_edge(0, 0)
network.connect_node_downstream_edge(1, 1)
network.connect_node_upstream_edge(5, 2)
network.connect_node_downstream_edge(5, 3)
network.connect_node_downstream_edge(5, 4)
network.connect_node_upstream_edge(2, 3)
network.connect_node_upstream_edge(3, 4)

# OUTPUT FLOW AT NODE 4
network.get_nodes()[4].set_output_flow(200, 'gpm')

user_solver = UserSolver(network)
user_solver.solve_system()


# FLOW CHECK
test_flows = [1135.2443, -383.5847, 751.6596, 394.3143, 357.3453]
for cont in range(pipe_count):
    cur_pipe = network.get_edges()[cont]
    print "p%s) flow %.3f gpm" % (cur_pipe.name, cur_pipe.get_gpm_flow())

# PRESSURE CHECK
test_press = [0, 0, 0, 0, 30.016, 7.383]

print
for node in network.get_nodes():
    in_gpm = 0
    for edge in node.get_input_pipes():
        in_gpm += edge.get_vol_flow('gpm')
    for edge in node.get_output_pipes():
        in_gpm -= edge.get_vol_flow('gpm')
    pressure = node.get_pressure('psi')
    print "n%s)P= %6.3f psi, Q= %9.3f" % (node.name, pressure, in_gpm)
