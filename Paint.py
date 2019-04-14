from tkinter import *
from Color import Color
from os.path import isfile


start_figure_size = 10

class HistoryRecord():
    u"""Запись в истории фигур"""
    def __init__(self, **param):
        # координата по x (относительная)
        self.x = param["x"]
        # координата по y (относительная)
        self.y = param["y"]
        # цвет - строка-код (color.code)
        self.color = param["color"]
        # тип (fig_type)
        self.type = param["type"]
        # название функции расстояния (distance_func_name)
        self.distance = param["distance"]
        # время (каждый клик мышкой увеличивает время на 1)
        self.time = param["time"]


class Paint(Canvas):
    u"""Класс виджета для рисования.
    Обеспечивает рисование с отображением, а также:
        сохранение экземпляра в файл
        восстановление экземпляра из файла
        отмену последних действий
        очистку
        перерисовку в зависимости от размера
        использование разных палитр"""
    def __init__(self, master=None, *ap, **an):
        Canvas.__init__(self, master, *ap, **an)
        self.fig_size = start_figure_size
        self.fig_type = 'circle'
        # None в color_pick означает, что будет выбираться автоматически
        self.color_pick = None
        # стартовый цвет
        self.color = Color()
        self.bind('<B1-Motion>', self.mousemove)
        self.bind('<Button-1>', self.mousedown)
        self.bind('<ButtonRelease-1>', self.mouseup)
        self.bind('<Configure>', lambda event: self.repaint())
        # загрузка палитры
        self.define_pallete()
        # выбор функции масштаба
        self.set_scale_function('const')
        # история - список из HistoryRecord
        self.history = []
        # время (каждый клик мышкой увеличивает время на 1)
        self.time = 0

    def mousemove(self, event):
        u"""Обработка события движения мышки."""
        self.history.append(HistoryRecord(
            x = event.x / self.winfo_width(),
            y = event.y / self.winfo_height(),
            color = self.color.code,
            type = self.fig_type,
            distance = self.distance_func_name,
            time = self.time
        ))
        self.create_figure(int(event.x), int(event.y))

    def mousedown(self, event):
        u"""Очистка хвоста истории после undo (т.е. нельзя будет сделать его redo).
        Реализует отмену действия всего нажатия мыши(по аналогии с редакторами) """
        while self.history and self.history[-1].time > self.time:
            self.history.pop()
        # счёт времени
        self.time += 1

    def mouseup(self, event):
        pass

    def cleanup(self):
        u"""Очистка холста и истории действий"""
        self.history = []
        self.time = 0
        self.delete("all")

    def undo(self):
        u"""Отмена действия"""
        if self.time > 0:
            self.time -= 1
        self.repaint()

    def redo(self):
        u"""Отмена отвены"""
        if self.history and self.history[-1].time > self.time:
            self.time += 1
        self.repaint()

    def save(self):
        u"""Сохранение картинки в файл"""
        filename = filedialog.asksaveasfilename(
            initialdir = "/",
            title = "Выберите файл",
            filetypes = (("kaleidoscope files", "*.kld"),)
        )
        if not filename:
            return
        try:
            with open(filename, "w") as f:
                for h in self.history:
                    f.write(
                        str(h.x) + " " +
                        str(h.y) + " " +
                        h.color + " " +
                        h.type + " " +
                        h.distance + " " +
                        "\n")
        except BaseException:
            self.history = []
            messagebox.showerror(
                "Ошибка",
                "В процессе сохранения файла произошла ошибка")

    def load(self):
        u"""Загрузка картинки из файла"""
        filename = filedialog.askopenfilename(
            initialdir = "/",
            title = "Выберите файл",
            filetypes = (("kaleidoscope files", "*.kld"),)
        )
        if not filename:
            return
        self.history = []
        self.time = 1
        try:
            with open(filename, "r") as f:
                for l in f.readlines():
                    l = l.split()
                    self.history.append(HistoryRecord(
                        x = float(l[0]),
                        y = float(l[1]),
                        color = l[2],
                        type = l[3],
                        distance = l[4],
                        time = 1
                    ))
        except BaseException:
            self.history = []
            messagebox.showerror(
                "Ошибка",
                "В процессе загрузки файла произошла ошибка")
        self.repaint()

    def repaint(self):
        u"""Перерисовка картинки согласно истории"""
        self.delete("all")
        for h in self.history:
            if h.time > self.time:
                continue
            self.color.code = h.color
            self.color.decode()
            self.set_style(h.type)
            self.set_scale_function(h.distance)
            x = int(h.x * self.winfo_width())
            y = int(h.y * self.winfo_height())
            self.create_figure(x, y)

    def set_style(self, string):
        u"""Сеттер стиля кисти"""
        self.fig_type = string

    def create_figure(self, coord_x, coord_y):
        u"""Метод, рисующий с отображением (x, y - координаты базовой фигуры)"""
        # переменные размеров окна
        x_size = self.winfo_width()
        y_size = self.winfo_height()

        # изменение цвета
        color = next(self.color)
        x_center = coord_x - x_size/2
        y_center = coord_y - y_size/2
        # масштаб - в зависимости от расстояния до центра
        size = self.fig_size * self.distance_func(x_center, y_center)

        # переключение разных фигур с помощью self.fig_type
        if self.fig_type == 'triangle':
            create_poly = self.create_polygon

            def figure_function(x1, y1, x2, y2, **kwargs):
                # Треугольник, обращённый углом к центру
                x0 = (x1+x2)/2
                rx = x0 - x_size/2
                y0 = (y1+y2)/2
                ry = y0 - y_size/2
                rho = self.distance_func(rx, ry)
                dx = rho * (x2-x1)/4
                dy = rho * (y2-y1)/4
                create_poly(
                    round(x0 - dx), round(y0 + dy),
                    round(x0 + dx), round(y0 + dy),
                    round(x0 + dx), round(y0 - dy),
                    **kwargs)
        elif self.fig_type == 'circle':
            figure_function = self.create_oval
        elif self.fig_type == 'square':
            figure_function = self.create_rectangle
        else:
            print('Warning')
            return None

        # координаты фигуры
        point1 = coord_x - size, coord_y - size
        point2 = coord_x + size, coord_y + size

        self.figure_symmetry(figure_function, point1, point2, color)
        return None

    def figure_symmetry(self, func, point1, point2, color):
        u"""Функция симметричного отображения относительно главных диагоналей."""
        # коэффициенты растяжения для отображения относительно диагоналей

        x1, y1 = point1
        x2, y2 = point2
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        x_k = y_size / x_size
        y_k = x_size / y_size

        # 8 кругов
        kwargs = {'fill': color, 'width': 0}
        for A1, A3 in [(x1, x2), (x_size - x1, x_size-x2)]:
            for B2, B4 in [(y_size-y1, y_size-y2), (y1, y2)]:
                func(round(A1), round(B2), round(A3), round(B4), **kwargs)
        for A1, A3 in [(y1 * y_k, y2 * y_k), ((y_size-y1) * y_k, (y_size-y2) * y_k)]:
            for B2, B4 in [(x1 * x_k, x2 * x_k), ((x_size-x1) * x_k, (x_size-x2) * x_k)]:
                func(round(A1), round(B2), round(A3), round(B4), **kwargs)

    def define_pallete(self, index=-1):
        u"""Определение палитры, если возможно, её загрузка из файла"""
        if index > 0:
            if isfile('./palette{}.txt'.format(str(index))):
                palette = []
                with open('./palette{}.txt'.format(str(index))) as palette_text:
                    for line in palette_text:
                        count = len(line)//6
                        for i in range(count):
                            position = i*6
                            palette.append('#'+line[position:position+6])

                def cycle(palette):
                    while palette:
                        for element in palette:
                            yield element
                self.color.palette = cycle(palette)
            else:
                messagebox.showerror(
                    "Ошибка загрузки палитры.",
                    "Внимание!\n\
Не удалось загрузить файл палитры.\
\nУстановлено случайное изменение цветов.")
                self.color.palette = []
        else:
            self.color.random_color = index
            if self.color.palette:
                self.color.decode()
            self.color.palette = []

    def set_scale_function(self, string=''):
        u"""Выбор масштабирущей функции"""
        if string == 'manhatten':
            def func(x_center, y_center):
                rho = (abs(x_center) + abs(y_center))*start_figure_size
                screen_factor = self.winfo_width() + self.winfo_height()
                return rho / screen_factor
        elif string == 'square_dist':
            def func(x_center, y_center):
                rho = x_center*x_center + y_center*y_center
                screen_factor = self.winfo_width() * self.winfo_height()
                return rho / screen_factor * start_figure_size
        elif string == 'inv_Chebushev':
            def func(x_center, y_center):
                coef = start_figure_size
                rho = min(abs(x_center), abs(y_center)) + coef*coef
                screen_factor = sqrt(self.winfo_width() * self.winfo_height())
                return screen_factor / rho
        elif string == "inverse_dist":
            def func(x_center, y_center):
                rho = x_center*x_center + y_center*y_center
                screen_factor = self.winfo_width()*self.winfo_height()
                return 1 / (sqrt(rho) / sqrt(screen_factor) + 0.15)
        elif string == "const":
            func = lambda x, y: 1
        else:
            print("Warning")
        self.distance_func_name = string
        self.distance_func = func