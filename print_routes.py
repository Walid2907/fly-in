from parser import Map_parser
from Graph import Graph
from path_finder import Pathfinder
parsed = Map_parser("maps/easy/03_basic_capacity.txt")
data = parsed.parser()
graph = Graph(data)
pf = Pathfinder(graph)
pf.loop()
for route in graph.routes:
    print([(z.name, t) for z, t in route])
