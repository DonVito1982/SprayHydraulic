from hydraulics.pipe_network import PNetwork
from hydraulics.edges import EndNode, ConnectionNode, Pipe, Nozzle


problem = PNetwork()

# SET NODES
system_nodes = ['e', 'e', 'c', 'c', 'c', 'e', 'e', 'e', 'c']
elevations = [30, 35, 25, 0, 0, 0, 0, 0, 0]

for index in range(len(system_nodes)):
    if system_nodes[index] == 'e':
        cur_node = EndNode()
    if system_nodes[index] == 'c':
        cur_node = ConnectionNode()
        cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[index], 'm')
    cur_node.name = index
    problem.add_node(cur_node)


# SET EDGES
#   SET PIPES
lengths = [100, 150, 20, 2, 2]
inner_diameters = [1.939, 1.939, 1.939, .957, .957]
pipe_count = len(lengths)

for pipe_index in range(pipe_count):
    cur_pipe = Pipe()
    cur_pipe.set_length(lengths[pipe_index], 'm')
    cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
    cur_pipe.set_c_coefficient(100)
    problem.add_edge(cur_pipe)
    problem.set_pipe_name(pipe_index, pipe_index)
    # cur_pipe.name = pipe_index


#   SET NOZZLES
for index in range(5, 8):
    cur_pipe = Nozzle()
    cur_pipe.set_factor(2, 'gpm/psi^0.5')
    cur_pipe.name = index
    problem.add_edge(cur_pipe)

# for element in problem.get_edges():
#     print '%s is %s' % (element.name, type(element))

# SET CONNECTIVITY
problem.connect_node_downstream_edge(0, 0)
problem.connect_node_downstream_edge(1, 1)
problem.connect_node_downstream_edge(2, 2)
problem.connect_node_upstream_edge(2, 0)
problem.connect_node_upstream_edge(2, 1)
problem.connect_node_downstream_edge(3, 5)
problem.connect_node_downstream_edge(3, 3)
problem.connect_node_upstream_edge(3, 2)
problem.connect_node_downstream_edge(4, 4)
problem.connect_node_downstream_edge(4, 6)
problem.connect_node_upstream_edge(4, 3)
problem.connect_node_upstream_edge(5, 5)
problem.connect_node_upstream_edge(6, 6)
problem.connect_node_upstream_edge(7, 7)
problem.connect_node_downstream_edge(8, 7)
problem.connect_node_upstream_edge(8, 4)

# for index in range(8):
#     cur_pipe = problem.get_edges()[index]
#     message = 'complete' if cur_pipe.is_complete() else 'not complete'
#     print "Pipe #%s is %s" % (cur_pipe.name, message)

problem.solve_system()

for edge in problem.get_edges():
    print "%s) flow: %8.4f" % (edge.name, edge.get_gpm_flow())

for node in problem.get_nodes():
    if isinstance(node, ConnectionNode):
        in_gpm = 0
        for edge in node.get_input_pipes():
            in_gpm += edge.get_vol_flow('gpm')
        for edge in node.get_output_pipes():
            in_gpm -= edge.get_vol_flow('gpm')
        pressure = node.get_energy('psi')
        print "%s)Press: %7.4f psi, flow: %6.3f" % (node.name, pressure, in_gpm)
