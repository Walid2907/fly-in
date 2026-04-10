from typing import Dict, List, Any, Optional
from classes import ZoneType, Zone, Connection, Data, MapError


VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def parse_metadata(attrs_str: str, line_num: int) -> Dict[str, Any]:
    attrs_dict: Dict[str, Any] = {}
    for var in attrs_str.split():
        if "=" not in var:
            raise MapError(f"Line {line_num}: Invalid metadat syntax")
        key, value = var.split("=", 1)
        if value.isdigit():
            attrs_dict[key] = int(value)
        else:
            attrs_dict[key] = value
    return attrs_dict


def parse_zone(hub_type: str, value: str, line_num: int) -> Zone:
    metadata: Dict[str, Any] = {}
    is_start = False
    is_end = False
    if hub_type == "start_hub":
        is_start = True
    elif hub_type == "end_hub":
        is_end = True

    if "[" in value:
        zone, attrs = value.split("[", 1)
        if not attrs.endswith("]"):
            raise MapError(f"Line {line_num}: Unclosed metadata bracket")
        attrs = attrs.removesuffix("]").strip()
        metadata = parse_metadata(attrs, line_num)
    else:
        zone = value.strip()

    zone_info = zone.strip().split()
    if len(zone_info) != 3:
        raise MapError(f"Line {line_num}: Expected 'name x y', got '{value.strip()}'")

    zone_name, xs, ys = zone_info
    try:
        x, y = int(xs), int(ys)
    except ValueError:
        raise MapError(f"Line {line_num}: Coordinates must be integers")

    try:
        zone_type = ZoneType(str(metadata.get("zone", "normal")))
    except ValueError:
        raise MapError(f"Line {line_num}: Invalid zone type '{str(metadata.get('zone', 'normal'))}'. Must be one of {[e.value for e in ZoneType]}")

    max_drones = metadata.get("max_drones", 1)
    if not isinstance(max_drones, int) or max_drones < 1:
        raise MapError(f"Line {line_num}: max_drones must be a positive intger")

    if metadata.get("color", None) is not None:
        color = str(metadata.get("color", None))
    else:
        color = None

    return Zone(
        name=zone_name,
        x=x,
        y=y,
        is_start=is_start,
        is_end=is_end,
        zone_type=zone_type,
        max_drones=max_drones,
        color=color
    )


# parsing the connection part
def parse_connection(value: str, line_num: int) -> tuple[str, str, int]:
    # to store the metadata as key: value
    metadata: Dict[str, Any] = {}
    if "[" in value:
        zones, attrs = value.split("[", 1)
        if not attrs.endswith("]"):
            raise MapError(f"Line {line_num}: Unclosed metadata bracket")
        attrs = attrs.removesuffix("]").strip()
        metadata = parse_metadata(attrs, line_num)  # to add
    else:
        zones = value.strip()

    if "-" not in zones:
        raise MapError(f"Line {line_num}: Connection must be 'zone1-zone2', got '{value}'")
    # simple parse add the metadata parse first
    zone1, zone2 = zones.split("-", 1)
    zone1, zone2 = zone1.strip(), zone2.strip()

    if not zone1 or not zone2:
        raise MapError(f"Line {line_num}: Connection has empty zone name")
    max_link_capacity = metadata.get("max_link_capacity", 1)
    if not isinstance(max_link_capacity, int) or max_link_capacity < 1:
        raise MapError(f"Line {line_num}: max_link_capacity must be a positive integer")

    return zone1, zone2, max_link_capacity


# main parsing manager
def parser(file_name: str) -> Data:
    zones: Dict[str, Zone] = {}
    connections: List[Connection] = []
    nb_drones: Optional[int] = None
    seen_connections: set[frozenset] = set()
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
                    if zone_name not in zones:
                        raise MapError(f"Zone unknown '{zone_name}' in Line {line_num}")
                conn_key = frozenset([zone1, zone2])
                if conn_key in seen_connections:
                    raise MapError(f"Line {line_num}: Duplicate connection '{zone1}-{zone2}'")
                seen_connections.add(conn_key)
                connections.append(Connection(
                        zone1=zones[zone1],
                        zone2=zones[zone2],
                        max_link_capacity=max_link_capacity,
                    ))
            elif key in ("hub", "start_hub", "end_hub"):
                zone = parse_zone(key, value, line_num)

                if zone.name in zones:
                    raise MapError(f"Line {line_num}: Duplicated zone name '{zone.name}'")

                if key == "start_hub":
                    start_count += 1
                    if start_count > 1:
                        raise MapError(f"Line {line_num}: Multiples start zone")

                elif key == "end_hub":
                    end_count += 1
                    if end_count > 1:
                        raise MapError(f"Line {line_num}: Multiples end zone")

                zones[zone.name] = zone
            else:
                raise MapError(f"Line {line_num}: unknown key '{key}'")

    if nb_drones is None:
        raise MapError("Missing 'nb_drones' definition")
    if start_count == 0:
        raise MapError("Missing 'start_hub' definition")
    if end_count == 0:
        raise MapError("Missing 'end_hub' definition")

    return Data(nb_drones=nb_drones, zones=zones, connections=connections)
