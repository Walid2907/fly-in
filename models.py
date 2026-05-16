from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional



# Enum class that defines the zones types
class ZoneType(str, Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"


# a data class so save the Zone metadata (Nodes)
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
    
    @property
    def movement_cost(self) -> int:
        # return 1 for normal and priority and return 2 for restricted
        # raise error for the blocked zones
        if self.zone_type == ZoneType.blocked:
            raise ValueError(f"Zone '{self.name}' is BLOCKED and cannot be entered.")
        if self.zone_type == ZoneType.restricted:
            return 2
        return 1

    
    def effective_capacity(self) -> int:
        """Return actual capacity, with start/end exception.

        The start and end hubs accept unlimited drones by spec.

        Returns:
            999 for start/end zones, max_drones otherwise.
        """
        if self.is_start or self.is_end:
            return 999
        return self.max_drones

    # __hash__ is used so we can use the class in sets and dicts in our code
    # for easier acces
    def __hash__(self) -> int:
        return hash(self.name)

    # the __eq__ is used so i'm  able to check if two zones have the same name
    # so we don't have duplicated names
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Zone):
            return False
        return self.name == other.name


# data class to store the connection (Edges)
@dataclass
class Connection:
    zone1: Zone
    zone2: Zone
    max_link_capacity: int = 1


@dataclass
class Drone:
    """Represents a single drone and its routing state."""
    drone_id: int
    current_zone: Zone
    defined_path: List[Zone] = field(default_factory=list)
    path_index: int = 0
    arrival_turn: int = 0  # 0 = drone not in transit, N = must land at N turns

    @property
    def Drone_ID(self) -> str:
        """Return the drone ID output formatted ."""
        return f"D{self.drone_id}"

    def move_to(self, next_zone: Zone) -> None:
        """Update current position and record the move in history.

        Args:
            next_zone: The zone this drone is moving into.
        """
        self.current_zone = next_zone
        self.path_index += 1


# Data class to save all the previous data for easier acces inside our code
@dataclass(frozen=True)
class Data:
    nb_drones: int
    zones: Dict[str, Zone]
    connections: List[Connection]
