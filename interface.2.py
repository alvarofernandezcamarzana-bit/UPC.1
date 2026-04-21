"""Interfaz gráfica en Tkinter para la versión 1 de ProjectoAeropuerto."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from airport import (
    Airport,
    AddAirport,
    ERROR_EMPTY_LIST,
    ERROR_NOT_FOUND,
    LoadAirports,
    MapAirports,
    PlotAirports,
    RemoveAirport,
    SaveSchengenAirports,
    SetSchengen,
)

airports = []

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


def apply_styles():
    """Aplica un estilo visual suave a la interfaz."""

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

    style.map(
        "Custom.TButton",
        background=[("active", "#e6dfda")],
    )


def build_interface():
    """Construye todos los componentes de la ventana principal."""
    global root

    root.title("Airport Management - Version 1")
    root.geometry("1200x760")
    root.minsize(1020, 700)
    root.configure(bg="#f4f1ee")

    apply_styles()

    container = ttk.Frame(root, padding=12, style="Main.TFrame")
    container.pack(fill=tk.BOTH, expand=True)

    left_panel = ttk.Frame(container, padding=(0, 0, 12, 0), style="Main.TFrame")
    left_panel.pack(side=tk.LEFT, fill=tk.Y)

    right_panel = ttk.Frame(container, style="Main.TFrame")
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    build_form(left_panel)
    build_buttons(left_panel)
    build_table(right_panel)
    build_log(right_panel)
    build_plot_area(right_panel)


def build_form(parent):
    """Crea el formulario para añadir nuevos aeropuertos."""
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
        text="Asignar Schengen automáticamente",
        variable=autoschengen_var,
    ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=4, pady=6)

    ttk.Button(
        form,
        text="Añadir aeropuerto",
        command=add_airport,
        style="Custom.TButton",
    ).grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(6, 2))

    form.columnconfigure(1, weight=1)


def build_buttons(parent):
    """Crea el panel de botones principales."""
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
        text="Gráfico",
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

    for column in range(2):
        buttons.columnconfigure(column, weight=1)


def build_table(parent):
    """Crea la tabla donde se muestran los aeropuertos."""
    ttk.Label(parent, text="Aeropuertos cargados", style="Custom.TLabel").pack(anchor=tk.W)

    columns = ("code", "lat", "lon", "schengen")

    global tree
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)

    tree.heading("code", text="ICAO")
    tree.heading("lat", text="Latitud")
    tree.heading("lon", text="Longitud")
    tree.heading("schengen", text="Schengen")

    tree.column("code", width=90, anchor=tk.CENTER)
    tree.column("lat", width=140, anchor=tk.CENTER)
    tree.column("lon", width=140, anchor=tk.CENTER)
    tree.column("schengen", width=120, anchor=tk.CENTER)

    tree.pack(fill=tk.BOTH, expand=False)
    tree.bind("<<TreeviewSelect>>", show_selected)


def build_log(parent):
    """Crea la zona de texto para mostrar mensajes."""
    ttk.Label(parent, text="Información", style="Custom.TLabel").pack(anchor=tk.W, pady=(10, 0))

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
    """Crea la zona donde se incrusta la gráfica dentro de la interfaz."""
    ttk.Label(parent, text="Gráfico integrado", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global figure
    global axes
    global canvas

    figure = Figure(figsize=(6.8, 4.8), dpi=100)
    axes = figure.add_subplot(111)
    axes.set_title("Schengen / No Schengen airports")
    axes.set_ylabel("Number of airports")

    figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    canvas = FigureCanvasTkAgg(figure, master=plot_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()


def log_message(message):
    """Escribe un mensaje en la zona de información."""
    details.insert(tk.END, message + "\n")
    details.see(tk.END)


def clear_log():
    """Borra el contenido de la zona de información."""
    details.delete("1.0", tk.END)


def clear_input_fields():
    """Limpia los campos del formulario."""
    code_var.set("")
    lat_var.set("")
    lon_var.set("")


def apply_schengen_flags():
    """Actualiza el atributo Schengen de todos los aeropuertos."""
    for airport in airports:
        SetSchengen(airport)


def selected_index():
    """Devuelve el índice del aeropuerto seleccionado."""
    selection = tree.selection()
    index = -1

    if len(selection) > 0:
        iid = selection[0]

        if str(iid).isdigit():
            possible_index = int(iid)

            if 0 <= possible_index < len(airports):
                index = possible_index

    return index


def selected_airport():
    """Devuelve el aeropuerto seleccionado."""
    airport = None
    index = selected_index()

    if index != -1:
        airport = airports[index]

    return airport


def refresh_list():
    """Actualiza la tabla con la lista actual."""
    apply_schengen_flags()

    for item in tree.get_children():
        tree.delete(item)

    for index, airport in enumerate(airports):
        tree.insert(
            "",
            tk.END,
            iid=str(index),
            values=(
                airport["code"],
                f"{airport['latitude']:.6f}",
                f"{airport['longitude']:.6f}",
                "Sí" if airport["schengen"] else "No",
            ),
        )


def load_file():
    """Carga una lista de aeropuertos desde un fichero."""
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
                "No se ha cargado ningún aeropuerto. Revisa el fichero seleccionado.",
            )


def show_selected(_event=None):
    """Muestra en el panel inferior la información del aeropuerto seleccionado."""
    airport = selected_airport()

    if airport is not None:
        clear_log()
        log_message(f"Código ICAO: {airport['code']}")
        log_message(f"Latitud: {airport['latitude']:.6f}")
        log_message(f"Longitud: {airport['longitude']:.6f}")
        log_message(f"Schengen: {'Sí' if airport['schengen'] else 'No'}")


def show_all():
    """Muestra en el panel inferior todos los aeropuertos cargados."""
    apply_schengen_flags()
    clear_log()

    if len(airports) == 0:
        log_message("No hay aeropuertos cargados.")
    else:
        log_message("Lista actual de aeropuertos:")
        log_message("")

        for airport in airports:
            log_message(
                f"{airport['code']} | "
                f"Lat: {airport['latitude']:.6f} | "
                f"Lon: {airport['longitude']:.6f} | "
                f"Schengen: {'Sí' if airport['schengen'] else 'No'}"
            )


def add_airport():
    """Añade un aeropuerto a partir de los datos del formulario."""
    code = code_var.get().strip()
    valid_data = True
    latitude = 0.0
    longitude = 0.0

    if code == "":
        valid_data = False
        messagebox.showerror("Error", "El código ICAO no puede estar vacío.")

    if valid_data:
        try:
            latitude = float(lat_var.get())
            longitude = float(lon_var.get())
        except ValueError:
            valid_data = False
            messagebox.showerror("Error", "Latitud y longitud deben ser números reales.")

    if valid_data:
        airport = Airport(code, latitude, longitude)

        if autoschengen_var.get():
            SetSchengen(airport)

        added = AddAirport(airports, airport)

        if added:
            refresh_list()
            clear_input_fields()
            clear_log()
            log_message(f"Aeropuerto añadido correctamente: {airport['code']}")
        else:
            messagebox.showwarning("Aviso", "Ese aeropuerto ya existe en la lista.")


def remove_selected():
    """Elimina de la lista el aeropuerto seleccionado."""
    airport = selected_airport()

    if airport is None:
        messagebox.showinfo("Información", "Selecciona un aeropuerto en la tabla.")
    else:
        result = RemoveAirport(airports, airport["code"])

        if result == ERROR_NOT_FOUND:
            messagebox.showwarning("Aviso", "No se encontró el aeropuerto a eliminar.")
        else:
            refresh_list()
            clear_log()
            log_message(f"Aeropuerto eliminado: {airport['code']}")


def detect_schengen():
    """Actualiza el atributo Schengen del aeropuerto seleccionado o de todos."""
    airport = selected_airport()

    if airport is not None:
        SetSchengen(airport)
        refresh_list()
        clear_log()
        log_message(f"Atributo Schengen actualizado para: {airport['code']}")
    else:
        apply_schengen_flags()
        refresh_list()
        clear_log()
        log_message("Atributo Schengen actualizado para toda la lista.")


def save_schengen():
    """Guarda en fichero solo los aeropuertos Schengen."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "No hay aeropuertos para guardar.")
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
    """Muestra el gráfico integrado dentro de la propia interfaz."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "Carga o añade aeropuertos primero.")
    else:
        apply_schengen_flags()
        drawn = PlotAirports(airports, axes)

        if drawn:
            figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            canvas.draw()
            clear_log()
            log_message("Gráfico actualizado dentro de la interfaz.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el gráfico.")


def map_airports():
    """Genera el fichero KML y trata de abrirlo."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "Carga o añade aeropuertos primero.")
    else:
        apply_schengen_flags()
        filename = MapAirports(airports)

        if filename is None:
            messagebox.showerror("Error", "No se pudo generar el fichero KML.")
        else:
            clear_log()
            log_message(f"Fichero KML generado: {filename}")
            log_message("Ábrelo con Google Earth si no se muestra automáticamente.")


def main():
    """Punto de entrada principal del programa."""
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