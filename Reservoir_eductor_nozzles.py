from hydraulics.edges import ANSIPipe, Nozzle
from hydraulics.eductor import Eductor
from hydraulics.nodes import EndNode, EductorInlet, EductorOutlet, \
    ConnectionNode
from hydraulics.pipe_network import PNetwork

n_types = "eiocece"
node_dict = {'e': EndNode, 'i': EductorInlet, 'o': EductorOutlet,
             'c': ConnectionNode}

elevations = [20, 0, 0, 0, 0, 0, 0]
problem = PNetwork()

for index in range(len(elevations)):
    current_node = node_dict[n_types[index]]()
    current_node.set_pressure(0, 'psi')
    current_node.set_elevation(elevations[index], 'm')
    current_node.name = "{}{}".format(n_types[index], index)
    problem.add_node(current_node)


for node in problem.get_nodes():
    node_elev = node.get_elevation('m')
    print "{}: type {}   Elev:{} m".format(node.name, type(node), node_elev)

# SET EDGES
#   SET PIPES
lengths = (30, 1, 1)
diams = (2, 1, 1)
pipes = []
for i in range(len(diams)):
    cur_pipe = ANSIPipe()
    cur_pipe.nominal_diameter = diams[i]
    cur_pipe.diam_unit = 'in'
    cur_pipe.set_length(lengths[i], 'm')
    cur_pipe.schedule = '80'
    pipes.append(cur_pipe)

#   NOZZLES
nozzles = []
for i in range(2):
    cur_nozzle = Nozzle()
    cur_nozzle.set_factor(3.2, 'gpm/psi^0.5')
    cur_nozzle.set_required_pressure(15, 'psi')
    nozzles.append(cur_nozzle)

# SET EDUCTORS
eductors = []
cur_eductor = Eductor()
cur_eductor.set_factor(7.0, 'gpm/psi^0.5')
cur_eductor.concentration = 0.03
eductors.append(cur_eductor)

edge_types = "pepnpn"
typ_dict = {'p': pipes, 'n': nozzles, 'e': eductors}
for carac in edge_types:
    problem.add_edge(typ_dict[carac].pop(0))
    problem.set_pipe_name(-1, "{}{}".format(carac,
                                            len(problem.get_edges()) - 1))

# SET CONNECTIVITY
conect_nodes = [[0, 1], [1, 2], [2, 3], [3, 4], [3, 5], [5, 6]]
for i in range(len(problem.get_edges())):
    problem.connect_node_downstream_edge(conect_nodes[i][0], i)
    problem.connect_node_upstream_edge(conect_nodes[i][1], i)

for n in range(6):
    edge = problem.edge_at(n)
    in_name = edge.input_node.name
    out_name = edge._output_node.name
    if edge.is_complete(): print "Complete",
    print "{}: Input: {} -  output:{}".format(edge.name, in_name, out_name)

flow_equations = []


def aporte(edge_index, node_index):
    edge = problem.edge_at(edge_index)
    if edge.input_node == problem.node_at(node_index):
        return -1
    if edge.output_node == problem.node_at(node_index):
        if isinstance(edge, Eductor):
            return 1.03
        return 1
    return 0

for elem in [1, 2, 3, 5]:
    equation = [aporte(i, elem) for i in range(len(problem.get_edges()))]
    print equation
# eq_2 = [aporte(i, 2) for i in range(len(problem.get_edges()))]
# print eq_1
# print eq_2