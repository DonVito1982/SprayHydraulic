from hydraulics.pipe_network import PNetwork
from hydraulics.pipes import EndNode, ConnectionNode, Pipe, Nozzle


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
inner_diameters = [2, 2, 2, 1, 1]
pipe_count = len(lengths)

for pipe_index in range(pipe_count):
    cur_pipe = Pipe()
    cur_pipe.set_length(lengths[pipe_index], 'm')
    cur_pipe.set_inner_diam(inner_diameters[pipe_index], 'in')
    cur_pipe.set_c_coefficient(100)
    cur_pipe.name = pipe_index
    problem.add_pipe(cur_pipe)

#   SET NOZZLES
for index in range(5, 8):
    cur_pipe = Nozzle()
    cur_pipe.set_factor(2, 'gpm/psi^0.5')
    cur_pipe.name = index
    problem.add_pipe(cur_pipe)

# for element in problem.get_pipes():
#     print '%s is %s' % (element.name, type(element))

# SET CONNECTIVITY
problem.connect_node_downstream_pipe(0, 0)
problem.connect_node_downstream_pipe(1, 1)
problem.connect_node_downstream_pipe(2, 2)
