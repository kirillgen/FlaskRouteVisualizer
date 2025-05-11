import osmium
import tkinter
import tkintermapview
from geopy.distance import geodesic
import heapq
import time


class CounterHandler(osmium.SimpleHandler):
    def __init__(self, way_type):
        super().__init__()
        # osmium.SimpleHandler.__init__(self)
        self.type_of_way = way_type
        self.nodes = {}
        self.ways = {}
        self.graph = {}
        self.distances = {}
        self.highway_by_car = {
                                'motorway', 'motorway_link', 'trunk', 'trunk_link',
                                'primary', 'primary_link', 'secondary', 'secondary_link',
                                'tertiary', 'tertiary_link', 'residential', 'unclassified',
                                'living_street', 'service', 'driveway', 'parking_aisle', 'road'
                            }

        self.highway_by_walk = {
            'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link',
            'secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'residential',
            'unclassified', 'living_street', 'service', 'driveway', 'parking_aisle',
            'road', 'track', 'path', 'steps', 'cycleway', 'parking_aisle',
            'bridleway', 'crossing', 'pedestrian', 'footway'
        }

        self.road_speeds = {
            'motorway': 110, 'motorway_link': 60, 'trunk': 90, 'trunk_link': 60,
            'primary': 70, 'primary_link': 50, 'secondary': 60, 'secondary_link': 50,
            'tertiary': 50, 'tertiary_link': 40, 'residential': 30, 'unclassified': 30,
            'living_street': 20, 'service': 20, 'driveway': 15, 'parking_aisle': 10, 'road': 30
        }

    def node(self, n):
        lat = n.location.lat
        lon = n.location.lon
        self.nodes[str(n.id)] = (lat, lon)

    # метод для парсинга путей из файла
    def way(self, w):
        way_id = w.id
        nodes_in_way = [node.ref for node in w.nodes]

        tags = []
        if w.tags:
            tags = [{'k': tag.k, 'v': tag.v} for tag in w.tags]

        if self.type_of_way == 'car':
            if not self.is_car_accessible(tags):
                return
        elif self.type_of_way == 'walking':
            if not self.is_walk_accessible(tags):
                return
        else:
            raise ValueError("Неизвестный тип движения")

        has_building_tag = any(tag['k'] == 'building' for tag in tags)
        if has_building_tag:
            # Если ключ 'building' найден, пропускаем этот путь
            return

        self.ways[way_id] = {'id': way_id, 'nodes': nodes_in_way, 'tags': tags}

    def calculate_distance(self, node1, node2):
        """Вычисляет расстояние между двумя узлами с использованием формулы гаверсинуса."""
        lat1, lon1 = self.nodes[str(node1)]
        lat2, lon2 = self.nodes[str(node2)]
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    def build_graph(self):
        # Инициализация списка для хранения всех узлов
        all_nodes = []

        # Проходим по всем путям и собираем узлы в список
        for way_data in self.ways.values():
            all_nodes.extend(way_data['nodes'])  # Расширяем список узлов

        # Создаем граф, где каждому узлу соответствует пустой список
        self.graph = {node: [] for node in all_nodes}

        # Проходим по всем путям еще раз для заполнения графа и словаря расстояний
        for way_data in self.ways.values():
            nodes_in_way = way_data['nodes']  # Получаем узлы текущего пути

            # Проходим по узлам пути, кроме последнего
            for i in range(len(nodes_in_way) - 1):
                # Проверяем, существует ли уже ребро между текущим и следующим узлом
                if nodes_in_way[i + 1] not in self.graph[nodes_in_way[i]]:
                    # Добавляем ребро в оба направления для симметрии графа
                    self.graph[nodes_in_way[i]].append(nodes_in_way[i + 1])
                    self.graph[nodes_in_way[i + 1]].append(nodes_in_way[i])

                    # Вычисляем расстояние между узлами и сохраняем его
                    distance = self.calculate_distance(nodes_in_way[i], nodes_in_way[i + 1])

                    # Сохраняем расстояние в словаре расстояний
                    self.distances[nodes_in_way[i]] = self.distances.get(nodes_in_way[i], {}) | {
                        nodes_in_way[i + 1]: distance}  # Добавляем расстояние до следующего узла
                    self.distances[nodes_in_way[i + 1]] = self.distances.get(nodes_in_way[i + 1], {}) | {
                        nodes_in_way[i]: distance}  # Добавляем обратное расстояние

    def is_car_accessible(self, tags):
        # Проверяем явный запрет на проезд
        for tag in tags:
            if tag['k'] in ['motor_vehicle', 'vehicle', 'access'] and tag['v'] == 'no':
                return False

        highway_type = next((tag['v'] for tag in tags if tag['k'] == 'highway'), None)
        if not highway_type or highway_type not in self.highway_by_car:
            return False

        # Особая логика для road
        if highway_type == 'road':
            # Если явно указано, что только для пешеходов, велосипедистов и т.п. — не включаем
            for tag in tags:
                if tag['k'] in ['foot', 'bicycle', 'horse', 'agricultural', 'bus'] and tag['v'] == 'designated':
                    return False
            # Если явно запрещено для автомобилей — не включаем
            for tag in tags:
                if tag['k'] in ['motor_vehicle', 'vehicle', 'access'] and tag['v'] == 'no':
                    return False
            # Если явно разрешено для автомобилей — включаем
            for tag in tags:
                if tag['k'] == 'motor_vehicle' and tag['v'] == 'yes':
                    return True
            # Если нет информации — по умолчанию включаем
            return True

        return True

    def is_walk_accessible(self, tags):
        # Явный запрет для пешеходов
        for tag in tags:
            if tag['k'] in ['foot', 'access'] and tag['v'] == 'no':
                return False
        highway_type = next((tag['v'] for tag in tags if tag['k'] == 'highway'), None)
        if not highway_type or highway_type not in self.highway_by_walk:
            return False
        return True

    def find_way_by_nodes(self, node1, node2):
        for way in self.ways.values():
            nodes = way['nodes']
            for i in range(len(nodes) - 1):
                if (nodes[i] == node1 and nodes[i+1] == node2) or (nodes[i] == node2 and nodes[i+1] == node1):
                    return way
        return None

    def calculate_route_time(self, path, route_type):
        total_time_hours = 0
        if route_type == 'walking':
            speed = 5  # км/ч
            total_distance = 0
            for i in range(len(path) - 1):
                total_distance += self.distances[path[i]][path[i+1]]
            total_time_hours = total_distance / speed
        else:  # car
            for i in range(len(path) - 1):
                way = self.find_way_by_nodes(path[i], path[i+1])
                if way:
                    tags = way['tags']
                    highway_type = next((tag['v'] for tag in tags if tag['k'] == 'highway'), 'road')
                    speed = self.road_speeds.get(highway_type, 30)
                else:
                    speed = 30
                distance = self.distances[path[i]][path[i+1]]
                total_time_hours += distance / speed
        return total_time_hours


