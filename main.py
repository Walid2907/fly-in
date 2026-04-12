from parser import Map_parser
from dataclasses import asdict
from classes import Graph
from pprint import pprint


if __name__ == "__main__":
    try:
        # parse the Map
        parsed = Map_parser("01_linear_path.txt")
        # get the parsed data
        data = parsed.parser()
        # build my Graph
        graph = Graph(data)
        pprint(graph.adjacency[data.zones["goal"]])
    except Exception:
        pass
