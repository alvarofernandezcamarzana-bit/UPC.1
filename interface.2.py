"""Interfaz grafica en Tkinter para ProjectoAeropuerto version 1 y 2."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from airport import (
    Airport,
    AddAirport,
    ERROR_EMPTY_LIST,
    ERROR_NOT_FOUND,
    FilterAirports,
    LoadAirports,
    MapAirports,
    ModifyAirport,
    PlotAirports,
    RemoveAirport,
    SaveSchengenAirports,
    SearchAirport,
    SetSchengen,
)

from aircraft import (
    LoadArrivals,
    PlotArrivals,
    SaveFlights,
    LongDistanceArrivals,
    PlotAirlines,
    PlotFlightsType,
    MapFlights,
)

airports = []
aircrafts = []

root = None
tree = None
details = None
code_var = None
lat_var = None
lon_var = None
autoschengen_var = None
figure = None
axes = None
canvas = None
aircraft_tree = None
arrivals_figure = None
arrivals_axes = None
arrivals_canvas = None
airlines_figure = None
airlines_axes = None
airlines_canvas = None
flights_type_figure = None
flights_type_axes = None
flights_type_canvas = None
notebook = None
v2_notebook = None
info_text_v2 = None
airline_vars = {}
airline_full_data = {}
airline_check_frame = None


def apply_styles():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Main.TFrame", background="#f4f1ee")
    style.configure("Panel.TLabelframe", background="#ede7e3")
    style.configure(
        "Panel.TLabelframe.Label",
        background="#ede7e3",
        foreground="#5f5a56",
    )
    style.configure("Custom.TLabel", background="#f4f1ee", foreground="#5c5753")
    style.configure("Custom.TButton", padding=6)
    style.configure("Treeview", rowheight=24)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    style.configure("TNotebook", background="#f4f1ee")
    style.configure("TNotebook.Tab", background="#e6dfda", foreground="#5c5753")
    style.map(
        "TNotebook.Tab",
        background=[("selected", "#f4f1ee")],
    )
    style.map(
        "Custom.TButton",
        background=[("active", "#e6dfda")],
    )


def build_interface():
    global root

    root.title("Airport Management - Version 2")
    root.geometry("1200x800")
    root.minsize(1020, 700)
    root.configure(bg="#f4f1ee")

    apply_styles()

    container = ttk.Frame(root, padding=12, style="Main.TFrame")
    container.pack(fill=tk.BOTH, expand=True)

    global notebook
    notebook = ttk.Notebook(container)
    notebook.pack(fill=tk.BOTH, expand=True)

    v1_frame = ttk.Frame(notebook, style="Main.TFrame")
    v2_frame = ttk.Frame(notebook, style="Main.TFrame")

    notebook.add(v1_frame, text="Version 1 - Aeropuertos")
    notebook.add(v2_frame, text="Version 2 - Vuelos")

    build_version1(v1_frame)
    build_version2(v2_frame)


def build_version1(parent):
    left_panel = ttk.Frame(parent, padding=(0, 0, 12, 0), style="Main.TFrame")
    left_panel.pack(side=tk.LEFT, fill=tk.Y)

    right_panel = ttk.Frame(parent, style="Main.TFrame")
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    build_form(left_panel)
    build_buttons(left_panel)
    build_table(right_panel)
    build_log(right_panel)
    build_plot_area(right_panel)


def build_version2(parent):
    global v2_notebook

    left_panel = ttk.Frame(parent, padding=(0, 0, 12, 0), style="Main.TFrame")
    left_panel.pack(side=tk.LEFT, fill=tk.Y)

    right_panel = ttk.Frame(parent, style="Main.TFrame")
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    build_flight_buttons(left_panel)
    build_aircraft_table(right_panel)

    v2_notebook = ttk.Notebook(right_panel)
    v2_notebook.pack(fill=tk.BOTH, expand=True)

    arrivals_plot_frame = ttk.Frame(v2_notebook, style="Main.TFrame")
    airlines_plot_frame = ttk.Frame(v2_notebook, style="Main.TFrame")
    flights_type_plot_frame = ttk.Frame(v2_notebook, style="Main.TFrame")

    v2_notebook.add(arrivals_plot_frame, text="Llegadas por hora")
    v2_notebook.add(airlines_plot_frame, text="Por compania")
    v2_notebook.add(flights_type_plot_frame, text="Schengen/No-Schengen")

    build_arrivals_plot_area(arrivals_plot_frame)
    build_airlines_plot_area(airlines_plot_frame)
    build_flights_type_plot_area(flights_type_plot_frame)


def build_form(parent):
    form = ttk.LabelFrame(parent, text="Nuevo aeropuerto", padding=10, style="Panel.TLabelframe")
    form.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(form, text="ICAO", style="Custom.TLabel").grid(
        row=0, column=0, sticky=tk.W, padx=4, pady=4
    )
    ttk.Entry(form, textvariable=code_var, width=12).grid(
        row=0, column=1, sticky=tk.W, padx=4, pady=4
    )

    ttk.Label(form, text="Latitud", style="Custom.TLabel").grid(
        row=1, column=0, sticky=tk.W, padx=4, pady=4
    )
    ttk.Entry(form, textvariable=lat_var, width=14).grid(
        row=1, column=1, sticky=tk.W, padx=4, pady=4
    )

    ttk.Label(form, text="Longitud", style="Custom.TLabel").grid(
        row=2, column=0, sticky=tk.W, padx=4, pady=4
    )
    ttk.Entry(form, textvariable=lon_var, width=14).grid(
        row=2, column=1, sticky=tk.W, padx=4, pady=4
    )

    ttk.Checkbutton(
        form,
        text="Asignar Schengen automaticamente",
        variable=autoschengen_var,
    ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=4, pady=6)

    ttk.Button(
        form,
        text="Anadir aeropuerto",
        command=add_airport,
        style="Custom.TButton",
    ).grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(6, 2))

    ttk.Button(
        form,
        text="Modificar seleccionado",
        command=modify_selected,
        style="Custom.TButton",
    ).grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(4, 2))

    form.columnconfigure(1, weight=1)


def build_buttons(parent):
    buttons = ttk.LabelFrame(parent, text="Operaciones", padding=10, style="Panel.TLabelframe")
    buttons.pack(fill=tk.X)

    ttk.Button(buttons, text="Cargar fichero", command=load_file, style="Custom.TButton").grid(
        row=0, column=0, padx=4, pady=4, sticky=tk.EW
    )
    ttk.Button(
        buttons,
        text="Eliminar seleccionado",
        command=remove_selected,
        style="Custom.TButton",
    ).grid(row=0, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Detectar Schengen",
        command=detect_schengen,
        style="Custom.TButton",
    ).grid(row=1, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Guardar Schengen",
        command=save_schengen,
        style="Custom.TButton",
    ).grid(row=1, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Mostrar lista",
        command=show_all,
        style="Custom.TButton",
    ).grid(row=2, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Grafico",
        command=plot_airports_interface,
        style="Custom.TButton",
    ).grid(row=2, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Mapa",
        command=map_airports,
        style="Custom.TButton",
    ).grid(row=3, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Refrescar tabla",
        command=refresh_list,
        style="Custom.TButton",
    ).grid(row=3, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Filtrar",
        command=filter_airports,
        style="Custom.TButton",
    ).grid(row=4, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Mostrar todos",
        command=show_all_airports,
        style="Custom.TButton",
    ).grid(row=4, column=1, padx=4, pady=4, sticky=tk.EW)

    for column in range(2):
        buttons.columnconfigure(column, weight=1)


def build_flight_buttons(parent):
    buttons = ttk.LabelFrame(parent, text="Operaciones de vuelos", padding=10, style="Panel.TLabelframe")
    buttons.pack(fill=tk.X)

    ttk.Button(buttons, text="Cargar vuelos", command=load_arrivals, style="Custom.TButton").grid(
        row=0, column=0, padx=4, pady=4, sticky=tk.EW
    )
    ttk.Button(
        buttons,
        text="Grafico horas",
        command=plot_arrivals_interface,
        style="Custom.TButton",
    ).grid(row=0, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Guardar vuelos",
        command=save_flights,
        style="Custom.TButton",
    ).grid(row=1, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Grafico companias",
        command=plot_airlines_interface,
        style="Custom.TButton",
    ).grid(row=1, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Schengen/No-Schengen",
        command=plot_flights_type_interface,
        style="Custom.TButton",
    ).grid(row=2, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Larga distancia",
        command=show_long_distance,
        style="Custom.TButton",
    ).grid(row=2, column=1, padx=4, pady=4, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Mapa Google Earth",
        command=map_flights_interface,
        style="Custom.TButton",
    ).grid(row=3, column=0, padx=4, pady=4, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Mapa larga distancia",
        command=map_long_distance_interface,
        style="Custom.TButton",
    ).grid(row=3, column=1, padx=4, pady=4, sticky=tk.EW)

    global info_text_v2
    info_text_v2 = tk.Text(
        buttons,
        height=12,
        width=30,
        bg="#faf8f6",
        fg="#5c5753",
        relief="solid",
        borderwidth=1,
    )
    info_text_v2.grid(row=4, column=0, columnspan=2, padx=4, pady=10, sticky=tk.EW)

    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)


def build_table(parent):
    ttk.Label(parent, text="Aeropuertos cargados", style="Custom.TLabel").pack(anchor=tk.W)

    columns = ("code", "lat", "lon", "schengen")

    global tree
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

    tree.heading("code", text="ICAO")
    tree.heading("lat", text="Latitud")
    tree.heading("lon", text="Longitud")
    tree.heading("schengen", text="Schengen")

    tree.column("code", width=70, anchor=tk.CENTER)
    tree.column("lat", width=100, anchor=tk.CENTER)
    tree.column("lon", width=100, anchor=tk.CENTER)
    tree.column("schengen", width=80, anchor=tk.CENTER)

    tree.pack(fill=tk.BOTH, expand=False)
    tree.bind("<<TreeviewSelect>>", show_selected)


def build_aircraft_table(parent):
    ttk.Label(parent, text="Vuelos cargados", style="Custom.TLabel").pack(anchor=tk.W)

    columns = ("id", "origin", "arrival", "airline")

    global aircraft_tree
    aircraft_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

    aircraft_tree.heading("id", text="ID")
    aircraft_tree.heading("origin", text="Origen")
    aircraft_tree.heading("arrival", text="Llegada")
    aircraft_tree.heading("airline", text="Compania")

    aircraft_tree.column("id", width=100, anchor=tk.CENTER)
    aircraft_tree.column("origin", width=80, anchor=tk.CENTER)
    aircraft_tree.column("arrival", width=80, anchor=tk.CENTER)
    aircraft_tree.column("airline", width=80, anchor=tk.CENTER)

    aircraft_tree.pack(fill=tk.BOTH, expand=False)


def build_log(parent):
    ttk.Label(parent, text="Informacion", style="Custom.TLabel").pack(anchor=tk.W, pady=(10, 0))

    global details
    details = tk.Text(
        parent,
        height=7,
        wrap="word",
        bg="#faf8f6",
        fg="#5c5753",
        relief="solid",
        borderwidth=1,
    )
    details.pack(fill=tk.BOTH, expand=False, pady=(0, 6))


def build_plot_area(parent):
    ttk.Label(parent, text="Grafico Schengen/No Schengen", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global figure
    global axes
    global canvas

    figure = Figure(figsize=(6.5, 4.5), dpi=100)
    axes = figure.add_subplot(111)
    axes.set_title("Schengen / No Schengen airports")
    axes.set_ylabel("Number of airports")

    figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    canvas = FigureCanvasTkAgg(figure, master=plot_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()


def build_arrivals_plot_area(parent):
    ttk.Label(parent, text="Grafico de llegadas por hora", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global arrivals_figure
    global arrivals_axes
    global arrivals_canvas

    arrivals_figure = Figure(figsize=(6.5, 4.5), dpi=100)
    arrivals_axes = arrivals_figure.add_subplot(111)
    arrivals_axes.set_title("Arrivals frequency per hour")
    arrivals_axes.set_xlabel("Hour of day")
    arrivals_axes.set_ylabel("Number of arrivals")

    arrivals_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    arrivals_canvas = FigureCanvasTkAgg(arrivals_figure, master=plot_frame)
    arrivals_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    arrivals_canvas.draw()


def build_airlines_plot_area(parent):
    ttk.Label(parent, text="Grafico de vuelos por compania", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    main_frame = ttk.Frame(parent, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    plot_frame = ttk.Frame(main_frame, style="Main.TFrame")
    plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    global airlines_figure
    global airlines_axes
    global airlines_canvas

    airlines_figure = Figure(figsize=(6.5, 4.5), dpi=100)
    airlines_axes = airlines_figure.add_subplot(111)
    airlines_axes.set_title("Flights per airline")
    airlines_axes.set_ylabel("Number of flights")

    airlines_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    airlines_canvas = FigureCanvasTkAgg(airlines_figure, master=plot_frame)
    airlines_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    airlines_canvas.draw()

    check_panel = ttk.Frame(main_frame, style="Main.TFrame")
    check_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))

    ttk.Label(check_panel, text="Filtrar companias:", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(0, 4)
    )

    check_canvas = tk.Canvas(check_panel, width=200, bg="#f4f1ee", highlightthickness=0)
    check_scroll = ttk.Scrollbar(check_panel, orient="vertical", command=check_canvas.yview)

    global airline_check_frame
    airline_check_frame = ttk.Frame(check_canvas, style="Main.TFrame")

    airline_check_frame.bind(
        "<Configure>",
        lambda e: check_canvas.configure(scrollregion=check_canvas.bbox("all")),
    )

    check_canvas.create_window((0, 0), window=airline_check_frame, anchor="nw", width=190)
    check_canvas.configure(yscrollcommand=check_scroll.set)

    check_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    check_scroll.pack(side=tk.RIGHT, fill=tk.Y)


def build_flights_type_plot_area(parent):
    ttk.Label(parent, text="Grafico Schengen vs No-Schengen", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global flights_type_figure
    global flights_type_axes
    global flights_type_canvas

    flights_type_figure = Figure(figsize=(6.5, 4.5), dpi=100)
    flights_type_axes = flights_type_figure.add_subplot(111)
    flights_type_axes.set_title("Schengen vs Non-Schengen arrivals")
    flights_type_axes.set_ylabel("Number of flights")

    flights_type_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    flights_type_canvas = FigureCanvasTkAgg(flights_type_figure, master=plot_frame)
    flights_type_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    flights_type_canvas.draw()


def log_message(message):
    details.insert(tk.END, message + "\n")
    details.see(tk.END)


def clear_log():
    details.delete("1.0", tk.END)


def clear_input_fields():
    code_var.set("")
    lat_var.set("")
    lon_var.set("")


def apply_schengen_flags():
    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        i += 1


def selected_index():
    selection = tree.selection()
    index = -1

    if selection:
        iid = selection[0]
        if str(iid).isdigit():
            possible_index = int(iid)
            if 0 <= possible_index < len(airports):
                index = possible_index

    return index


def selected_airport():
    airport = None
    index = selected_index()

    if index != -1:
        airport = airports[index]

    return airport


def refresh_list():
    apply_schengen_flags()

    for item in tree.get_children():
        tree.delete(item)

    i = 0
    while i < len(airports):
        tree.insert(
            "",
            tk.END,
            iid=str(i),
            values=(
                airports[i].code,
                f"{airports[i].latitude:.6f}",
                f"{airports[i].longitude:.6f}",
                "Si" if airports[i].schengen else "No",
            ),
        )
        i += 1


def refresh_aircraft_list():
    for item in aircraft_tree.get_children():
        aircraft_tree.delete(item)

    i = 0
    while i < len(aircrafts):
        aircraft_tree.insert(
            "",
            tk.END,
            iid=str(i),
            values=(
                aircrafts[i].id,
                aircrafts[i].origin,
                aircrafts[i].arrival_time,
                aircrafts[i].airline,
            ),
        )
        i += 1


def load_file():
    global airports

    filename = filedialog.askopenfilename(
        title="Selecciona un fichero de aeropuertos",
        filetypes=[("Text files", "*.txt"), ("Todos los archivos", "*.*")],
    )

    if filename != "":
        airports = LoadAirports(filename)
        refresh_list()

        clear_log()
        log_message(f"Fichero cargado: {filename}")
        log_message(f"Aeropuertos cargados: {len(airports)}")

        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "No se ha cargado ningun aeropuerto. Revisa el fichero seleccionado.",
            )


def show_selected(_event=None):
    airport = selected_airport()

    if airport:
        clear_log()
        log_message(f"Codigo ICAO: {airport.code}")
        log_message(f"Latitud: {airport.latitude:.6f}")
        log_message(f"Longitud: {airport.longitude:.6f}")
        log_message(f"Schengen: {'Si' if airport.schengen else 'No'}")


def show_all():
    apply_schengen_flags()
    clear_log()

    if len(airports) == 0:
        log_message("No hay aeropuertos cargados.")
    else:
        log_message("Lista actual de aeropuertos:")
        log_message("")

        i = 0
        while i < len(airports):
            log_message(
                f"{airports[i].code} | "
                f"Lat: {airports[i].latitude:.6f} | "
                f"Lon: {airports[i].longitude:.6f} | "
                f"Schengen: {'Si' if airports[i].schengen else 'No'}"
            )
            i += 1


def add_airport():
    code = code_var.get().strip()
    valid_data = True
    latitude = 0.0
    longitude = 0.0

    if code == "":
        valid_data = False
        messagebox.showerror("Error", "El codigo ICAO no puede estar vacio.")

    if valid_data:
        try:
            latitude = float(lat_var.get())
            longitude = float(lon_var.get())
        except ValueError:
            valid_data = False
            messagebox.showerror("Error", "Latitud y longitud deben ser numeros reales.")

    if valid_data:
        airport = Airport(code, latitude, longitude)

        if autoschengen_var.get():
            SetSchengen(airport)

        added = AddAirport(airports, airport)

        if added:
            refresh_list()
            clear_input_fields()
            clear_log()
            log_message(f"Aeropuerto anadido correctamente: {airport.code}")
        else:
            messagebox.showwarning("Aviso", "Ese aeropuerto ya existe en la lista.")


def remove_selected():
    airport = selected_airport()

    if airport is None:
        messagebox.showinfo("Informacion", "Selecciona un aeropuerto en la tabla.")
    else:
        result = RemoveAirport(airports, airport.code)

        if result == ERROR_NOT_FOUND:
            messagebox.showwarning("Aviso", "No se encontro el aeropuerto a eliminar.")
        else:
            refresh_list()
            clear_log()
            log_message(f"Aeropuerto eliminado: {airport.code}")


def detect_schengen():
    airport = selected_airport()

    if airport is not None:
        SetSchengen(airport)
        refresh_list()
        clear_log()
        log_message(f"Atributo Schengen actualizado para: {airport.code}")
    else:
        apply_schengen_flags()
        refresh_list()
        clear_log()
        log_message("Atributo Schengen actualizado para toda la lista.")


def save_schengen():
    if len(airports) == 0:
        messagebox.showinfo("Informacion", "No hay aeropuertos para guardar.")
    else:
        apply_schengen_flags()

        filename = filedialog.asksaveasfilename(
            title="Guardar aeropuertos Schengen",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )

        if filename != "":
            result = SaveSchengenAirports(airports, filename)

            if result == ERROR_EMPTY_LIST:
                messagebox.showwarning("Aviso", "No hay aeropuertos Schengen en la lista.")
            elif result < 0:
                messagebox.showerror("Error", "No se pudo guardar el fichero de salida.")
            else:
                clear_log()
                log_message(f"Fichero guardado: {filename}")
                log_message(f"Aeropuertos Schengen guardados: {result}")
                messagebox.showinfo("Correcto", f"Se guardaron {result} aeropuertos.")


def plot_airports_interface():
    if len(airports) == 0:
        messagebox.showinfo("Informacion", "Carga o anade aeropuertos primero.")
    else:
        apply_schengen_flags()
        drawn = PlotAirports(airports, axes)

        if drawn:
            figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            canvas.draw()
            clear_log()
            log_message("Grafico actualizado dentro de la interfaz.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el grafico.")


def map_airports():
    if len(airports) == 0:
        messagebox.showinfo("Informacion", "Carga o anade aeropuertos primero.")
    else:
        apply_schengen_flags()
        filename = MapAirports(airports)

        if filename is None:
            messagebox.showerror("Error", "No se pudo generar el fichero KML.")
        else:
            clear_log()
            log_message(f"Fichero KML generado: {filename}")
            os.startfile(filename)


def modify_selected():
    airport = selected_airport()

    if airport is None:
        messagebox.showinfo("Informacion", "Selecciona un aeropuerto en la tabla.")
    else:
        code = code_var.get().strip()
        if code == "":
            code = airport.code

        latitude = airport.latitude
        longitude = airport.longitude

        lat_text = lat_var.get().strip()
        if lat_text != "":
            try:
                latitude = float(lat_text)
            except ValueError:
                pass

        lon_text = lon_var.get().strip()
        if lon_text != "":
            try:
                longitude = float(lon_text)
            except ValueError:
                pass

        ModifyAirport(airport, code, latitude, longitude, 0, 0)

        if autoschengen_var.get():
            SetSchengen(airport)

        refresh_list()
        clear_input_fields()
        clear_log()
        log_message(f"Aeropuerto modificado: {airport.code}")


def filter_airports():
    if len(airports) == 0:
        messagebox.showinfo("Informacion", "No hay aeropuertos para filtrar.")
    else:
        filtered = FilterAirports(airports, 0, 0, 0, 0)

        if len(filtered) == 0:
            messagebox.showinfo("Informacion", "No hay aeropuertos que coincidan con los filtros.")
        else:
            clear_log()
            log_message(f"Aeropuertos encontrados: {len(filtered)}")
            log_message("")

            i = 0
            while i < len(filtered):
                log_message(
                    f"{filtered[i].code} | "
                    f"Lat: {filtered[i].latitude:.6f} | "
                    f"Lon: {filtered[i].longitude:.6f} | "
                    f"Schengen: {'Si' if filtered[i].schengen else 'No'}"
                )
                i += 1


def show_all_airports():
    if len(airports) == 0:
        messagebox.showinfo("Informacion", "No hay aeropuertos para mostrar.")
    else:
        clear_log()
        log_message(f"Total de aeropuertos: {len(airports)}")
        log_message("")

        i = 0
        while i < len(airports):
            log_message(
                f"{airports[i].code} | "
                f"Lat: {airports[i].latitude:.6f} | "
                f"Lon: {airports[i].longitude:.6f} | "
                f"Schengen: {'Si' if airports[i].schengen else 'No'}"
            )
            i += 1


def load_arrivals():
    global aircrafts

    filename = filedialog.askopenfilename(
        title="Selecciona un fichero de vuelos",
        filetypes=[("Text files", "*.txt"), ("Todos los archivos", "*.*")],
    )

    if filename != "":
        aircrafts = LoadArrivals(filename)
        refresh_aircraft_list()

        clear_log()
        log_message(f"Fichero cargado: {filename}")
        log_message(f"Vuelos cargados: {len(aircrafts)}")

        if len(aircrafts) == 0:
            messagebox.showwarning(
                "Aviso",
                "No se ha cargado ningun vuelo. Revisa el fichero seleccionado.",
            )


def plot_arrivals_interface():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "Carga o anade vuelos primero.")
    else:
        hourly_data = PlotArrivals(aircrafts)

        if hourly_data:
            arrivals_axes.clear()
            hours = []
            counts = []
            hour = 0
            while hour < 24:
                hours.append(hour)
                counts.append(hourly_data[hour])
                hour += 1

            arrivals_axes.bar(hours, counts, color="#4a90a4")
            arrivals_axes.set_xlabel("Hour of day")
            arrivals_axes.set_ylabel("Number of arrivals")
            arrivals_axes.set_title("Arrivals frequency per hour")
            arrivals_axes.set_xticks(range(0, 24, 2))

            arrivals_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            arrivals_canvas.draw()
            clear_log()
            log_message("Grafico de llegadas actualizado.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el grafico.")


def save_flights():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "No hay vuelos para guardar.")
    else:
        filename = filedialog.asksaveasfilename(
            title="Guardar vuelos",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )

        if filename != "":
            result = SaveFlights(aircrafts, filename)

            if result < 0:
                messagebox.showerror("Error", "No se pudo guardar el fichero de salida.")
            else:
                clear_log()
                log_message(f"Fichero guardado: {filename}")
                log_message(f"Vuelos guardados: {result}")
                messagebox.showinfo("Correcto", f"Se guardaron {result} vuelos.")


def log_message_v2(message):
    info_text_v2.insert(tk.END, message + "\n")
    info_text_v2.see(tk.END)


def clear_log_v2():
    info_text_v2.delete("1.0", tk.END)


def show_long_distance():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "Carga o anade vuelos primero.")
    else:
        long_distance = LongDistanceArrivals(aircrafts)

        clear_log_v2()
        log_message_v2(f"Vuelos de larga distancia (>2000 km): {len(long_distance)}")
        log_message_v2("")

        i = 0
        while i < len(long_distance):
            dist = long_distance[i].distance
            log_message_v2(
                f"{long_distance[i].id} | {long_distance[i].origin} | "
                f"{long_distance[i].arrival_time} | {dist:.0f} km"
            )
            i += 1


def plot_airlines_interface():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "Carga o anade vuelos primero.")
    else:
        global airline_full_data
        global airline_vars

        airline_full_data = PlotAirlines(aircrafts)

        if airline_full_data:
            for widget in airline_check_frame.winfo_children():
                widget.destroy()

            airline_vars = {}
            for airline in sorted(airline_full_data.keys()):
                var = tk.BooleanVar(value=True)
                airline_vars[airline] = var
                cb = ttk.Checkbutton(
                    airline_check_frame,
                    text=f"{airline} ({airline_full_data[airline]})",
                    variable=var,
                )
                cb.pack(anchor=tk.W, padx=4, pady=1)
                cb.var = var

            ttk.Button(
                airline_check_frame,
                text="Aplicar filtro",
                command=apply_airline_filter,
                style="Custom.TButton",
            ).pack(anchor=tk.W, padx=4, pady=(8, 2))

            apply_airline_filter()
            clear_log_v2()
            log_message_v2("Grafico de companias actualizado.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el grafico.")


def apply_airline_filter():
    global airline_vars, airline_full_data, airlines_figure, airlines_axes, airlines_canvas

    if not airline_vars or not airline_full_data:
        return

    selected = [a for a, v in airline_vars.items() if v.get()]
    n = len(selected)

    airlines_axes.cla()

    bottom = min(0.16 + max(0, n - 5) * 0.003, 0.30)

    if selected:
        counts = [airline_full_data[a] for a in selected]
        airlines_axes.bar(range(n), counts, width=min(0.8, 10.0 / n), color="#4a90a4")
        airlines_axes.set_xticks(range(n))
        airlines_axes.set_xticklabels(selected, rotation=90, ha="center", fontsize=8)

    airlines_axes.set_xlabel("Airline")
    airlines_axes.set_ylabel("Number of flights")
    airlines_axes.set_title("Flights per airline")
    airlines_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=bottom)
    airlines_canvas.draw()


def plot_flights_type_interface():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "Carga o anade vuelos primero.")
    else:
        data = PlotFlightsType(aircrafts)

        if data:
            flights_type_axes.clear()
            flights_type_axes.bar(["Arrivals"], [data[0]], label="Schengen", color="#4a90a4")
            flights_type_axes.bar(["Arrivals"], [data[1]], bottom=[data[0]], label="No Schengen", color="#d95f5f")
            flights_type_axes.set_ylabel("Number of flights")
            flights_type_axes.set_title("Schengen vs Non-Schengen arrivals")
            flights_type_axes.legend()

            flights_type_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            flights_type_canvas.draw()
            clear_log_v2()
            log_message_v2("Grafico Schengen/No-Schengen actualizado.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el grafico.")


def map_flights_interface():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "Carga o anade vuelos primero.")
    else:
        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "Carga primero los aeropuertos para el mapa.",
            )
        else:
            filename = MapFlights(aircrafts)

            if filename is None:
                messagebox.showerror("Error", "No se pudo generar el archivo KML.")
            else:
                clear_log_v2()
                log_message_v2(f"Archivo KML generado: {filename}")
                os.startfile(filename)
                messagebox.showinfo("Correcto", f"Archivo KML generado: {filename}")


def map_long_distance_interface():
    if len(aircrafts) == 0:
        messagebox.showinfo("Informacion", "Carga o anade vuelos primero.")
    else:
        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "Carga primero los aeropuertos para el mapa.",
            )
        else:
            filename = MapFlights(aircrafts, long_distance_only=True)

            if filename is None:
                messagebox.showerror("Error", "No se pudo generar el archivo KML.")
            else:
                clear_log_v2()
                log_message_v2(f"Archivo KML de larga distancia generado: {filename}")
                os.startfile(filename)
                messagebox.showinfo("Correcto", f"Archivo KML generado: {filename}")


def main():
    global root
    global code_var
    global lat_var
    global lon_var
    global autoschengen_var

    root = tk.Tk()

    code_var = tk.StringVar()
    lat_var = tk.StringVar()
    lon_var = tk.StringVar()
    autoschengen_var = tk.BooleanVar(value=True)

    build_interface()
    root.mainloop()


if __name__ == "__main__":
    main()
