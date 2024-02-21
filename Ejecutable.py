import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import folium.plugins as plugins
import pandas as pd
import folium
import webbrowser
import platform
import subprocess

# Variables globales para almacenar los datos del archivo importado
df = None
mapa_html = "mapa_marcadores.html"

# Función para importar marcadores desde un archivo Excel o CSV
def importar_marcadores():
    global df

    # Abrir un cuadro de diálogo para seleccionar el archivo
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo",
                                              filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Archivos CSV", "*.csv")])

    # Verificar si se seleccionó un archivo
    if ruta_archivo:
        # Leer el archivo usando pandas
        if ruta_archivo.endswith('.xlsx') or ruta_archivo.endswith('.xls'):
            df = pd.read_excel(ruta_archivo)
        elif ruta_archivo.endswith('.csv'):
            df = pd.read_csv(ruta_archivo)

        # Eliminar filas con valores NaN
        df = df.dropna()

        # Verificar si el DataFrame tiene las columnas requeridas
        required_columns = ['Nombre', 'Latitud', 'Longitud', 'Cliente']
        if not set(required_columns).issubset(df.columns):
            tk.messagebox.showerror("Error", "El archivo no contiene todas las columnas requeridas.")
            return

        # Actualizar la tabla con los datos importados
        tabla.delete(*tabla.get_children())
        column_order = df.columns.tolist()  # Obtener el orden de las columnas
        for index, row in df.iterrows():
            values = [row[column] for column in column_order]  # Obtener los valores en el orden correcto
            tabla.insert("", "end", values=values)  # Insertar la fila con los valores en el orden correcto

        # Actualizar el conteo de marcadores
        contar_marcadores()

# Función para crear el gráfico visualizando los marcadores en un mapa de Folium
def crear_grafico():
    global df
    if df is not None:
        # Crear un mapa de Folium
        mapa = folium.Map()

        # Crear una lista para almacenar las coordenadas de los puntos
        coordenadas = []

        # Crear una lista para almacenar la información de los marcadores
        lista_marcadores = []

        # Iterar sobre las filas del DataFrame para agregar marcadores al mapa y a la lista de coordenadas
        for index, row in df.iterrows():
            coordenadas.append((row['Latitud'], row['Longitud']))

            # Añadir la información del marcador a la lista
            lista_marcadores.append(f"<b>{row['Cliente']}</b>: {row['Nombre']}<br>")

            # Personalizar el marcador con el nombre del cliente como tooltip y el nombre como contenido del popup
            if index == 0:  # Si es el primer marcador
                icono = plugins.BeautifyIcon(
                    icon="map-marker",
                    icon_shape="marker",
                    number=str(index + 1),
                    border_color="#c20000",
                    background_color="#c20000",
                    text_color='white',
                    inner_icon_style='font-size:1.2em; line-height: 1.5; text-align: center;'
                )
            elif index == len(df) - 1:  # Si es el último marcador
                icono = plugins.BeautifyIcon(
                    icon="map-marker",
                    icon_shape="marker",
                    number=str(index + 1),
                    border_color="black",
                    background_color="black",
                    text_color='white',
                    inner_icon_style='font-size:1.2em; line-height: 1.5; text-align: center;'
                )
            else:
                icono = plugins.BeautifyIcon(
                    icon="map-marker",
                    icon_shape="marker",
                    number=str(index + 1),
                    border_color="#2a8c4a",
                    background_color="#2a8c4a",
                    text_color='white',
                    inner_icon_style='font-size:1.3em; line-height: 1.5; text-align: center;'
                )
            folium.Marker(location=[row['Latitud'], row['Longitud']],
                          tooltip="<b><h4>" + str(row['Cliente']) + "</h4></b>",
                          popup="<div style='min-width: 200px;'><b><h5>" + str(row['Cliente']) + "</h5></b>" + "<dd><b>Nombre:</b> " + row['Nombre'] + "</dd><dd><b>Horarios:</b> " + 'Horarios' + "</dd></div>",
                          icon=icono
                          ).add_to(mapa)

        # Calcular el centro del mapa y el nivel de zoom adecuado
        latitudes = [coord[0] for coord in coordenadas]
        longitudes = [coord[1] for coord in coordenadas]
        centro_latitud = sum(latitudes) / len(latitudes)
        centro_longitud = sum(longitudes) / len(longitudes)
        zoom = 10  # Puedes ajustar el nivel de zoom según sea necesario

        # Agregar una polilínea que conecte los puntos en orden
        folium.PolyLine(coordenadas, color="blue", weight=2.5, opacity=1).add_to(mapa)

        # Establecer el centro y el nivel de zoom del mapa
        mapa.fit_bounds([(min(latitudes), min(longitudes)), (max(latitudes), max(longitudes))], padding=(3, 3))

        # Añadir la lista de marcadores al mapa
        lista_html = """
        <div id="marcadores" style="position: absolute; top: 10px; right: 10px; background-color: white; padding: 10px; border: 1px solid black; z-index: 1000; display: none; max-height: 95vh; overflow-y: auto;">
          <h3><b>Listado Clientes</b></h3>
          <ul style="list-style-type:none; padding: 0;">
        """
        for i, marcador in enumerate(lista_marcadores):
            lista_html += f"<li><b>{i + 1}:</b> {marcador}</li>"
        lista_html += """
          </ul>
        </div>
        """
        mapa.get_root().html.add_child(folium.Element(lista_html))

        # Añadir un botón para mostrar/ocultar la lista de marcadores
        boton_html = """
        <div style="position: fixed; top: 10px; right: 10px; z-index: 1000;">
            <button onclick="toggleMarcadores()" style="background-color: #fff; border: 1px solid #999; border-radius: 4px; padding: 5px 10px;">Mostrar/Ocultar Listado Clientes</button>
        </div>
        """
        mapa.get_root().html.add_child(folium.Element(boton_html))

        # JavaScript para mostrar/ocultar la lista de marcadores
        javascript = """
        <script>
        function toggleMarcadores() {
          var marcadoresDiv = document.getElementById("marcadores");
          if (marcadoresDiv.style.display === "none") {
            marcadoresDiv.style.display = "block";
          } else {
            marcadoresDiv.style.display = "none";
          }
        }
        </script>
        """
        mapa.get_root().html.add_child(folium.Element(javascript))

        # Guardar el mapa en un archivo HTML
        mapa.save(mapa_html)

        # Abrir el mapa en el navegador web predeterminado
        abrir_archivo_html()

