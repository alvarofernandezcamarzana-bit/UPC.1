"""Funciones básicas para la versión 1 de ProjectoAeropuerto."""

import os
import webbrowser

SCHENGEN_PREFIXES = [
    "LO", "EB", "LK", "LC", "EK", "EE", "EF", "LF", "ED", "LG", "EH",
    "LH", "BI", "LI", "EV", "EY", "EL", "LM", "EN", "EP", "LP", "LZ",
    "LJ", "LE", "ES", "LS",
]

ERROR_EMPTY_LIST = -1
ERROR_NOT_FOUND = -2
ERROR_FILE = -3


def Airport(code, latitude, longitude):
    """Crea un aeropuerto como diccionario simple."""
    airport = {
        "code": str(code).strip().upper(),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "schengen": False,
    }
    return airport


def _normalize_code(code):
    """Devuelve el código ICAO en mayúsculas y sin espacios."""
    normalized = ""

    if code is not None:
        normalized = str(code).strip().upper()

    return normalized


def IsSchengenAirport(code):
    """Devuelve True si el aeropuerto pertenece a Schengen."""
    code = _normalize_code(code)
    is_schengen = False

    if code != "":
        prefix = code[:2]

        for valid_prefix in SCHENGEN_PREFIXES:
            if prefix == valid_prefix:
                is_schengen = True

    return is_schengen


def SetSchengen(airport):
    """Actualiza el atributo schengen del aeropuerto recibido."""
    if airport is not None:
        airport["schengen"] = IsSchengenAirport(airport["code"])


def PrintAirport(airport):
    """Imprime por consola la información del aeropuerto."""
    if airport is None:
        print("Airport: None")
    else:
        print(
            f"Code: {airport['code']} | "
            f"Latitude: {airport['latitude']:.6f} | "
            f"Longitude: {airport['longitude']:.6f} | "
            f"Schengen: {airport['schengen']}"
        )


def _sexagesimal_to_decimal(coord):
    """Convierte coordenadas tipo NDDMMSS o EDDDMMSS a grados decimales."""
    coord = str(coord).strip()
    decimal = None

    if coord != "":
        direction = coord[0].upper()
        digits = coord[1:]

        if digits.isdigit():
            if direction in ("N", "S"):
                if len(digits) == 6:
                    degrees = int(digits[:2])
                    minutes = int(digits[2:4])
                    seconds = int(digits[4:6])
                    decimal = degrees + minutes / 60.0 + seconds / 3600.0

                    if direction == "S":
                        decimal = -decimal

            if direction in ("E", "W"):
                if len(digits) == 7:
                    degrees = int(digits[:3])
                    minutes = int(digits[3:5])
                    seconds = int(digits[5:7])
                    decimal = degrees + minutes / 60.0 + seconds / 3600.0

                    if direction == "W":
                        decimal = -decimal

    return decimal


def _decimal_to_sexagesimal(value, is_latitude):
    """Convierte grados decimales al formato del fichero."""
    value = float(value)

    if is_latitude:
        direction = "N"
        if value < 0:
            direction = "S"
    else:
        direction = "E"
        if value < 0:
            direction = "W"

    absolute_value = abs(value)

    degrees = int(absolute_value)
    remainder_minutes = (absolute_value - degrees) * 60
    minutes = int(remainder_minutes)
    seconds = int(round((remainder_minutes - minutes) * 60))

    if seconds == 60:
        seconds = 0
        minutes += 1

    if minutes == 60:
        minutes = 0
        degrees += 1

    numeric_part = ""
    if is_latitude:
        numeric_part = f"{degrees:02d}{minutes:02d}{seconds:02d}"
    else:
        numeric_part = f"{degrees:03d}{minutes:02d}{seconds:02d}"

    return direction + numeric_part


def LoadAirports(filename):
    """Carga aeropuertos desde fichero y devuelve una lista."""
    airports = []

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as handler:
                first_line = True

                for raw_line in handler:
                    line = raw_line.strip()

                    if line != "":
                        if first_line:
                            first_line = False
                        else:
                            parts = line.split()

                            if len(parts) >= 3:
                                code = _normalize_code(parts[0])
                                latitude = _sexagesimal_to_decimal(parts[1])
                                longitude = _sexagesimal_to_decimal(parts[2])

                                if code != "" and latitude is not None and longitude is not None:
                                    airport = Airport(code, latitude, longitude)
                                    airports.append(airport)
                                else:
                                    print(f"Línea ignorada por datos inválidos: {line}")
                            else:
                                print(f"Línea ignorada por formato incorrecto: {line}")

        except OSError:
            print(f"Error al leer el fichero '{filename}'.")
            airports = []
    else:
        print(f"Error: el fichero '{filename}' no existe.")

    return airports


