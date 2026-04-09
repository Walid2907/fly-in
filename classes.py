from dataclasses import dataclass, field
from enum import Enum


class ZoneType(str, Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"

@dataclass
class Zone:
    name: str
    x: int
    y: int
    is_start: bool = False
    is_end: bool = False
    zone_type: ZoneType = ZoneType.normal
    max_drones: int = 1

@dataclass
class Connection:
    zone1: Zone
    zone2: Zone
    max_link_capacity: int = 1


@dataclass
class Drone:
    drone_id: int
    current_zone: Zone
    path: List[Zone] = field(default_factory=list)
    path_index: int = 0

    @property
    def get_id(self) -> int:
        return self.drone_id
    
    @property
    def get_current_zone(self) -> Zone:
        return self.current_zone

    def move_to(self, next_zone: Zone) -> None:
        self.current_zone = next_zone
        if self.path_index < len(path):
            self.path_index += 1

class Graph:
    def __init__(self, edges: list[tuple[Zone, Zone]]):
        self.edges = edges
        self.edges_dict = {}
        for start, end in self.edges:
            if start in self.edges_dict:
                self.edges_dict[start].append(end)
            else:
                self.edges_dict[start] = [end]


    def get_path(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        elif start not in self.edges_dict:
            return []
        paths = []
        for node in self.edges_dict[start]:
            if node not in path:
                new_path = self.get_path(node, end, path)
                for p in new_path:
                    paths.append(p)
        return paths

# routes = [("hub", "roof1"),
#           ("hub", "corridorA"),
#           ("roof1", "roof2"),
#           ("roof2", "goal"),
#           ("corridorA", "tunnelB"),
#           ("tunnelB", "goal")]
#
# graph = Graph(routes)
# print(graph.get_path("hub", "goal"))