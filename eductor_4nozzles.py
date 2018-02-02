from hydraulics.edges import ANSIPipe, Nozzle
from hydraulics.eductor import Eductor
from hydraulics.nodes import EndNode, ConnectionNode
from hydraulics.pipe_network import PNetwork
from hydraulics.solvers import UserSolver

problem = PNetwork()

# SET NODES
system_nodes = ['e', 'c', 'c', 'c', 'c', 'c', 'c', 'e', 'e', 'c', 'e', 'c', 'e']
elevations = [30,   0,   0,   0,   0,   2,   2,   2,   2,   2,   2,   2,   2]

for index in range(len(system_nodes)):
    if system_nodes[index] == 'e':
        cur_node = EndNode()
    else:
        cur_node = ConnectionNode()
        cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[index], 'm')
    cur_node.name = "%s%d" % (system_nodes[index], index)
    problem.add_node(cur_node)

# SET EDGES
#   SET PIPES
lentghts = (40, 3, 10, 10, 2, 2)
diams = (3, 2, 2, 2, 1, 1)

pipes = []
for i in range(len(diams)):
    cur_pipe = ANSIPipe()
    cur_pipe.nominal_diameter = diams[i]
    cur_pipe.diam_unit = 'in'
    cur_pipe.set_length(lentghts[i], 'm')
    cur_pipe.schedule = '80'
    pipes.append(cur_pipe)

#   SET NOZZLES
nozzles = []
for i in range(4):
    cur_nozzle = Nozzle()
    cur_nozzle.set_factor(3.2, 'gpm/psi^0.5')
    cur_nozzle.set_required_pressure(15, 'psi')
    nozzles.append(cur_nozzle)

#   SET EDUCTORS
eductors = []
for i in range(2):
    cur_eductor = Eductor()
    cur_eductor.set_factor(7.0, 'gpm/psi^0.5')
    cur_eductor.concentration = 0.03
    eductors.append(cur_eductor)

edge_types = "ppeeppnnpnpn"

# INCLUDE EDGES IN NETWORK
typ_dict = {'p': pipes, 'n': nozzles, 'e': eductors}
for carac in edge_types:
    #print carac
    problem.add_edge(typ_dict[carac].pop(0))
    problem.set_pipe_name(-1, "%s%d" % (carac, len(problem.get_edges()) - 1))

'''
print "SOMETHING"
for edge in problem.get_edges():
    print "%3s -" % edge.name,
    if isinstance(edge, ANSIPipe):
        print "%4d - %5.1f" % (edge.nominal_diameter, edge.get_length('m'))
    elif isinstance(edge, Nozzle):
        print "%4.1f" % (edge.get_factor('gpm/psi^0.5'))
    else:
        print "%4.1f - %5.2f" % (edge.get_factor('gpm/psi^0.5'), edge.concentration)
'''

# SET CONNECTIVITY
connected_edges = [[[], [0]],
                   [[0], [1, 2]],
                   [[1], [3]],
                   [[2], [4]],
                   [[3], [5]],
                   [[4], [6, 8]],
                   [[5], [7, 10]],
                   [[6], []],
                   [[7], []],
                   [[8], [9]],
                   [[9], []],
                   [[10], [11]],
                   [[11], []]
                   ]

for i in range(len(connected_edges)):
    for input_index in connected_edges[i][0]:
        problem.connect_node_upstream_edge(i, input_index)
    for output_index in connected_edges[i][1]:
        problem.connect_node_downstream_edge(i, output_index)

for n in range(12):
    edge = problem.edge_at(n)
    in_name = edge.input_node.name
    out_name = edge._output_node.name
    if edge.is_complete(): print "Complete",
    print "{:3}: Input: {:3} -  output:{}".format(edge.name, in_name, out_name)
    # print "%-3s: Input: %-3s  -   output: %s" % (edge.name, in_name, out_name)

user_solver = UserSolver(problem, False)
user_solver.solve_system()

for n in range(12):
    edge = problem.edge_at(n)
    input_pressure = edge.input_node.get_pressure('psi')
    flow = edge.get_vol_flow('gpm')
    output_pressure = edge._output_node.get_pressure('psi')
    templa = "{:3}: from {:5.2f} psi flows {:.2f} gpm to {:5.2f} psi"
    print templa.format(edge.name, input_pressure, flow, output_pressure)

