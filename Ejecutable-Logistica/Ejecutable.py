import folium

# Crear un mapa vacío
mapa = folium.Map(location=[0, 0], zoom_start=2)

# Crear marcadores para cada icono disponible en Folium
for icono in folium.Icon().classes:
    marcador = folium.Marker(location=[0, 0], icon=icono).add_to(mapa)
    marcador.add_child(folium.Popup(icono))

# Guardar el mapa en un archivo HTML
mapa.save("iconos_folium.html")