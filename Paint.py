"""
Основной модуль рисования на холсте, сохранения и загрузки истории
"""
from Color import Color
from os.path import isfile
import time
from sys import platform
from tkinter import Canvas, messagebox, filedialog

START_FIGURE_SIZE = 10

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
        # базовый размер фигуры (fig_size)
        self.size = param["size"]


class Paint(Canvas):
    u"""Класс виджета для рисования.
    Обеспечивает рисование с отображением, а также:
        сохранение экземпляра в файл
        восстановление экземпляра из файла
        отмену последних действий
        очистку
        перерисовку в зависимости от размера
        использование разных палитр"""
    def __init__(self, master, *ap, **an):
        """Инициализация с параметрами по умолчанию:
            круглая кисть;
            случайная палитра;
            константная функция масштаба"""
        Canvas.__init__(self, master, *ap, **an)
        self.fig_size = START_FIGURE_SIZE
        self.fig_type = 'circle'
        # None в color_pick означает, что будет выбираться автоматически
        self.color_pick = None
        # стартовый цвет
        self.color = Color()
        self.bind('<B1-Motion>', self.mousemove)
        self.bind('<Button-1>', self.mousedown)
        self.bind('<Configure>', lambda event: self.repaint())
        # загрузка палитры
        self.define_pallete()
        # выбор функции масштаба
        self.set_scale_function()
        # история - список из HistoryRecord
        self.history = []
        # время (каждый клик мышкой увеличивает время на 1)
        self.time = 0

    def mousemove(self, event):
        u"""Обработка события движения мышки."""
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        self.history.append(HistoryRecord(
            x = event.x,
            y = event.y,
            color = self.color.code,
            type = self.fig_type,
            distance = self.distance_func_name,
            size = self.fig_size,
            time = self.time
        ))
        self.create_figure(event.x, event.y, x_size, y_size)

    def mousedown(self, _):
        u"""Очистка хвоста истории после undo (т.е. нельзя будет сделать его redo)."""
        while self.history and self.history[-1].time > self.time:
            self.history.pop()
        # счёт времени
        self.time += 1

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
        u"""Отмена отмены"""
        if self.history and self.history[-1].time > self.time:
            self.time += 1
        self.repaint()

    def save(self):
        u"""Сохранение картинки в файл"""
        filename = filedialog.asksaveasfilename(
            initialdir = ".",
            title = "Выберите файл",
            filetypes = (("kaleidoscope files", "*.kld"),)
        )
        if not filename:
            return
        if not filename.endswith('.kld'):
            filename += '.kld'
        try:
            with open(filename, "w") as f:
                for h in self.history:
                    f.write(
                        str(h.x) + " " +
                        str(h.y) + " " +
                        h.color + " " +
                        h.type + " " +
                        h.distance + " " +
                        str(h.size) + " " +
                        "\n")
        except BaseException:
            self.history = []
            messagebox.showerror(
                "Ошибка",
                "В процессе сохранения файла произошла ошибка")

    def load(self):
        u"""Загрузка картинки из файла"""
        filename = filedialog.askopenfilename(
            initialdir = ".",
            title = "Выберите файл",
            filetypes = (("kaleidoscope files", "*.kld"),)
        )
        if not filename:
            return
        if not filename.endswith('.kld'):
            filename += '.kld'
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
                        size = float(l[5]),
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
            self.fig_size = h.size
            self.set_style(h.type)
            self.set_scale_function(h.distance)
            x_size = self.winfo_width()
            y_size = self.winfo_height()
            self.create_figure(h.x, h.y, x_size, y_size)

    def set_style(self, string):
        u"""Сеттер стиля кисти"""
        self.fig_type = string

    def create_figure(self, coord_x, coord_y, x_size, y_size):
        u"""Метод, рисующий с отображением (x, y - координаты базовой фигуры)"""
        # переменные размеров окна

        x_center = coord_x - x_size/2
        y_center = coord_y - y_size/2

        # масштаб - в зависимости от расстояния до центра
        size = self.fig_size * self.distance_func(x_center, y_center, x_size, y_size)

        # переключение разных фигур с помощью self.fig_type
        if self.fig_type == 'triangle':
            create_poly = self.create_polygon

            def figure_function(x_1, y_1, x_2, y_2, **kwargs):
                # Треугольник, обращённый углом к центру
                from math import copysign
                x_0 = (x_1+x_2)/2
                radius_x = x_0 - x_size/2
                y_0 = (y_1+y_2)/2
                radius_y = y_0 - y_size/2
                rho = self.distance_func(radius_x, radius_y, x_size, y_size)
                dxs = rho * abs(x_2-x_1) / copysign(2, radius_x)
                dys = rho * abs(y_2-y_1) / copysign(2, radius_y)
                create_poly(
                    round(x_0 - dxs), round(y_0 - dys),
                    round(x_0 + dxs), round(y_0 - dys),
                    round(x_0 - dxs), round(y_0 + dys),
                    **kwargs)
        elif self.fig_type == 'circle':
            figure_function = self.create_oval
        elif self.fig_type == 'square':
            figure_function = self.create_rectangle
        else:
            messagebox.showerror(
                "Ошибка установки кисти.",
                "Внимание!\n\
Не удалось загрузить стиль кисти.\n\
Установлена круглая кисть.")
            figure_function = self.create_oval

        # координаты фигуры
        points = coord_x - size, coord_y - size, coord_x + size, coord_y + size
        self.figure_symmetry(figure_function, points, (x_size, y_size))

    def figure_symmetry(self, func, points, size):
        u"""Функция симметричного отображения относительно главных диагоналей."""
        # изменение цвета
        color = next(self.color)
        kwargs = {'fill' : color, 'width' : 0}

        #загрузка точек и размеров экрана
        x_1, y_1, x_2, y_2 = points
        x_size, y_size = size

        # коэффициенты растяжения относительно главных диагоналей
        x_coef = y_size / x_size
        y_coef = x_size / y_size

        # радиус-размерности
        rdx = (x_2 - x_1) / 2
        rdy = (y_2 - y_1) / 2

        # 8 фигур
        kwargs = {'fill': color, 'width': 0}
        func((y_1 + rdy) * y_coef - rdy, (x_1 + rdx) * x_coef - rdx,
             (y_2 - rdy) * y_coef + rdy, (x_2 - rdx) * x_coef + rdx, **kwargs)
        func((y_size - y_1 - rdy) * y_coef + rdy, (x_1 + rdx) * x_coef - rdx,
             (y_size - y_2 + rdy) * y_coef - rdy, (x_2 - rdx) * x_coef + rdx, **kwargs)
        func((y_1 + rdy) * y_coef - rdy, (x_size - x_1 - rdx) * x_coef + rdx,
             (y_2 - rdy) * y_coef + rdy, (x_size - x_2 + rdx) * x_coef - rdx, **kwargs)
        func((y_size - y_1 - rdy) * y_coef + rdy, (x_size - x_1 - rdx) * x_coef + rdx,
             (y_size - y_2 + rdy) * y_coef - rdy, (x_size - x_2 + rdx) * x_coef - rdx, **kwargs)
        func(x_1, y_1,
             x_2, y_2, **kwargs)
        func(-x_1 + x_size, -y_1 + y_size,
             -x_2 + x_size, -y_2 + y_size, **kwargs)
        func(x_1, -y_1 + y_size,
             x_2, -y_2 + y_size, **kwargs)
        func(-x_1 + x_size, y_1,
             -x_2 + x_size, y_2, **kwargs)

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
        from math import sqrt
        fig_min_size = 0.5
        fig_div_size = 3
        if string == 'manhatten':
            def func(x_center, y_center, x_size, y_size):
                rho = (abs(x_center) + abs(y_center))*START_FIGURE_SIZE
                rho = rho / fig_div_size
                screen_factor = x_size + y_size
                return rho / screen_factor + fig_min_size
        elif string == 'square_dist':
            def func(x_center, y_center, x_size, y_size):
                rho = x_center*x_center + y_center*y_center
                rho = rho / fig_div_size
                screen_factor = x_size * y_size
                return rho / screen_factor * START_FIGURE_SIZE + fig_min_size
        elif string == 'inv_Chebushev':
            def func(x_center, y_center, x_size, y_size):
                coef = START_FIGURE_SIZE
                rho = min(abs(x_center), abs(y_center)) + coef*coef
                rho = rho * fig_div_size
                screen_factor = sqrt(x_size * y_size)  + fig_min_size
                return screen_factor / rho
        elif string == "inverse_dist":
            def func(x_center, y_center, x_size, y_size):
                rho = x_center*x_center + y_center*y_center
                rho = sqrt(rho * fig_div_size * fig_div_size)
                screen_factor = x_size * y_size
                return 1 / (rho / sqrt(screen_factor) + 0.15) + fig_min_size
        else:
            def func(*_):
                return 1.0
        self.distance_func_name = string
        self.distance_func = func

    def save_to_png(self):
        u"""Сохраненить в файл как картинку, к сожалению нету адекватного способа заставить работать на linux"""
        filename = filedialog.asksaveasfilename(
            initialdir = ".",
            title = "Выберите файл",
            filetypes = (("png file", "*.png"),)
        )
        if not filename:
            return
        try:
            if platform in ("linux", "linux2"):
                import pyscreenshot as ImageGrab
            else:
                from PIL import ImageGrab
            # with open(filename, "w") as f:
            time.sleep(0.5)
            img = ImageGrab.grab((self.winfo_rootx(), self.winfo_rooty(), self.winfo_rootx() + \
                self.winfo_width(), self.winfo_rooty() + self.winfo_height()))
            img.save("11.png")

        except ImportError:
            messagebox.showerror(
                "Ошибка",
                "Установите Pillow или pyscreenshot(такая библиотека)")



        except BaseException:
            self.history = []
            messagebox.showerror(
                "Ошибка",
                "В процессе сохранения файла произошла ошибка")
