# Работа с картой
root_window = tkinter.Tk()
root_window.geometry(f"{1920}x{1080}")
root_window.title("Приложение для построения маршрутов на карте Лихтенштейна")

map_widget = tkintermapview.TkinterMapView(root_window, width=1920, height=1080, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")

# Создание кнопок
text_above = tkinter.Label(root_window, text="Выберите тип движения")
button_car = tkinter.Button(root_window, text='Дорожный')
button_walk = tkinter.Button(root_window, text='Пеший')

# Создание полей для ввода координат
coord_from = tkinter.Entry(root_window)
coord_to = tkinter.Entry(root_window)

#
coord_from.grid(row=2, column=1, columnspan=2, sticky='we')
start_node = coord_from.bind("<FocusOut>", on_focus_out_from())

coord_to.grid(row=3, column=1, columnspan=2, sticky='we')
target_node = coord_to.bind("<FocusOut>", on_focus_out_to())

tkinter.Label(root_window, text="Откуда").grid(row=2, column=0, sticky='w')
tkinter.Label(root_window, text="Куда").grid(row=3, column=0, sticky='w')

#
text_above.grid(row=0, column=0, columnspan=2, sticky='we', pady='10px', )
button_car.grid(row=1, column=0, sticky='we')
button_walk.grid(row=1, column=1, sticky='we')

start_button = tkinter.Button(root_window, text="Построить маршрут",
                              command=shortest_path(h.distances, start_node, target_node))
start_button.grid(row=4, column=0, columnspan=2, sticky='we', pady='10px')

map_widget.set_position(h.nodes[str(start_node)][0], h.nodes[str(start_node)][1])

map_widget.set_zoom(14)

map_widget.mainloop()
