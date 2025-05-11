from geopy.distance import geodesic
from parsetestingpbf import CounterHandler, shortest_path, find_nearest_point
from collections import OrderedDict

class RoutePredictor:
    def __init__(self, map_file="Map/liechtenstein-latest.osm.pbf"):
        self.map_file = map_file
        self.handlers = {}  # Кеш графов для разных типов маршрутов
        self.route_cache = OrderedDict()
        self.cache_size = 100  # Можно увеличить/уменьшить

    def get_handler(self, route_type):
        if route_type not in self.handlers:
            print(f"Создаю новый граф для типа маршрута: {route_type}")
            handler = CounterHandler(route_type)
            handler.apply_file(self.map_file)
            handler.build_graph()
            self.handlers[route_type] = handler
        return self.handlers[route_type]

    def predict(self, start_point, end_point, route_type='car'):
        print(f"RoutePredictor: start={start_point}, end={end_point}, type={route_type}")
        try:
            if isinstance(start_point, str):
                start_point = tuple(map(float, start_point.split()))
            if isinstance(end_point, str):
                end_point = tuple(map(float, end_point.split()))

            if not self._is_valid_coordinates(start_point) or not self._is_valid_coordinates(end_point):
                print("Некорректные координаты!")
                return {'error': 'Некорректные координаты'}

            cache_key = (start_point, end_point, route_type)
            if cache_key in self.route_cache:
                print("Маршрут найден в кеше!")
                self.route_cache.move_to_end(cache_key)
                return self.route_cache[cache_key]

            handler = self.get_handler(route_type)
            print(f"Ищу ближайшие узлы для точек: {start_point}, {end_point}")
            start_node = find_nearest_point(handler.graph, handler.nodes, f"{start_point[0]} {start_point[1]}")
            end_node = find_nearest_point(handler.graph, handler.nodes, f"{end_point[0]} {end_point[1]}")
            print(f"Ближайшие узлы: start_node={start_node}, end_node={end_node}")

            if not start_node or not end_node:
                print("Не удалось найти ближайшие точки на карте!")
                return {'error': 'Не удалось найти ближайшие точки на карте'}

            print(f"Запускаю алгоритм Дейкстры для поиска маршрута...")
            distance, path = shortest_path(handler.distances, start_node, end_node)
            print(f"Результат Дейкстры: distance={distance}, path={path}")

            if not path:
                print("Маршрут не найден!")
                return {'error': 'Маршрут не найден'}

            route_coords = [handler.nodes[str(node)] for node in path]

            # Расчёт времени маршрута
            duration = handler.calculate_route_time(path, route_type)

            print(f"Время маршрута: {duration} ч")

            result = {
                'route': [{'lat': lat, 'lng': lon} for lat, lon in route_coords],
                'distance': distance,
                'duration': duration
            }
            self.route_cache[cache_key] = result
            if len(self.route_cache) > self.cache_size:
                self.route_cache.popitem(last=False)
            print(f"Маршрут успешно построен и добавлен в кеш!")
            return result
        except Exception as e:
            print(f"Ошибка при построении маршрута: {str(e)}")
            return {'error': f'Ошибка при построении маршрута: {str(e)}'}

    def _is_valid_coordinates(self, coords):
        if not isinstance(coords, tuple) or len(coords) != 2:
            return False
        lat, lon = coords
        return -90 <= lat <= 90 and -180 <= lon <= 180 