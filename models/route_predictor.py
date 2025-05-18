from geopy.distance import geodesic
from parsetestingpbf import CounterHandler, shortest_path, find_nearest_point
from collections import OrderedDict
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class OpenRouteServiceClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ORS_API_KEY')
        self.base_url = "https://api.openrouteservice.org"
        
    def get_route_duration(self, start_coords, end_coords, route_type='car'):
        """
        Получает только время прохождения маршрута через OpenRouteService Matrix API
        
        Args:
            start_coords: tuple(float, float) - координаты начальной точки (lat, lon)
            end_coords: tuple(float, float) - координаты конечной точки (lat, lon)
            route_type: str - тип маршрута ('car' или 'walking')
        
        Returns:
            float: время в часах или None в случае ошибки
        """
        if not self.api_key:
            raise ValueError("OpenRouteService API key не установлен")
            
        # Определяем профиль маршрута для API
        profile = "driving-car" if route_type == 'car' else "foot-walking"
            
        # Конвертируем координаты в формат [lon, lat] как требует API
        locations = [
            [start_coords[1], start_coords[0]],  # ORS требует формат [lon, lat]
            [end_coords[1], end_coords[0]]
        ]
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            "locations": locations,
            "metrics": ["duration"],  # Запрашиваем только время
            "units": "km"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/matrix/{profile}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Возвращаем только время в часах
            return result['durations'][0][1] / 3600
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к OpenRouteService: {str(e)}")
            return None

class RoutePredictor:
    def __init__(self, map_file="Map/liechtenstein-latest.osm.pbf"):
        self.map_file = map_file
        self.handlers = {}
        self.route_cache = OrderedDict()
        self.cache_size = 100
        self.ors_client = OpenRouteServiceClient()

    def predict(self, start_point, end_point, route_type='car'):
        """
        Строит маршрут используя локальный алгоритм Дейкстры и получает время прохождения через API
        """
        print(f"RoutePredictor: start={start_point}, end={end_point}, type={route_type}")
        try:
            if isinstance(start_point, str):
                start_point = tuple(map(float, start_point.split()))
            if isinstance(end_point, str):
                end_point = tuple(map(float, end_point.split()))

            if not self._is_valid_coordinates(start_point) or not self._is_valid_coordinates(end_point):
                print("Некорректные координаты!")
                return {'error': 'Некорректные координаты'}

            # Проверяем тип маршрута
            if route_type not in ['car', 'walking']:
                return {'error': 'Поддерживаются только автомобильные и пешие маршруты'}

            cache_key = (start_point, end_point, route_type)
            if cache_key in self.route_cache:
                print("Маршрут найден в кеше!")
                self.route_cache.move_to_end(cache_key)
                return self.route_cache[cache_key]

            # Построение маршрута с помощью локального алгоритма Дейкстры
            route_data = self._build_route(start_point, end_point, route_type)
            if 'error' in route_data:
                return route_data

            # Получение времени прохождения маршрута через API
            api_duration = self.ors_client.get_route_duration(start_point, end_point, route_type)
            
            # Формируем результат с обоими значениями времени
            result = {
                'route': route_data['route'],
                'distance': route_data['distance'],
                'duration': {
                    'local': route_data['duration'],
                    'api': api_duration if api_duration is not None else None,
                    'selected': api_duration if api_duration is not None else route_data['duration']
                },
                'route_type': route_type
            }
            
            self.route_cache[cache_key] = result
            if len(self.route_cache) > self.cache_size:
                self.route_cache.popitem(last=False)
            print(f"Маршрут успешно построен и добавлен в кеш!")
            return result
            
        except Exception as e:
            print(f"Ошибка при построении маршрута: {str(e)}")
            return {'error': f'Ошибка при построении маршрута: {str(e)}'}

    def _build_route(self, start_point, end_point, route_type):
        """
        Строит маршрут используя локальный алгоритм Дейкстры
        """
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
        duration = handler.calculate_route_time(path, route_type)

        return {
            'route': [{'lat': lat, 'lng': lon} for lat, lon in route_coords],
            'distance': distance,
            'duration': duration
        }

    def get_handler(self, route_type):
        if route_type not in self.handlers:
            print(f"Создаю новый граф для типа маршрута: {route_type}")
            handler = CounterHandler(route_type)
            handler.apply_file(self.map_file)
            handler.build_graph()
            self.handlers[route_type] = handler
        return self.handlers[route_type]

    def _is_valid_coordinates(self, coords):
        if not isinstance(coords, tuple) or len(coords) != 2:
            return False
        lat, lon = coords
        return -90 <= lat <= 90 and -180 <= lon <= 180 