import xml.etree.ElementTree as ET
import tkinter
import tkintermapview

# Парсинг данных из xml файла
tree = ET.parse('Map/testmapdata.osm')
root = tree.getroot()

# Парсим max и min точки из файла
x_min = root[0].get('minlon')
x_max = root[0].get('maxlon')

y_min = root[0].get('minlat')
y_max = root[0].get('maxlat')

bounds = [x_min, x_max, y_min, y_max]



# Парсинг id и lat, lon + создание словаря {'id': {lat, lon}}

graph = {}

# Парсинг данных из файла и создание словаря: {id: (lat, lon)}

for node in root.findall("node"):
    node_id = node.get("id")
    lat = float(node.get("lat"))
    lon = float(node.get("lon"))
    graph[node_id] = (lat, lon)


# print(len(root.findall('node')))

# print(graph)


root_window = tkinter.Tk()
root_window.geometry(f"{800}x{600}")
root_window.title("Map Testing")

map_widget = tkintermapview.TkinterMapView(root_window, width=1920, height=1080, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")

map_widget.set_position(53.8928062, 27.5442249)
map_widget.set_zoom(14)

coords = list(graph.values())


# Отображение точек на карте
for i in range(len(coords)):
    map_widget.set_marker(coords[i][0], coords[i][1])

# Соединение всех точек
# map_widget.set_path(coords)


root_window.mainloop()

