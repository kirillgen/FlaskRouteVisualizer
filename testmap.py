import tkinter
import tkintermapview
# import ast # модуль для конвертации строки в tuple

# Дейкстра и попытки его применить на картку
# dist_graph = {}
def build_distance_graph(file_path: str) -> dict:
    distance_graph = {}
    with open(file_path, encoding='utf-8') as file:
        while True:
            cur_line = file.readline()
            if cur_line:
                city1 = cur_line.split('\t')[0]
                city2 = cur_line.split('\t')[1]
                dist = cur_line.split('\t')[2].strip('\n')
                if city1 not in distance_graph:
                    distance_graph[city1] = []
                if city2 not in distance_graph:
                    distance_graph[city2] = []
                distance_graph[city1].append([city2, int(dist)])
                distance_graph[city2].append([city1, int(dist)])
            else:
                break
    return distance_graph

def shortest_distances(distance_graph: dict, start_vertex: str) -> (dict, dict):
    if start_vertex not in distance_graph:
        return 'Неверная точка', {}
    visited = set()
    distances = {elem: float('inf') for elem in distance_graph}
    prev_nodes = {elem: None for elem in distance_graph}
    distances[start_vertex] = 0
    for _ in range(len(distance_graph) - 1):
        cur_vertex = min((v for v in distance_graph if v not in visited), key=lambda v: distances[v])
        visited.add(cur_vertex)
        for neighbor, dist in distance_graph[cur_vertex]:
            if neighbor in visited:
                continue
            new_distance = distances[cur_vertex] + dist
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                prev_nodes[neighbor] = cur_vertex
    return distances, prev_nodes

def convert_coordinates(point_str):
    lat, lon = map(float, point_str[1:-1].split(','))
    return lat, lon




graph = build_distance_graph('data.txt')

# distances = sorted(shortest_distances(graph, '(53.8928121, 27.5453602)').items(), key=lambda x: x[1])

# print(f"dist_graph: {graph}")


root_window = tkinter.Tk()
root_window.geometry(f"{1920}x{1080}")
root_window.title("Map Testing")

map_widget = tkintermapview.TkinterMapView(root_window, width=1920, height=1080, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")


map_widget.set_position(53.8928062, 27.5442249)
map_widget.set_zoom(14)


# Получение кратчайших расстояний и путей
start_node = '(53.8927267, 27.5458135)'
distances, paths = shortest_distances(graph, start_node)

# Построение маршрута
route = []
current_node = '(53.8937536, 27.5499859)'
while current_node is not None:
    route.append(current_node)
    current_node = paths.get(current_node)

# Преобразование координат маршрута
route_coordinates = [convert_coordinates(point) for point in route]

# Отображение маршрута на карте
map_widget.set_path(route_coordinates)


path_coordinates = [(float(point[1:11]), float(point[13:23])) for point in graph]

for point in graph:
    map_widget.set_marker(float(point[1:11]), float(point[13:23]))


root_window.mainloop()
