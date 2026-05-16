from collections import deque

graph = {
    'A': ['B', 'C', 'D'],

    'B': ['E', 'F'],
    'C': ['G', 'H'],
    'D': ['I'],

    'E': ['J', 'K'],
    'F': ['L', 'C'],      # cycle back to C

    'G': ['M'],
    'H': ['N', 'O'],

    'I': ['P', 'Q'],

    'J': [],
    'K': ['R'],

    'L': ['S'],
    'M': ['T', 'B'],      # cycle back to B

    'N': [],
    'O': ['U'],

    'P': ['V'],
    'Q': ['W', 'X'],

    'R': ['Y'],
    'S': [],

    'T': ['Z'],
    'U': ['D'],           # cycle back to D

    'V': [],
    'W': [],

    'X': ['H'],           # cycle back to H

    'Y': [],
    'Z': []
}


# def dfs(graph, start, end):
#     stack = deque()
#     visited = set()
#     stack.append(start)
    
#     while stack:
#         current = stack.pop()
#         if current in visited:
#             continue
        
#         visited.add(current)
        
#         print(current)
        
#         if current == end:
#             return True
        
#         for neighbor in reversed(graph[current]):
#             stack.append(neighbor)
    
#     return False
    
# dfs(graph, 'A', 'Z')

import heapq
from typing import List

def djikstra(graph, start, end):
    pq : List = []
