from hydraulics.pipe_network import PNetwork
from hydraulics.edges import EndNode, Pipe, Nozzle
from hydraulics.nodes import InputNode, ConnectionNode
# from hydraulics.solvers import UserSolver

problem = PNetwork()

# SET NODES
system_nodes = ['i', 'c', 'c', 'c', 'e', 'e', 'e']
elevations = [0, 0, 0, 0, 0, 0, 0]

for index in range(len(system_nodes)):
    if system_nodes[index] == 'e':
        cur_node = EndNode()
    if system_nodes[index] == 'c':
        cur_node = ConnectionNode()
        cur_node.set_pressure(0, 'psi')
    if system_nodes[index] == 'i':
        cur_node = InputNode()
    cur_node.set_elevation(elevations[index], 'm')
    cur_node.name = "%s%d" % (system_nodes[index], index)
    problem.add_node(cur_node)

# SET EDGES
#   SET PIPES
pipe_count = 3

for pipe_index in range(pipe_count):
    cur_pipe = Pipe()
    cur_pipe.set_length(2, 'm')
    cur_pipe.set_inner_diam(.957, 'in')
    cur_pipe.set_c_coefficient(100)
    problem.add_edge(cur_pipe)
    problem.set_pipe_name(pipe_index, pipe_index)

# SET NOZZLES
for edge_index in range(3, 6):
    cur_pipe = Nozzle()
    cur_pipe.set_factor(2, 'gpm/psi^0.5')
    cur_pipe.set_required_pressure(25, 'psi')
    problem.add_edge(cur_pipe)
    problem.set_pipe_name(edge_index, edge_index)

# for element in problem.get_edges():
#     print '%s is %s' % (element.name, type(element))

# SET CONNECTIVITY
problem.connect_node_downstream_edge(0, 0)
problem.connect_node_downstream_edge(1, 1)
problem.connect_node_downstream_edge(1, 3)
problem.connect_node_upstream_edge(1, 0)
problem.connect_node_downstream_edge(2, 2)
problem.connect_node_downstream_edge(2, 4)
problem.connect_node_upstream_edge(2, 1)
problem.connect_node_upstream_edge(3, 2)
problem.connect_node_downstream_edge(3, 5)
problem.connect_node_upstream_edge(4, 3)
problem.connect_node_upstream_edge(5, 4)
problem.connect_node_upstream_edge(6, 5)

# for index in range(6):
#     cur_pipe = problem.get_edges()[index]
#     message = 'complete' if cur_pipe.is_complete() else 'not complete'
#     print "Pipe #%s is %s" % (cur_pipe.name, message)

# user_solve = UserSolver(problem)
# user_solve._set_active_nodes_indexes()
# user_solve.prepare_solving_conditions()
# problem_size =  user_solve.size

problem.solve_remote_nozzle()
problem.show_network()
