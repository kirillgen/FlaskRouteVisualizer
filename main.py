import osmium
import numpy as np
from collections import defaultdict
import heapq

class CounterHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.num_nodes = 0
        self.dict_values = {}
        self.ways = defaultdict(list)

    def way(self, w):
        way_id = w.id
        nodes_in_way = [node.ref for node in w.nodes]
        for i in range(len(nodes_in_way) - 1):
            self.ways[nodes_in_way[i]].append(nodes_in_way[i+1])

    def node(self, n):
        self.num_nodes += 1
        lat = n.location.lat
        lon = n.location.lon
        self.dict_values[n.id] = (lat, lon)

if __name__ == '__main__':
    h = CounterHandler()
    h.apply_file("", locations=True)

    # Применение алгоритма Дейкстры для нахождения кратчайшего пути
    def dijkstra(graph, start, end):
        queue = [(0, start, [])]
        seen = set()
        while queue:
            (cost, node, path) = heapq.heappop(queue)
            if node not in seen:
                seen.add(node)
                path = path + [node]
                if node == end:
                    return cost, path
                for next_node in graph[node]:
                    if next_node not in seen:
                        # Вычисление расстояния по мере необходимости
                        lat1, lon1 = h.dict_values[node]
                        lat2, lon2 = h.dict_values[next_node]
                        distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                        total_cost = cost + distance
                        heapq.heappush(queue, (total_cost, next_node, path))
        return float("inf"), []

    start_node = 1252477908  # Пример идентификатора узла
    end_node = 8582810690  # Пример идентификатора узла
    cost, path = dijkstra(h.ways, start_node, end_node)
    print(f"Total cost: {cost}, Path: {path}")
