"""Airport class and functions for ProjectoAeropuerto Version 1."""

SCHENGEN_PREFIXES = [
    "LO", "EB", "LK", "LC", "EK", "EE", "EF", "LF", "ED", "LG", "EH",
    "LH", "BI", "LI", "EV", "EY", "EL", "LM", "EN", "EP", "LP", "LZ",
    "LJ", "LE", "ES", "LS",
]

ERROR_EMPTY_LIST = -1
ERROR_NOT_FOUND = -2
ERROR_FILE = -3


class Airport:
    def __init__(self, code, latitude, longitude, year=0, capacity=0):
        self.code = str(code).strip().upper()
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.year = int(year)
        self.capacity = int(capacity)
        self.schengen = False


def _normalize_code(code):
    if code is None:
        return ""
    return str(code).strip().upper()


def _sexagesimal_to_decimal(coord):
    coord = str(coord).strip()
    if coord == "":
        return None

    direction = coord[0].upper()
    digits = coord[1:]

    if not digits.isdigit():
        return None

    if direction in ("N", "S"):
        if len(digits) == 6:
            degrees = int(digits[:2])
            minutes = int(digits[2:4])
            seconds = int(digits[4:6])
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            if direction == "S":
                decimal = -decimal
            return decimal

    if direction in ("E", "W"):
        if len(digits) == 7:
            degrees = int(digits[:3])
            minutes = int(digits[3:5])
            seconds = int(digits[5:7])
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            if direction == "W":
                decimal = -decimal
            return decimal

    return None


def _decimal_to_sexagesimal(value, is_latitude):
    value = float(value)

    if is_latitude:
        direction = "N" if value >= 0 else "S"
    else:
        direction = "E" if value >= 0 else "W"

    absolute_value = abs(value)
    degrees = int(absolute_value)
    remainder = (absolute_value - degrees) * 60
    minutes = int(remainder)
    seconds = int(round((remainder - minutes) * 60))

    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1

    if is_latitude:
        return direction + f"{degrees:02d}{minutes:02d}{seconds:02d}"
    else:
        return direction + f"{degrees:03d}{minutes:02d}{seconds:02d}"


def IsSchengenAirport(code):
    code = _normalize_code(code)
    if code == "":
        return False

    prefix = code[:2]
    for valid_prefix in SCHENGEN_PREFIXES:
        if prefix == valid_prefix:
            return True
    return False


def SetSchengen(airport):
    if airport is not None:
        airport.schengen = IsSchengenAirport(airport.code)


def PrintAirport(airport):
    if airport is None:
        print("Airport: None")
    else:
        print(
            f"Code: {airport.code} | "
            f"Latitude: {airport.latitude:.6f} | "
            f"Longitude: {airport.longitude:.6f} | "
            f"Year: {airport.year} | "
            f"Capacity: {airport.capacity} | "
            f"Schengen: {airport.schengen}"
        )


def AirportToString(airport):
    if airport is None:
        return ""

    return (
        f"{airport.code} | "
        f"Lat: {airport.latitude:.6f} | "
        f"Lon: {airport.longitude:.6f} | "
        f"Año: {airport.year} | "
        f"Capacidad: {airport.capacity} | "
        f"Schengen: {'Sí' if airport.schengen else 'No'}"
    )


def GetYear(airport):
    if airport is None:
        return 0
    return airport.year


def SetYear(airport, year):
    if airport is not None:
        airport.year = int(year)


def GetCapacity(airport):
    if airport is None:
        return 0
    return airport.capacity


def SetCapacity(airport, capacity):
    if airport is not None:
        airport.capacity = int(capacity)


def GetSchengen(airport):
    if airport is None:
        return False
    return airport.schengen


def ModifyAirport(airport, code, latitude, longitude, year, capacity):
    if airport is None:
        return False

    airport.code = _normalize_code(code)
    airport.latitude = float(latitude)
    airport.longitude = float(longitude)
    airport.year = int(year)
    airport.capacity = int(capacity)
    return True


def SearchAirport(airports, code):
    code = _normalize_code(code)
    index = 0
    while index < len(airports):
        if airports[index].code == code:
            return airports[index]
        index += 1
    return None


def FilterAirports(airports, min_year, max_year, min_capacity, max_capacity):
    results = []

    for airport in airports:
        year_match = True
        capacity_match = True

        if min_year > 0:
            year_match = min_year <= airport.year <= max_year

        if min_capacity > 0:
            capacity_match = min_capacity <= airport.capacity <= max_capacity

        if year_match and capacity_match:
            results.append(airport)

    return results


def AddAirport(airports, airport):
    if airport is None:
        return False

    airport.code = _normalize_code(airport.code)

    index = 0
    while index < len(airports):
        if airports[index].code == airport.code:
            return False
        index += 1

    airports.append(airport)
    return True