# Función para contar la cantidad de marcadores cargados en la tabla
def contar_marcadores():
    cantidad_marcadores = len(tabla.get_children())
    label_cantidad_marcadores.config(text=f"Cantidad de marcadores: {cantidad_marcadores}")

# Función para abrir el archivo HTML resultante según el sistema operativo
def abrir_archivo_html():
    if platform.system() == "Windows":
        webbrowser.open(mapa_html)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", mapa_html])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", mapa_html])
    else:
        print("Sistema operativo no compatible.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Visualización de Datos")

# Crear frames para cada sección
frame_importar_excel = ttk.Frame(ventana)
frame_importar_excel.pack(pady=10)

frame_tabla = ttk.Frame(ventana)
frame_tabla.pack(pady=10)

frame_grafico = ttk.Frame(ventana)
frame_grafico.pack(pady=10)

# Sección para describir los campos requeridos en el archivo
label_campos = ttk.Label(frame_importar_excel,
                         text="Campos requeridos en el archivo: Nombre, Latitud, Longitud, Cliente", font=("Arial", 12))
label_campos.pack(side=tk.TOP, pady=10)

# Sección para importar el archivo Excel o CSV
ttk.Label(frame_importar_excel, text="Importar archivo:").pack(side=tk.LEFT, padx=10)
btn_importar_marcadores = ttk.Button(frame_importar_excel, text="Importar", command=importar_marcadores)
btn_importar_marcadores.pack(side=tk.LEFT, padx=5)

# Sección para visualizar la tabla importada
tabla = ttk.Treeview(frame_tabla, columns=("Cliente", "Nombre", "Latitud", "Longitud"), show="headings")
tabla.heading("Cliente", text="Cliente")  # Nueva columna para el cliente
tabla.heading("Nombre", text="Nombre")
tabla.heading("Latitud", text="Latitud")
tabla.heading("Longitud", text="Longitud")
tabla.pack(expand=True, fill=tk.BOTH)

# Etiqueta para mostrar la cantidad de marcadores
label_cantidad_marcadores = ttk.Label(frame_tabla, text="Cantidad de marcadores: 0")
label_cantidad_marcadores.pack(side=tk.BOTTOM, pady=10)

# Sección para visualizar el gráfico
btn_crear_grafico = ttk.Button(frame_grafico, text="Crear Gráfico", command=crear_grafico)
btn_crear_grafico.pack()

# Ejecutar la aplicación
ventana.mainloop()
