from dataclasses import dataclass
from typing import Dict, List
from classes import ZoneType, Zone, Connection




class MapError(Exception):
    """Exception raised when Map parsing or validation fails."""


# @dataclass
# class Zone:
#     name: str
#     x: int
#     y: int
#     is_start: bool = False
#     is_end: bool = False
#     zone_type: ZoneType = ZoneType.normal
#     max_drones: int = 1

# @dataclass
# class Connection:
#     zone1: Zone
#     zone2: Zone
#     max_link_capacity: int = 1


VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

@dataclass
class Data:
    nb_drones: int
    hubs: Dict[str, Zone]
    connections: List[Connection]


def parse_connection(value: str, line_num: int) -> Connection:
    zone1, zone2 = value.split("-")
    zone1, zone2 = zone1.strip(), zone2.strip()


def parser(file_name: str) -> Data:
    hubs: Dict[str, Zone] = {}
    connections: List[Connection] = []
    nb_drones: Optional[int] = None
    seen_connections: set[Connection] = set()
    start_count = 0
    end_count = 0
    with open(file_name, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if ":" not in line:
            raise MapError(f"Line {line_num}: Expected 'key:value'")
        
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "nb_drones":
            if not value.isdigit() or int(value) < 1:
                raise MapError(f"Line {line_num}: nb_drones must be a positive integer")
            nb_drones = int(value)
        
        elif key == "connection":
            zone1, zone2, max_link_capacity = parse_connection(value, line_num)
            for zone_name in (zone1, zone2):
                if zone_name not in hubs:
                    raise MapError(f"Zone unknown '{zone_name}' in Line {line_num}")
            conn_key = frozenset([zone1, zone2])
            if conn_key in seen_connections:
                raise MapError(f"Line {line_num}: Duplicate connection '{conn.zone1}-{conn.zone2}'")
            seen_connections.add(conn_key)
            connections.append(conn)


# maze_data = parser("01_maze_nightmare.txt")
# print(f"Number of drones: {maze_data.nb_drones}\n")

# # Print hubs in the order stored
# print("Hubs:")
# for key, hub in maze_data.hubs.items():
#     attrs = ", ".join(f"{k}={v}" for k, v in hub["attributes"].items())
#     print(f"  {key}: {hub['name']} ({hub['x']}, {hub['y']}) [{attrs}]")

# # Print connections
# print("\nConnections:")
# for conn in maze_data.connections:
#     print(f"  {conn}")
