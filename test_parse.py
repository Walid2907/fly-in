from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Hub:
    """Represents a zone/hub in the drone network."""

    name: str
    x: int
    y: int
    hub_type: str  # start_hub, end_hub, hub
    zone: str = "normal"
    color: Optional[str] = None
    max_drones: int = 1


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones."""

    zone1: Hub
    zone2: Hub
    max_link_capacity: int = 1


@dataclass
class Data:
    """Holds the fully parsed drone simulation data."""

    nb_drones: int
    hubs: Dict[str, Hub] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)


VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def parse_metadata(attrs_str: str, line_num: int) -> Dict[str, object]:
    """Parse a metadata string like 'zone=restricted color=red max_drones=2'.

    Args:
        attrs_str: The raw string inside the brackets.
        line_num: Current line number for error reporting.

    Returns:
        A dictionary of key-value pairs from the metadata.
    """
    attr_dict: Dict[str, object] = {}
    for token in attrs_str.split():
        if "=" not in token:
            raise ValueError(
                f"Line {line_num}: Invalid metadata token '{token}'"
            )
        k, v = token.split("=", 1)
        if v.isdigit():
            attr_dict[k] = int(v)
        else:
            attr_dict[k] = v
    return attr_dict


def parse_hub(
    hub_type: str, value: str, line_num: int
) -> Hub:
    """Parse a hub line value into a Hub object.

    Args:
        hub_type: One of 'hub', 'start_hub', 'end_hub'.
        value: Everything after the colon on the line.
        line_num: Current line number for error reporting.

    Returns:
        A Hub dataclass instance.
    """
    metadata: Dict[str, object] = {}

    if "[" in value:
        parts, attrs_raw = value.split("[", 1)
        if not attrs_raw.endswith("]"):
            raise ValueError(
                f"Line {line_num}: Unclosed metadata bracket"
            )
        metadata = parse_metadata(attrs_raw[:-1].strip(), line_num)
    else:
        parts = value

    name_parts = parts.strip().split()
    if len(name_parts) != 3:
        raise ValueError(
            f"Line {line_num}: Expected 'name x y', got '{parts.strip()}'"
        )

    name, x_str, y_str = name_parts

    try:
        x, y = int(x_str), int(y_str)
    except ValueError:
        raise ValueError(
            f"Line {line_num}: Coordinates must be integers"
        )

    zone = str(metadata.get("zone", "normal"))
    if zone not in VALID_ZONE_TYPES:
        raise ValueError(
            f"Line {line_num}: Invalid zone type '{zone}'. "
            f"Must be one of {VALID_ZONE_TYPES}"
        )

    max_drones = metadata.get("max_drones", 1)
    if not isinstance(max_drones, int) or max_drones < 1:
        raise ValueError(
            f"Line {line_num}: max_drones must be a positive integer"
        )

    color_val = metadata.get("color", None)
    color = str(color_val) if color_val is not None else None

    return Hub(
        name=name,
        x=x,
        y=y,
        hub_type=hub_type,
        zone=zone,
        color=color,
        max_drones=max_drones,
    )


def parse_connection(value: str, line_num: int) -> tuple[str, str, int]:
    """Parse a connection line value into zone names and capacity.

    Args:
        value: Everything after the colon on the line.
        line_num: Current line number for error reporting.

    Returns:
        A tuple of (zone1_name, zone2_name, max_link_capacity).
    """
    metadata: Dict[str, object] = {}

    if "[" in value:
        parts, attrs_raw = value.split("[", 1)
        if not attrs_raw.endswith("]"):
            raise ValueError(
                f"Line {line_num}: Unclosed metadata bracket"
            )
        metadata = parse_metadata(attrs_raw[:-1].strip(), line_num)
    else:
        parts = value

    parts = parts.strip()
    if "-" not in parts:
        raise ValueError(
            f"Line {line_num}: Connection must be 'zone1-zone2', got '{parts}'"
        )

    zone1, zone2 = parts.split("-", 1)
    zone1, zone2 = zone1.strip(), zone2.strip()

    if not zone1 or not zone2:
        raise ValueError(
            f"Line {line_num}: Connection has empty zone name"
        )

    max_link_capacity = metadata.get("max_link_capacity", 1)
    if not isinstance(max_link_capacity, int) or max_link_capacity < 1:
        raise ValueError(
            f"Line {line_num}: max_link_capacity must be a positive integer"
        )

    return zone1, zone2, max_link_capacity


def parser(file_name: str) -> Data:
    """Parse a drone simulation map file into a Data object.

    Args:
        file_name: Path to the input map file.

    Returns:
        A Data object with all parsed information.

    Raises:
        ValueError: On any parsing or validation error.
    """
    hubs: Dict[str, Hub] = {}
    connections: List[Connection] = []
    nb_drones: Optional[int] = None
    seen_connections: set = set()
    start_count = 0
    end_count = 0

    with open(file_name, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                raise ValueError(
                    f"Line {line_num}: Expected 'key: value', got '{line}'"
                )

            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "nb_drones":
                if not value.isdigit() or int(value) < 1:
                    raise ValueError(
                        f"Line {line_num}: nb_drones must be a positive integer"
                    )
                nb_drones = int(value)

            elif key == "connection":
                zone1_name, zone2_name, max_link_capacity = parse_connection(value, line_num)

                # Check both zones exist and resolve to Hub objects
                for zone_name in (zone1_name, zone2_name):
                    if zone_name not in hubs:
                        raise ValueError(
                            f"Line {line_num}: Unknown zone '{zone_name}'"
                        )

                # Check for duplicate connections (a-b == b-a)
                conn_key = frozenset([zone1_name, zone2_name])
                if conn_key in seen_connections:
                    raise ValueError(
                        f"Line {line_num}: Duplicate connection "
                        f"'{zone1_name}-{zone2_name}'"
                    )
                seen_connections.add(conn_key)
                connections.append(Connection(
                    zone1=hubs[zone1_name],
                    zone2=hubs[zone2_name],
                    max_link_capacity=max_link_capacity,
                ))

            elif key in ("hub", "start_hub", "end_hub"):
                hub = parse_hub(key, value, line_num)

                if hub.name in hubs:
                    raise ValueError(
                        f"Line {line_num}: Duplicate zone name '{hub.name}'"
                    )

                if key == "start_hub":
                    start_count += 1
                    if start_count > 1:
                        raise ValueError(
                            f"Line {line_num}: Multiple start_hub definitions"
                        )
                elif key == "end_hub":
                    end_count += 1
                    if end_count > 1:
                        raise ValueError(
                            f"Line {line_num}: Multiple end_hub definitions"
                        )

                hubs[hub.name] = hub

            else:
                raise ValueError(
                    f"Line {line_num}: Unknown key '{key}'"
                )

    if nb_drones is None:
        raise ValueError("Missing 'nb_drones' definition")
    if start_count == 0:
        raise ValueError("Missing 'start_hub' definition")
    if end_count == 0:
        raise ValueError("Missing 'end_hub' definition")

    return Data(nb_drones=nb_drones, hubs=hubs, connections=connections)


if __name__ == "__main__":
    import sys

    file = sys.argv[1] if len(sys.argv) > 1 else "01_maze_nightmare.txt"

    try:
        data = parser(file)
    except ValueError as e:
        print(f"Parsing error: {e}")
        sys.exit(1)

    print(f"Number of drones: {data.nb_drones}\n")

    print("Hubs:")
    for hub in data.hubs.values():
        print(
            f"  [{hub.hub_type}] {hub.name} ({hub.x}, {hub.y}) "
            f"zone={hub.zone} color={hub.color} max_drones={hub.max_drones}"
        )

    print("\nConnections:")
    for conn in data.connections:
        print(
            f"  {conn.zone1.name} <-> {conn.zone2.name} "
            f"(max_link_capacity={conn.max_link_capacity})"
        )