def shortest_path(distance_graph: dict, start_vertex: int, end_vertex: int):
    start_time = time.time()
    if start_vertex not in distance_graph or end_vertex not in distance_graph:
        print(f"Вершины {start_vertex} и {end_vertex} не найдены в графе.")
        return float('inf'), []

    distances = {vertex: float('inf') for vertex in distance_graph}
    previous = {vertex: None for vertex in distance_graph}
    distances[start_vertex] = 0
    queue = [(0, start_vertex)]

    while queue:
        current_distance, current_vertex = heapq.heappop(queue)
        if current_vertex == end_vertex:
            break
        for neighbor, weight in distance_graph[current_vertex].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(queue, (distance, neighbor))

    # Восстановление пути
    path = []
    current = end_vertex
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    elapsed = time.time() - start_time
    print(f"Время поиска кратчайшего пути: {elapsed:.4f} секунд")
    return distances[end_vertex], path if distances[end_vertex] != float('inf') else []

def find_nearest_point(graph_move: dict, nodes: dict, my_coords: str):
    nearest_node = None
    min_distance = float("inf")
    my_coords_tuple = tuple([float(x) for x in my_coords.split()])
    for node_id in graph_move:
        cur_coords = nodes[str(node_id)]
        dist = geodesic(my_coords_tuple, cur_coords).kilometers
        if dist < min_distance:
            min_distance = dist
            nearest_node = node_id
    return nearest_node


near_start_node = None
near_target_node = None

def get_input():
    global points
    points.append(entry.get())
    if len(points) < 2:
        tkinter.Button(root_window, text='Добавить координаты в список', command=get_input)
    else:
        run_main()


def run_main():
    global points
    print(f"Начальная точка: {points[0]}\nКонечная точка: {points[1]}")
    near_start_node = find_nearest_point(h.graph, h.nodes, points[0])
    near_target_node = find_nearest_point(h.graph, h.nodes, points[1])
    distance, short_path, *_ = shortest_path(h.distances, near_start_node, near_target_node)
    print(f"Общее расстояние: {distance} км\nКратчайший путь: {short_path}")
    wayrepr = [h.nodes[str(node)] for node in short_path]
    print(f"Список для построения пути между двумя точками: {wayrepr}")
    if wayrepr:
        map_widget.set_path(wayrepr)
    else:
        return 'Пути между двумя точками не было найдённо'

    map_widget.set_marker(h.nodes[str(near_start_node)][0], h.nodes[str(near_start_node)][1])
    map_widget.set_marker(h.nodes[str(near_target_node )][0], h.nodes[str(near_target_node)][1])
    map_widget.set_position(h.nodes[str(near_start_node)][0], h.nodes[str(near_start_node)][1])
    map_widget.set_zoom(16)

    points.clear()

if __name__ == '__main__':

    points = []

    type_of_way = 'car'  # 'walking' / 'car'

    h = CounterHandler(type_of_way)

    # Лучше использовать.pbf формат (более свежая версия)
    h.apply_file("Map/liechtenstein-latest.osm.pbf")

    h.build_graph()

    # Работа с картой
    root_window = tkinter.Tk()
    root_window.geometry(f"{1920}x{1080}")
    root_window.title("Map Testing")

    map_widget = tkintermapview.TkinterMapView(root_window, width=1920, height=1080, corner_radius=0)
    map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")

    entry = tkinter.Entry(root_window)
    entry.pack(padx=10, pady=10)

    button = tkinter.Button(root_window, text='Добавить координаты в список', command=get_input)
    button.pack(padx=10, pady=10)

    map_widget.set_zoom(12)
    map_widget.set_position(47.12020948185704, 9.56028781452834)  # установка карты на точке, которая находится в стране

    print(len(h.nodes))

    map_widget.mainloop()
