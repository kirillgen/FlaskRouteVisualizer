import osmium
import tkinter
import tkintermapview

class CounterHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        # self.num_nodes = 0
        self.nodes = {}
        self.ways = {}
        self.graph = {}
        self.relations = {}

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

        self.ways[way_id] = {'id': way_id, 'nodes': nodes_in_way, 'tags': tags}

    def relation(self, r):
        relation_id = r.id
        members = [{'type': member.type, 'ref': member.ref, 'role': member.role} for member in r.members]

        tags = []
        if r.tags:
            tags = [{'k': tag.k, 'v': tag.v} for tag in r.tags]

        self.relations[relation_id] = {'id': relation_id, 'members': members, 'tags': tags}

    def build_path_from_relation(self, relation_id):
        # Проверяем наличие отношения в словаре
        if relation_id not in h.relations:
            print(f"Отношение с ID {relation_id} не найдено.")
            return []

        relation = h.relations[relation_id]
        if not relation:
            return []

        path = []

        for member in relation['members']:
            if member['type'] == 'n':
                node_id = member['ref']
                if str(node_id) in h.nodes:
                    path.append(h.nodes[str(node_id)])
            elif member['type'] == 'w':
                way_id = member['ref']
                if way_id in h.ways:
                    way = h.ways[way_id]
                    for node_id in way['nodes']:
                        if str(node_id) in h.nodes:
                            path.append(h.nodes[str(node_id)])
            elif member['type'] == 'r':
                # Рекурсивно обрабатываем вложенные отношения
                if member['ref'] in h.relations:
                    path.extend(self.build_path_from_relation(member['ref']))

        return path



if __name__ == '__main__':

    #  Выбор начальной точки и точки, куда хотим добраться
    # start_node_id = 4903992
    # end_node_id = 4903993

    h = CounterHandler()

    # Лучше использовать .pbf формат (более свежая версия)
    h.apply_file("Map/liechtenstein-latest.osm.pbf")

    relation_id = 14710393

    # print(h.nodes)

    # print(h.build_path_from_relation(relation_id))

    #
    # for way in h.ways:
    #     for node_id in h.ways[way]['nodes']:
    #         if str(node_id) in h.nodes:
    #             path.append(h.nodes[str(node_id)])
    #
    # print(path)

    # nd_in_curway = []

    # for node_id in h.ways[start_node_id]['nodes']:
    #     if str(node_id) in h.nodes:
    #         nd_in_curway.append(h.nodes[str(node_id)])
    #
    # print(h.ways[start_node_id]['nodes'])
    # print(nd_in_curway)

    # for node_id in h.ways[end_node_id]['nodes']:
    #     if str(node_id) in h.nodes:
    #         nd_in_endway.append(h.nodes[str(node_id)])
    #
    # for node_id in h.ways[4904154]['nodes']:
    #     if str(node_id) in h.nodes:
    #         nd_in_endway.append(h.nodes[str(node_id)])



    # Работа с картой
    root_window = tkinter.Tk()
    root_window.geometry(f"{1920}x{1080}")
    root_window.title("Map Testing")

    map_widget = tkintermapview.TkinterMapView(root_window, width=1920, height=1080, corner_radius=0)
    map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")

    map_widget.set_position(47.1878356, 9.5504767)
    map_widget.set_zoom(14)

    cur_path = h.build_path_from_relation(relation_id)
    print(h.relations[relation_id])
    print(cur_path)
    print(f"Кол-во узлов в пути: {len(cur_path)}")

    map_widget.set_path(cur_path)


    map_widget.mainloop()



