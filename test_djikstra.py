from pprint import pprint
from heapq import heapify, heappop, heappush


class Graph:
    def __init__(self, graph=None):
        if graph == None:
            self.graph = {}
        else:
            self.graph = graph
    
    def add_edge(self, node1, node2, weight):
        if node1 not in self.graph:
            self.graph[node1] = {}
        if node2 not in self.graph:
            self.graph[node2] = {}
        
        self.graph[node1][node2] = weight
        self.graph[node2][node1] = weight

    def djikstra(self, start):
        distances = {node: float('inf') for node in self.graph}
        previous = {node: None for node in self.graph}
        distances[start] = 0
        visited = set()
        priority_queue = [(0, start)]
        heapify(priority_queue)

        while priority_queue:
            current_distance, current_node = heappop(priority_queue)

            if current_node in visited:
                continue 
            visited.add(current_node)
            for neighbor, weight in self.graph[current_node].items():
                dist_holder = current_distance + weight
                if dist_holder < distances[neighbor]:
                    distances[neighbor] = dist_holder
                    previous[neighbor] = current_node
                    heappush(priority_queue, (dist_holder, neighbor))
        
        return distances, previous
    
    def path(self, start, end):
        distances, previous = self.djikstra(start)

        path = []
        current = end

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()
        return path
            




graph = {
    "A": {"B": 3, "C": 3},
    "B": {"A": 3, "D": 3.5, "E": 2.8},
    "C": {"A": 3, "E": 2.8, "F": 3.5},
    "D": {"B": 3.5, "E": 3.1, "G": 10},
    "E": {"B": 2.8, "D": 3.1, "C": 2.8, "G": 7},
    "F": {"C": 3.5, "G": 2.5},
    "G": {"F": 2.5, "D": 10, "E": 7},
}
G = Graph(graph)
pprint(G.path("B", "G"))
