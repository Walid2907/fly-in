from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from models import Zone, Connection, Data, Drone
from pprint import pprint


class Graph:
    def __init__(self, data: Data) -> None:
        self.zones: Dict[str, Zone] = data.zones
        self.nb_drones: int = data.nb_drones
        self.start: Zone = self._find_start()
        self.end: Zone = self._find_end()
        self.drones: List[Drone] = []
        self.routes = []
        # dict for the node and what node it next to it (neighbors)
        '''
        each zone will have list of tiuples that stores the neibhor zone
        and the connction between them
        '''
        self.adjacency: Dict[Zone, List[Connection]] = defaultdict(list)
        '''
        call the function that will actually make the neighbors for each zone
        '''
        self._make_Edges(data)
        self._initialize_drones()

    # function to find the start zone
    def _find_start(self) -> Zone:
        for zone in self.zones.values():
            if zone.is_start:
                return zone
        raise MapError("No start zone found")

    # function to find the end zone
    def _find_end(self) -> Zone:
        for zone in self.zones.values():
            if zone.is_end:
                return zone
        raise MapError("No end zone found")

    def _make_Edges(self, data: Data) -> None:
        for connection in data.connections:
            # skip blocked zones
            if connection.zone1.zone_type == "blocked":
                continue
            if connection.zone2.zone_type == "blocked":
                continue
            # add both directions because the connections are bidirectional
            self.adjacency[connection.zone1].append((connection.zone2, connection))
            self.adjacency[connection.zone2].append((connection.zone1, connection))
    
    def _initialize_drones(self) -> None:
        """Spawn all drones at the start hub.

        Raises:
            ValueError: If start_hub has not been set yet.
        """
        if not self.start:
            raise ValueError("Cannot initialize drones without a start_hub.")
        for i in range(1, self.nb_drones + 1):
            self.drones.append(Drone(drone_id=i, current_zone=self.start))
    
    def get_neighbors(self, zone: Zone) -> List[Tuple[Zone, Connection]]:
        # Return all neighbors of a zone
        return self.adjacency[zone]

    def get_connection(self, a: Zone, b: Zone) -> Optional[Connection]:
        # Return the connection between two zones
        for neighbor, conn in self.adjacency[a]:
            if neighbor == b:
                return conn
        return None

