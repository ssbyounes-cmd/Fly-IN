from typing import Any


class Parser:
    @staticmethod
    def __parsing_map(filename: str) -> dict[str, list[tuple[int, str]]]:
        with open(filename, "r") as file:
            known_keys = ["nb_drones", "start_hub", "hub", "end_hub", "connection"]
            data = {}
            first_line = False
            for i, line in enumerate(file, 1):
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if "#" in line:
                    line = line.split("#", 1)[0].strip()
                if ":" not in line or len(line.split(":")) != 2:
                    raise ValueError(f"Line {i}: Invalid line: {line}")
                key, value = line.split(":", 1)
                if not first_line:
                    if key.strip() != "nb_drones":
                        raise ValueError(f"Line {i}: First line must specify nb_drones")
                    first_line = True
                if key.strip() not in known_keys:
                    raise ValueError(f"Line {i}: Unknown attribute: {key}")
                if key.strip() in data:
                    data[key.strip()].append((i, value.strip()))
                else:
                    data[key.strip()] = [(i, value.strip())]
        return data

    @staticmethod
    def __parsing_zones(data: dict[str, list[tuple[int, str]]]) -> dict[str, Any]:
        # parsing nb_drones and validating its value
        parsed_data = {"nb_drones": 0, "zones": [], "zone_lines": {}}
        if len(data["nb_drones"]) != 1:
            raise ValueError(f"Line {data['nb_drones'][-1][0]}: nb_drones is defined more than once")
        try:
            value = int(data['nb_drones'][0][1])
            if value <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(f"Line {data['nb_drones'][0][0]}: Invalid value for nb_drones")
        parsed_data['nb_drones'] = int(data['nb_drones'][0][1])

        # parsing zones and validating their data
        for key in ['start_hub', 'hub', 'end_hub']:
            for i, value in data.get(key, []):
                if "[" in value:
                    metadata_ = value[value.index("["):].strip()
                    value = value[:value.index("[")].strip()
                    if not metadata_.endswith("]"):
                        raise ValueError(f"Line {i}: Invalid metadata format for {key} {value}")
                else:
                    metadata_ = ""
                parts = value.split()
                if len(parts) != 3:
                    raise ValueError(f"Line {i}: Invalid format for {key} {value}. Expected format: <name> <x> <y>")
                # checking for zone name duplicates
                if parts[0] in [zone["name"] for zone in parsed_data["zones"]]:
                    raise ValueError(f"Line {i}: Duplicate zone name \"{parts[0]}\" for {key} {value}")
                if "-" in parts[0]:
                    raise ValueError(f"Line {i}: Invalid zone name \"{parts[0]}\" for {key} {value}")
                # checking for valid coordinates
                try:
                    int(parts[1])
                    int(parts[2])
                except ValueError:
                    raise ValueError(f"Line {i}: Invalid coordinates for {key} {value}")
                # checking for metadata
                metadata = {}

                if metadata_:
                    metadata_ = metadata_[1:-1]  # strip metadata brackets
                    if len(metadata_.split()) > 3 or len(metadata_.split()) < 1:
                        raise ValueError(f"Line {i}: Invalid metadata format for {key} {value}")
                    meta_parts = metadata_.split()
                    for x in range(len(meta_parts)):
                        if len(meta_parts[x].split('=')) != 2:
                            raise ValueError(f"Line {i}: Invalid metadata format for {key} {value}")
                        m_key, m_value = meta_parts[x].split('=')
                        if m_key not in ['color', 'max_drones', 'zone']:
                            raise ValueError(f"Line {i}: Unknown metadata attribute \"{m_key}\" for {key} {value}")
                        if m_key == "zone" and m_value not in ["normal", "blocked", "restricted", "priority"]:
                            raise ValueError(f"Line {i}: Invalid zone type \"{m_value}\" for {key} {value}")
                        if m_key == "max_drones":
                            try:
                                try_value = int(m_value)
                                if try_value <= 0:
                                    raise ValueError
                            except ValueError:
                                raise ValueError(f"Line {i}: Invalid max_drones value \"{m_value}\" for {key} {value}")
                        if m_key == "max_drones" and key in {"start_hub", "end_hub"}:
                            if int(m_value) < parsed_data['nb_drones']:
                                raise ValueError(f"Line {i}: max_drones value \"{m_value}\" for {key} {value} must be greater than or equal to nb_drones")
                        if m_key in metadata:
                            raise ValueError(f"Line {i}: Duplicate metadata attribute \"{m_key}\" for {key} {value}")
                        if not m_value:
                            raise ValueError(f"Line {i}: Invalid metadata for {key} {value}")
                        metadata[m_key] = m_value
                if "max_drones" not in metadata and key in {"start_hub", "end_hub"}:
                    metadata["max_drones"] = parsed_data['nb_drones']

                parsed_data["zones"].append({"kind": key, "name": parts[0], "x": int(parts[1]), "y": int(parts[2]), **metadata})
                parsed_data["zone_lines"][parts[0]] = i

        # validating the number of start_hub and end_hub
        if sum(1 for x in parsed_data['zones'] if x['kind'] == "start_hub") != 1:
            raise ValueError("There must be exactly one start_hub")
        if sum(1 for x in parsed_data['zones'] if x['kind'] == "end_hub") != 1:
            raise ValueError("There must be exactly one end_hub")
        return parsed_data

    @staticmethod
    def __parsing_connections(data: dict[str, list[tuple[int, str]]], parsed_data: dict[str, Any]) -> dict[str, int | list[dict[str, Any]]]:
        # parsing connections and validating their data
        parsed_data["connections"] = []
        zone_names = [zone["name"] for zone in parsed_data["zones"]]
        for i, value in data.get('connection', []):
            if "[" in value:
                metadata_ = value[value.index("["):].strip()
                value = value[:value.index("[")].strip()
                if not metadata_.endswith("]"):
                    raise ValueError(f"Line {i}: Invalid metadata format for connection {value}")
            else:
                metadata_ = ""

            parts = value.split()
            if len(parts) != 1:
                raise ValueError(f"Line {i}: Invalid format for connection {value}. Expected format: <zone1>-<zone2>")
            if len(parts[0].split("-")) != 2:
                raise ValueError(f"Line {i}: Invalid format for connection {value}. Expected format: <zone1>-<zone2>")
            zone1, zone2 = parts[0].split("-")

            # checking for valid zone names and if they are defined before the connection
            if zone1 not in zone_names or zone2 not in zone_names:
                raise ValueError(f"Line {i}: Invalid zone name for connection {value}")
            else:
                line_zone1 = parsed_data["zone_lines"][zone1]
                line_zone2 = parsed_data["zone_lines"][zone2]
                if line_zone1 > i or line_zone2 > i:
                    raise ValueError(f"Line {i}: Connection {value} references undefined zone(s)")
            for connection in parsed_data["connections"]:
                if {zone1, zone2} == {connection["from_"], connection["to"]}:
                    raise ValueError(f"Line {i}: Duplicate connection between {zone1} and {zone2}")

            # checking for metadata
            metadata = {}
            if metadata_:
                    metadata_ = metadata_[1:-1]
                    if len(metadata_.split('=')) != 2:
                        raise ValueError(f"Line {i}: Invalid metadata format for connection {value}")
                    c_key, c_value = metadata_.split('=')
                    if c_key != "max_link_capacity":
                        raise ValueError(f"Line {i}: Unknown metadata attribute \"{c_key}\" for connection {zone1}-{zone2}")
                    if not c_value:
                        raise ValueError(f"Line {i}: Missing value for metadata attribute \"{c_key}\" in connection {zone1}-{zone2}")
                    try:
                        try_value = int(c_value)
                        if try_value <= 0:
                            raise ValueError
                    except ValueError:
                        raise ValueError(f"Line {i}: Invalid max_link_capacity value \"{c_value}\" for connection {zone1}-{zone2}")
                    metadata[c_key] = c_value

            parsed_data["connections"].append({"from_": zone1, "to": zone2, **metadata})
        del parsed_data["zone_lines"]
        return parsed_data

    @staticmethod
    def parsing_all(filename: str) -> dict[str, Any]:
        map_parsed = Parser.__parsing_map(filename)
        zones_parsed = Parser.__parsing_zones(map_parsed)
        parsed_data = Parser.__parsing_connections(map_parsed, zones_parsed)
        return parsed_data