def RemoveAirport(airports, code):
    code = _normalize_code(code)
    index = 0
    while index < len(airports):
        if airports[index].code == code:
            airports.pop(index)
            return index
        index += 1

    return ERROR_NOT_FOUND


def LoadAirports(filename):
    airports = []

    try:
        with open(filename, "r", encoding="utf-8") as handler:
            first_line = True

            for raw_line in handler:
                line = raw_line.strip()

                if line == "":
                    continue

                if first_line:
                    first_line = False
                    continue

                parts = line.split()

                if len(parts) >= 3:
                    code = _normalize_code(parts[0])
                    latitude = _sexagesimal_to_decimal(parts[1])
                    longitude = _sexagesimal_to_decimal(parts[2])

                    year = 0
                    if len(parts) > 3 and parts[3].isdigit():
                        year = int(parts[3])

                    capacity = 0
                    if len(parts) > 4 and parts[4].isdigit():
                        capacity = int(parts[4])

                    if code != "" and latitude is not None and longitude is not None:
                        airport = Airport(code, latitude, longitude, year, capacity)
                        airports.append(airport)

    except FileNotFoundError:
        print(f"Error: el fichero '{filename}' no existe.")
    except OSError:
        print(f"Error al leer el fichero '{filename}'.")

    return airports


def SaveSchengenAirports(airports, filename):
    schengen_airports = []

    for airport in airports:
        if airport.schengen:
            schengen_airports.append(airport)

    result = len(schengen_airports)

    if result == 0:
        print("Error: no hay aeropuertos Schengen para guardar.")
        return ERROR_EMPTY_LIST

    try:
        with open(filename, "w", encoding="utf-8") as handler:
            handler.write("CODE LAT LON YEAR CAPACITY\n")

            for airport in schengen_airports:
                lat_text = _decimal_to_sexagesimal(airport.latitude, True)
                lon_text = _decimal_to_sexagesimal(airport.longitude, False)
                handler.write(
                    f"{airport.code} {lat_text} {lon_text} "
                    f"{airport.year} {airport.capacity}\n"
                )

    except OSError:
        print(f"Error al escribir el fichero '{filename}'.")
        return ERROR_FILE

    return result


def PlotAirports(airports, axes=None):
    if len(airports) == 0:
        print("Error: no hay aeropuertos para representar.")
        return False

    schengen_count = 0
    for airport in airports:
        if airport.schengen:
            schengen_count += 1

    non_schengen_count = len(airports) - schengen_count

    if axes is not None:
        axes.clear()
        axes.bar(["Airports"], [schengen_count], label="Schengen")
        axes.bar(
            ["Airports"],
            [non_schengen_count],
            bottom=[schengen_count],
            label="No Schengen",
        )
        axes.set_ylabel("Number of airports")
        axes.set_title("Schengen / No Schengen airports")
        axes.legend()

    return True


def MapAirports(airports, output_filename="airports_map.kml"):
    if len(airports) == 0:
        print("Error: no hay aeropuertos para mostrar en el mapa.")
        return None

    kml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "  <Document>",
        '    <Style id="schengen">',
        "      <IconStyle>",
        "        <color>ff33cc33</color>",
        "        <scale>1.2</scale>",
        "        <Icon>",
        '          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>',
        "        </Icon>",
        "      </IconStyle>",
        "    </Style>",
        '    <Style id="nonschengen">',
        "      <IconStyle>",
        "        <color>ff3366ff</color>",
        "        <scale>1.2</scale>",
        "        <Icon>",
        '          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>',
        "        </Icon>",
        "      </IconStyle>",
        "    </Style>",
    ]

    for airport in airports:
        style_name = "schengen" if airport.schengen else "nonschengen"

        kml_lines.append("    <Placemark>")
        kml_lines.append(f"      <name>{airport.code}</name>")
        kml_lines.append(f"      <styleUrl>#{style_name}</styleUrl>")
        kml_lines.append(
            f"      <description>Lat {airport.latitude:.6f}, Lon {airport.longitude:.6f}</description>"
        )
        kml_lines.append("      <Point>")
        kml_lines.append(
            f"        <coordinates>{airport.longitude},{airport.latitude},0</coordinates>"
        )
        kml_lines.append("      </Point>")
        kml_lines.append("    </Placemark>")

    kml_lines.append("  </Document>")
    kml_lines.append("</kml>")

    try:
        with open(output_filename, "w", encoding="utf-8") as handler:
            handler.write("\n".join(kml_lines))
    except OSError:
        print(f"Error al escribir el fichero KML '{output_filename}'.")
        return None

    return output_filename
