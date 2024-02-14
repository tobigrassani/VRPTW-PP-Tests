import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import folium.plugins as plugins
import pandas as pd
import folium
import webbrowser

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

        # Actualizar la tabla con los datos importados
        tabla.delete(*tabla.get_children())
        for index, row in df.iterrows():
            tabla.insert("", "end", values=(row['Nombre'], row['Latitud'], row['Longitud'], row['Cliente']))


# Función para crear el gráfico visualizando los marcadores en un mapa de Folium
def crear_grafico():
    global df

    if df is not None:
        # Crear un mapa de Folium
        mapa = folium.Map()

        # Crear una lista para almacenar las coordenadas de los puntos
        coordenadas = []

        # Iterar sobre las filas del DataFrame para agregar marcadores al mapa y a la lista de coordenadas
        for index, row in df.iterrows():

            coordenadas.append((row['Latitud'], row['Longitud']))
            # Personalizar el marcador con el nombre del cliente como tooltip y el nombre como contenido del popup
            if index == 0:  # Si es el primer marcador
                icono = plugins.BeautifyIcon(
                    icon="map-marker",
                    icon_shape="marker",
                    number=str(index + 1),
                    border_color="#c20000",
                    background_color="#c20000",
                    text_color='white',
                    inner_icon_style='font-size:1.2em;vertical-align:middle;horizontal-align:middle'
                )
            elif index == len(df) - 1:  # Si es el último marcador
                icono = plugins.BeautifyIcon(
                    icon="map-marker",
                    icon_shape="marker",
                    number=str(index + 1),
                    border_color="black",
                    background_color="black",
                    text_color='white',
                    inner_icon_style='font-size:1.2em;vertical-align:middle;horizontal-align:middle'
                )
            else:
                icono = plugins.BeautifyIcon(
                    icon= "map-marker",
                    icon_shape= "marker",
                    number= str(index + 1),
                    border_color="#2a8c4a",
                    background_color="#2a8c4a",
                    text_color='white',
                    inner_icon_style='font-size:1.3em;vertical-align:middle;horizontal-align:middle'
                )
            folium.Marker(location=[row['Latitud'], row['Longitud']],
                          tooltip="<b><h4>" + str(row['Cliente']) + "</h4></b>",
                          popup="<b><h5>" + str(row['Cliente']) + "</h5></b>" + "<dd>" +  row['Nombre'] + "</dd>",
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

        # Guardar el mapa en un archivo HTML
        mapa.save(mapa_html)

        # Abrir el mapa en el navegador web predeterminado
        webbrowser.open(mapa_html)

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

# Sección para importar el archivo Excel o CSV
ttk.Label(frame_importar_excel, text="Importar archivo:").pack(side=tk.LEFT, padx=10)
btn_importar_marcadores = ttk.Button(frame_importar_excel, text="Importar", command=importar_marcadores)
btn_importar_marcadores.pack(side=tk.LEFT, padx=5)

# Sección para visualizar la tabla importada
tabla = ttk.Treeview(frame_tabla, columns=("Nombre", "Latitud", "Longitud", "Cliente"))
tabla.heading("#0", text="Indice")
tabla.heading("Nombre", text="Nombre")
tabla.heading("Latitud", text="Latitud")
tabla.heading("Longitud", text="Longitud")
tabla.heading("Cliente", text="Cliente")  # Nueva columna para el cliente
tabla.pack(expand=True, fill=tk.BOTH)

# Sección para visualizar el gráfico
btn_crear_grafico = ttk.Button(frame_grafico, text="Crear Gráfico", command=crear_grafico)
btn_crear_grafico.pack()

# Ejecutar la aplicación
ventana.mainloop()