def SaveSchengenAirports(airports, filename):
    """Guarda en fichero solo los aeropuertos Schengen."""
    schengen_airports = []

    for airport in airports:
        if airport["schengen"]:
            schengen_airports.append(airport)

    result = len(schengen_airports)

    if result == 0:
        print("Error: no hay aeropuertos Schengen para guardar.")
        result = ERROR_EMPTY_LIST
    else:
        try:
            with open(filename, "w", encoding="utf-8") as handler:
                handler.write("CODE LAT LON\n")

                for airport in schengen_airports:
                    lat_text = _decimal_to_sexagesimal(airport["latitude"], True)
                    lon_text = _decimal_to_sexagesimal(airport["longitude"], False)
                    handler.write(f"{airport['code']} {lat_text} {lon_text}\n")

        except OSError:
            print(f"Error al escribir el fichero '{filename}'.")
            result = ERROR_FILE

    return result


def AddAirport(airports, airport):
    """Añade un aeropuerto a la lista si no existe ya por código ICAO."""
    added = True

    if airport is None:
        added = False
    else:
        airport["code"] = _normalize_code(airport["code"])

        for existing_airport in airports:
            if existing_airport["code"] == airport["code"]:
                added = False

        if added:
            airports.append(airport)

    return added


def RemoveAirport(airports, code):
    """Elimina de la lista el aeropuerto con el código recibido."""
    code = _normalize_code(code)
    result = ERROR_NOT_FOUND
    index = 0

    while index < len(airports) and result == ERROR_NOT_FOUND:
        if airports[index]["code"] == code:
            del airports[index]
            result = index
        else:
            index += 1

    return result


def PlotAirports(airports, axes=None):
    """Dibuja el gráfico de barras apiladas.

    Si recibe un axes de matplotlib, dibuja dentro de ese axes.
    Así se puede integrar dentro de Tkinter.
    """
    graph_drawn = False

    if len(airports) == 0:
        print("Error: no hay aeropuertos para representar.")
    else:
        schengen_count = 0

        for airport in airports:
            if airport["schengen"]:
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
            graph_drawn = True

    return graph_drawn


def MapAirports(airports, output_filename="airports_map.kml"):
    """Genera un fichero KML con los aeropuertos y trata de abrirlo."""
    result = None

    if len(airports) == 0:
        print("Error: no hay aeropuertos para mostrar en el mapa.")
    else:
        kml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<kml xmlns="http://www.opengis.net/kml/2.2">',
            "  <Document>",
            "    <Style id=\"schengen\">",
            "      <IconStyle>",
            "        <color>ff33cc33</color>",
            "        <scale>1.2</scale>",
            "        <Icon>",
            "          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>",
            "        </Icon>",
            "      </IconStyle>",
            "    </Style>",
            "    <Style id=\"nonschengen\">",
            "      <IconStyle>",
            "        <color>ff3366ff</color>",
            "        <scale>1.2</scale>",
            "        <Icon>",
            "          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>",
            "        </Icon>",
            "      </IconStyle>",
            "    </Style>",
        ]

        for airport in airports:
            style_name = "nonschengen"
            if airport["schengen"]:
                style_name = "schengen"

            kml_lines.append("    <Placemark>")
            kml_lines.append(f"      <name>{airport['code']}</name>")
            kml_lines.append(f"      <styleUrl>#{style_name}</styleUrl>")
            kml_lines.append(
                f"      <description>Lat {airport['latitude']:.6f}, Lon {airport['longitude']:.6f}</description>"
            )
            kml_lines.append("      <Point>")
            kml_lines.append(
                f"        <coordinates>{airport['longitude']},{airport['latitude']},0</coordinates>"
            )
            kml_lines.append("      </Point>")
            kml_lines.append("    </Placemark>")

        kml_lines.append("  </Document>")
        kml_lines.append("</kml>")

        try:
            with open(output_filename, "w", encoding="utf-8") as handler:
                handler.write("\n".join(kml_lines))
            result = output_filename

            full_path = os.path.abspath(output_filename)
            url = "file:///" + full_path.replace("\\", "/")

            try:
                webbrowser.open(url)
            except Exception:
                print("Aviso: no se pudo abrir automáticamente el fichero KML.")

        except OSError:
            print(f"Error al escribir el fichero KML '{output_filename}'.")

    return result


__all__ = [
    "Airport",
    "IsSchengenAirport",
    "SetSchengen",
    "PrintAirport",
    "LoadAirports",
    "SaveSchengenAirports",
    "AddAirport",
    "RemoveAirport",
    "PlotAirports",
    "MapAirports",
    "ERROR_EMPTY_LIST",
    "ERROR_NOT_FOUND",
    "ERROR_FILE",
]