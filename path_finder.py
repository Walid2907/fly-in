from Graph import Graph
from models import Zone
from typing import Dict, List, Set, Tuple
import heapq
class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        # Reservations: maps (zone, time) to the number of drones occupying it
        self.node_reservations: Dict[Tuple[Zone, int], int] = {}
        # Max time allowed to prevent infinite loops when drones get trapped
        self.max_time_allowed = 1000
    
    def is_reserved(self, zone: Zone, time: int) -> bool:
        capacity = zone.effective_capacity()
        occupied = self.node_reservations.get((zone, time), 0)
        return occupied >= capacity
    def dijkstra(self, start_time: int = 0) -> List[Tuple[Zone, int]]:
        start = self.graph.start
        end = self.graph.end
        
        # Track distances using (Zone, time) as the state
        distances: Dict[Tuple[Zone, int], int] = {}
        previous: Dict[Tuple[Zone, int], Tuple[Zone, int] | None] = {}
        
        start_state = (start, start_time)
        distances[start_state] = start_time
        previous[start_state] = None
        
        # Priority Queue: (current_distance, tie-breaker counter, Zone, current_time)
        pq: List[tuple[int, int, Zone, int]] = []
        counter = 0
        
        heapq.heappush(pq, (start_time, counter, start, start_time))
        visited: Set[Tuple[Zone, int]] = set()
        
        while pq:
            current_distance, _, current_zone, current_time = heapq.heappop(pq)
            state = (current_zone, current_time)
            
            if state in visited:
                continue
                
            visited.add(state)
            # Reached the end zone! We can build the path and return.
            if current_zone == end:
                path = []
                curr = state
                while curr is not None:
                    path.append(curr)
                    curr = previous[curr]
                path.reverse()
                return path
            if current_time > self.max_time_allowed:
                continue
            # Check neighbors including the WAIT action
            neighbors_to_check = []
            
            # 1. Wait action: Drone stays in current zone for 1 time step
            neighbors_to_check.append((current_zone, current_time + 1))
            
            # 2. Move actions: Drone moves to an adjacent zone
            for neighbor, connection in self.graph.adjacency[current_zone]:
                move_time = current_time + neighbor.movement_cost
                neighbors_to_check.append((neighbor, move_time))
            for neighbor_zone, new_time in neighbors_to_check:
                # Discard neighbor if that zone is fully occupied at 'new_time'
                if self.is_reserved(neighbor_zone, new_time):
                    continue
                
                new_state = (neighbor_zone, new_time)
                
                # Check if this new path is shorter/faster
                if new_time < distances.get(new_state, float('inf')):
                    distances[new_state] = new_time
                    previous[new_state] = state
                    
                    counter += 1
                    heapq.heappush(pq, (new_time, counter, neighbor_zone, new_time))
        return []
    
    def update_reserved(self, path: List[Tuple[Zone, int]]):
        for zone, time in path:
            # Increase the occupancy for this zone at this specific time
            self.node_reservations[(zone, time)] = self.node_reservations.get((zone, time), 0) + 1
    def loop(self):
        drones = self.graph.nb_drones
        for i in range(drones):
            # 1. Calculate the optimal path for Drone 'i' avoiding existing reservations
            path_with_times = self.dijkstra(start_time=0)
            
            if not path_with_times:
                print(f"Warning: Drone {i} could not find a path!")
                continue
                
            # 2. Extract just the Zones for our graph routes
            self.graph.routes.append(path_with_times)
            
            # 3. Reserve the nodes in space-time so the next drone avoids them
            self.update_reserved(path_with_times)
