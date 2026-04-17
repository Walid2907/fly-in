from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class MapError(Exception):
    """Exception raised when Map parsing or validation fails."""


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
    is_start: bool
    is_end: bool
    zone_type: ZoneType
    max_drones: int
    color: str | None

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Zone):
            return False
        return self.name == other.name


@dataclass
class Connection:
    zone1: Zone
    zone2: Zone
    max_link_capacity: int = 1


@dataclass(frozen=True)
class Data:
    nb_drones: int
    zones: Dict[str, Zone]
    connections: List[Connection]


# modify this piece of shit
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
    def __init__(self, data: Data) -> None:
        self.nb_drones: int = data.nb_drones
        self.start: Zone = self.find_start(data)
        self.end: Zone = self.find_end(data)
        # a dict for the node and what node it next to it
        self.adjacency: Dict[Zone, List[Tuple[Zone, Connection]]] = defaultdict(list)
        self.make_Edges(data)

    def find_start(self, data: Data) -> Zone:
        for zone in data.zones.values():
            if zone.is_start:
                return zone
        raise MapError("No start zone found")

    def find_end(self, data: Data) -> Zone:
        for zone in data.zones.values():
            if zone.is_end:
                return zone
        raise MapError("No end zone found")

    def make_Edges(self, data: Data) -> None:
        for connection in data.connections:
            # skip blocked zones
            if connection.zone1.zone_type.value == "blocked":
                continue
            if connection.zone2.zone_type.value == "blocked":
                continue
            # add both directions because the connections are bidirectional
            self.adjacency[connection.zone1].append((connection.zone2, connection))
            self.adjacency[connection.zone2].append((connection.zone1, connection))
    
    def get_neighbors(self, zone: Zone) -> List[Tuple[Zone, Connection]]:
        # Return all neighbors of a zone
        return self.adjacency[zone]

    def get_connection(self, a: Zone, b: Zone) -> Optional[Connection]:
        # Return the connection between two zones
        for neighbor, conn in self.adjacency[a]:
            if neighbor == b:
                return conn
        return None

    def movement_cost(self, zone: Zone) -> int:
        # Return the turn cost to move inside a zone
        if zone.zone_type.value == "restricted":
            return 2
        return 1  # normal and priority both cost 1 turn

    # test path finder
    def dijkstra(self, start: Zone, end: Zone) -> Optional[List[Zone]]:
        import heapq
        # (cost, zone_name) → to avoid comparing Zone objects
        heap: List[Tuple[int, str]] = [(0, start.name)]
        costs: Dict[str, int] = {start.name: 0}
        prev: Dict[str, Optional[str]] = {start.name: None}

        while heap:
            cost, name = heapq.heappop(heap)
            zone = self.zones[name]  # you'll need access to zones dict

            if zone == end:
                return self._reconstruct_path(prev, start, end)

            for neighbor, conn in self.get_neighbors(zone):
                new_cost = cost + self.movement_cost(neighbor)
                if neighbor.name not in costs or new_cost < costs[neighbor.name]:
                    costs[neighbor.name] = new_cost
                    prev[neighbor.name] = name
                    heapq.heappush(heap, (new_cost, neighbor.name))
        return None
