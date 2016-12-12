from hydraulics.nodes import EndNode, ConnectionNode
from hydraulics.pipe_network import PNetwork
from hydraulics.pipes import Pipe

elevations = [100, 85, 65, 65, 70, 70]
names = [0, 1, 2, 3, 4, 5]
problem = PNetwork()
# SET NODES
#  END NODES
for cont in range(4):
    cur_node = EndNode()
    cur_node.set_elevation(elevations[cont], 'm')
    cur_node.name = names[cont]
    problem.add_node(cur_node)

node_count = len(elevations)
end_count = 4

for node_index in range(end_count, node_count):
    cur_node = ConnectionNode()
    cur_node.set_pressure(0, 'psi')
    cur_node.set_elevation(elevations[node_index], 'm')
    cur_node.name = names[node_index]
    problem.add_node(cur_node)

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
    problem.add_pipe(cur_pipe)


# SET CONNECTIVITY
problem.connect_node_downstream_pipe(4, 2)
problem.connect_node_upstream_pipe(4, 1)
problem.connect_node_upstream_pipe(4, 0)
problem.connect_node_downstream_pipe(0, 0)
problem.connect_node_downstream_pipe(1, 1)
problem.connect_node_upstream_pipe(5, 2)
problem.connect_node_downstream_pipe(5, 3)
problem.connect_node_downstream_pipe(5, 4)
problem.connect_node_upstream_pipe(2, 3)
problem.connect_node_upstream_pipe(3, 4)

# SET INITIAL HEAD GUESS

print problem.get_pipes()[0].get_gpm_flow()
print "That was pipe #0"
print

problem.solve_shit()

end_flows = []

for cont5 in range(pipe_count):
    end_flows.append(problem.get_pipes()[cont5].get_gpm_flow())

print
print "Pipe   Flow (gpm)"
for cont in range(pipe_count):
    print " %s      %9.4f" % (problem.get_pipes()[cont].name, end_flows[cont])
print
print "Node  Pressures"
for cont in range(node_count):
    print " %s    %6.3f psi" % (problem.get_nodes()[cont].name,
                                problem.get_nodes()[cont].get_pressure('psi'))
