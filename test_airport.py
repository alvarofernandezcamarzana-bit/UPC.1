"""Script de pruebas para airport.py (Versión 1)."""

import os

from airport import (
    Airport,
    AddAirport,
    IsSchengenAirport,
    LoadAirports,
    MapAirports,
    PlotAirports,
    PrintAirport,
    RemoveAirport,
    SaveSchengenAirports,
    SetSchengen,
)

airports_test = []


def create_sample_file():
    """Crea un fichero de ejemplo si todavía no existe."""
    filename = "sample_airports.txt"

    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as handler:
            handler.write(
                """CODE LAT LON
BIKF N635906 W0223620
CYUL N452805 W0734429
CYYZ N434038 W0793750
DAAG N364138 E0031252
EBAW N511122 E0042737
"""
            )

    return filename


def test_is_schengen_airport():
    """Comprueba varios casos de IsSchengenAirport."""
    print("\n[1] Probando IsSchengenAirport")
    print("LEBL ->", IsSchengenAirport("LEBL"))
    print("EBAW ->", IsSchengenAirport("EBAW"))
    print("CYUL ->", IsSchengenAirport("CYUL"))
    print("XXXX ->", IsSchengenAirport("XXXX"))
    print("Vacío ->", IsSchengenAirport(""))


def test_single_airport():
    """Prueba Airport, SetSchengen y PrintAirport con aeropuertos sueltos."""
    print("\n[2] Probando Airport, SetSchengen y PrintAirport")

    airport = Airport("LEBL", 41.297445, 2.0832941)
    SetSchengen(airport)
    PrintAirport(airport)

    airport2 = Airport("CYUL", 45.467, -73.742)
    SetSchengen(airport2)
    PrintAirport(airport2)


def test_load_airports():
    """Prueba LoadAirports cargando datos desde fichero."""
    global airports_test

    print("\n[3] Probando LoadAirports")
    filename = create_sample_file()
    airports_test = LoadAirports(filename)

    print("Fichero cargado:", filename)
    print("Número de aeropuertos cargados:", len(airports_test))

    for airport in airports_test:
        PrintAirport(airport)


def test_add_airport():
    """Prueba AddAirport añadiendo un aeropuerto nuevo y uno repetido."""
    print("\n[4] Probando AddAirport")

    new_airport = Airport("LEBL", 41.297445, 2.0832941)
    SetSchengen(new_airport)
    added = AddAirport(airports_test, new_airport)
    print("Añadir LEBL:", added)

    duplicate_airport = Airport("LEBL", 41.0, 2.0)
    added_duplicate = AddAirport(airports_test, duplicate_airport)
    print("Añadir LEBL duplicado:", added_duplicate)

    for airport in airports_test:
        PrintAirport(airport)


def test_remove_airport():
    """Prueba RemoveAirport eliminando un aeropuerto existente y otro inexistente."""
    print("\n[5] Probando RemoveAirport")

    result_existing = RemoveAirport(airports_test, "CYUL")
    print("Eliminar CYUL:", result_existing)

    result_missing = RemoveAirport(airports_test, "XXXX")
    print("Eliminar XXXX:", result_missing)

    for airport in airports_test:
        PrintAirport(airport)


def test_save_schengen_airports():
    """Prueba SaveSchengenAirports guardando en fichero los aeropuertos Schengen."""
    print("\n[6] Probando SaveSchengenAirports")

    for airport in airports_test:
        SetSchengen(airport)

    output_file = "schengen_airports.txt"
    result = SaveSchengenAirports(airports_test, output_file)

    print("Resultado guardado:", result)
    print("Fichero de salida:", output_file)


def test_plot_airports():
    """Prueba PlotAirports."""
    print("\n[7] Probando PlotAirports")

    for airport in airports_test:
        SetSchengen(airport)

    result = PlotAirports(airports_test)
    print("Resultado gráfico:", result)


def test_map_airports():
    """Prueba MapAirports."""
    print("\n[8] Probando MapAirports")

    for airport in airports_test:
        SetSchengen(airport)

    filename = MapAirports(airports_test)
    print("Fichero KML generado:", filename)


def run_all_tests():
    """Ejecuta todas las pruebas en el orden recomendado."""
    test_is_schengen_airport()
    test_single_airport()
    test_load_airports()
    test_add_airport()
    test_remove_airport()
    test_save_schengen_airports()

    answer = input(
        "\n¿Quieres ejecutar también las pruebas visuales de gráfico y mapa? (s/n): "
    ).strip().lower()

    execute_visuals = False

    if answer == "s":
        execute_visuals = True

    if execute_visuals:
        test_plot_airports()
        test_map_airports()
    else:
        print("Pruebas visuales omitidas.")


if __name__ == "__main__":
    run_all_tests()