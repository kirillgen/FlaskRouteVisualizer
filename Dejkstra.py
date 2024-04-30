import queue, heapq

# Реализация BFS (обход графа в ширину)

def bfs_search(graph, start_node):
    visited = set()
    q = queue.Queue()
    q.put(start_node)
    order = []

    while not q.empty():
        vertex = q.get()
        if vertex not in visited:
            visited.add(vertex)
            order.append(vertex)
            for node in graph[vertex]:
                if node not in visited:
                    q.put(node)

    return order

# Реализация DFS (обход графа в глубину)

def dfs_search(graph, start_node, visited=None) -> list:
    if visited is None:
        visited = set()

    order = []

    if start_node not in visited:
        order.append(start_node)
        visited.add(start_node)
        for node in graph[start_node]:
            if node not in visited:
                order.extend(dfs_search(graph, node, visited))

    return order
