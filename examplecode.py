# import xml.etree.ElementTree as ET
#
# def osm_to_graph(osm_file):
#     tree = ET.parse(osm_file)
#     root = tree.getroot()
#
#     graph = {}
#
#     for node in root.findall("node"):
#         node_id = node.get("id")
#         lat = float(node.get("lat"))
#         lon = float(node.get("lon"))
#         graph[node_id] = {"lat": lat, "lon": lon}
#
#     for way in root.findall("way"):
#         way_id = way.get("id")
#         nodes = way.findall("nd")
#         if nodes:
#             for nd in nodes:
#                 node_id = nd.get("ref")
#                 if node_id in graph:
#                     if way_id not in graph[node_id]:
#                         graph[node_id][way_id] = []
#                     graph[node_id][way_id].append(node_id)
#
#     return graph
#

import tkinter
import tkintermapview


root_window = tkinter.Tk()
root_window.geometry(f"{800}x{600}")
root_window.title("Map Testing")

map_widget = tkintermapview.TkinterMapView(root_window, width=800, height=600, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")


map_widget.set_position(56.5043164, 21.034245)
map_widget.set_zoom(14)

root_window.mainloop()
