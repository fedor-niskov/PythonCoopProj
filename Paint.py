"""
Основной модуль рисования на холсте, сохранения и загрузки истории
"""

from os.path import isfile
from sys import platform
from tkinter import Canvas, messagebox, filedialog
from Color import Color

START_FIGURE_SIZE = 10
_DEBUG = True

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
        #число симметрии
        self.snum = param["snum"]


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
            константная функция масштаба;
            8 симметричных отображений"""
        Canvas.__init__(self, master, *ap, **an)
        self.fig_size = START_FIGURE_SIZE
        self.fig_type = 'circle'
        # None в color_pick означает, что будет выбираться автоматически
        self.color_pick = None
        # стартовый цвет
        self.color = Color()
        # привязки функций-обработчиков
        self.binding_functions()
        # загрузка палитры
        self.define_pallete(-1)
        # выбор функции масштаба
        self.set_scale_function("constant")
        # число симметричных отображений
        self.num_symm = 16
        # история - список из HistoryRecord
        self.history = []
        # время (каждый клик мышкой увеличивает время на 1)
        self.time = 0
        self.recalculate_coefficients()

    def binding_functions(self):
        u"""Привязка функций-обработчиков:
            нажатия и перемещения мыши - рисование,
            изменения конфигурации - перерисовка изображения,
            отладочная привязка перемещения по холсту на пр. кн. мыши"""
        self.bind('<B1-Motion>', self.mousemove)
        self.bind('<Button-1>', self.mousedown)
        self.bind('<Configure>', lambda event: self.repaint())
        if _DEBUG:
            self.bind("<ButtonPress-3>", self.scroll_start)
            self.bind("<B3-Motion>", self.scroll_move)

    def recalculate_coefficients(self):
        u"""Перерасчёт коэффициентов отражения"""
        from math import sin, cos, pi
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        x_coef = y_size / x_size
        y_coef = x_size / y_size
        if self.num_symm > 0:
            num = self.num_symm // 2
            omega = 2*pi/num
        elif self.num_symm < 0:
            num = - self.num_symm
            omega = 2*pi/num
        else:
            num = 0
        cos_coef = [cos(omega*i) for i in range(num)]
        sin_ycoef = [sin(omega*i)*y_coef for i in range(num)]
        sin_xcoef = [sin(omega*i)*x_coef for i in range(num)]
        self.coefficients = cos_coef, sin_ycoef, sin_xcoef

    def mousemove(self, event):
        u"""Обработка события движения мышки."""
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        self.history.append(HistoryRecord(
            x=event.x/x_size,
            y=event.y/y_size,
            color=self.color.code,
            type = self.fig_type,
            distance = self.distance_func_name,
            size = self.fig_size,
            time = self.time,
            snum = self.num_symm
        ))
        self.create_figure(event.x, event.y, x_size, y_size)

    def mousedown(self, _):
        u"""Очистка хвоста истории после undo (т.е. нельзя будет сделать его redo)."""
        while self.history and self.history[-1].time > self.time:
            self.history.pop()
        # счёт времени
        self.time += 1

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

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
                        str(h.snum) + " " +
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
                        time = 1,
                        snum = int(l[6])
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
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        self.num_symm = 8
        self.recalculate_coefficients()
        for h in self.history:
            if h.time > self.time:
                continue
            self.color.code = h.color
            self.fig_size = h.size
            self.set_style(h.type)
            self.num_symm = h.snum
            if h.snum != self.num_symm:
                self.recalculate_coefficients()
            self.set_scale_function(h.distance)
            self.create_figure(h.x*x_size, h.y*y_size, x_size, y_size)
        self.color.decode()

    def set_style(self, string):
        u"""Сеттер стиля кисти"""
        self.fig_type = string

    def create_figure(self, coord_x, coord_y, x_size, y_size):
        u"""Метод, рисующий с отображением (x, y - координаты базовой фигуры)"""
        # переменные размеров окна
        x_half_size, y_half_size = x_size/2, y_size/2
        x_center = coord_x - x_half_size
        y_center = coord_y - y_half_size

        # масштаб - в зависимости от расстояния до центра
        size = self.fig_size * self.distance_func(x_center, y_center, x_size, y_size)

        # переключение разных фигур с помощью self.fig_type
        if self.fig_type == 'triangle':
            create_poly = self.create_polygon

            def figure_function(x_center, y_center, size, **kwargs):
                x_half_size, y_half_size, delta = size
                # Треугольник, обращённый углом к центру
                from math import copysign
                x_0 = x_half_size + x_center
                y_0 = y_half_size + y_center
                dxs = copysign(delta, x_center)
                dys = copysign(delta, y_center)
                create_poly(
                    round(x_0 - dxs), round(y_0 - dys),
                    round(x_0 + dxs), round(y_0 - dys),
                    round(x_0 - dxs), round(y_0 + dys),
                    **kwargs)
        elif self.fig_type == 'circle':
            def figure_function(x_center, y_center, size, **kwargs):
                x_half_size, y_half_size, delta = size
                x_base, y_base = x_half_size + x_center, y_half_size + y_center
                self.create_oval(
                    x_base - delta, y_base - delta,
                    x_base + delta, y_base + delta,
                    **kwargs)
        elif self.fig_type == 'square':
            def figure_function(x_center, y_center, size, **kwargs):
                x_half_size, y_half_size, delta = size
                x_base, y_base = x_half_size + x_center, y_half_size + y_center
                self.create_rectangle(
                    x_base - delta, y_base - delta,
                    x_base + delta, y_base + delta,
                    **kwargs)
        else:
            messagebox.showerror(
                "Ошибка установки кисти.",
                "Внимание!\n\
Не удалось загрузить стиль кисти.\n\
Установлена круглая кисть.")
            def figure_function(x_center, y_center, size, **kwargs):
                x_half_size, y_half_size, delta = size
                x_base, y_base = x_half_size + x_center, y_half_size + y_center
                self.create_oval(
                    x_base - delta, y_base - delta,
                    x_base + delta, y_base + delta,
                    **kwargs)
        # координаты фигуры
        self.figure_symmetry(
            figure_function,
            (x_center, y_center),
            (x_half_size, y_half_size, size),
            self.num_symm)

    def figure_symmetry(self, func, base_point, size, num):
        u"""Функция симметричного отображения относительно главных диагоналей."""
        # изменение цвета, заполнение цвета, канва фигуры
        kwargs = {'fill' : next(self.color), 'width' : 0}

        # загрузка точек и размеров экрана
        x_center, y_center = base_point
        # загрузка коэффициентов отражений
        cos_coef, sin_ycoef, sin_xcoef = self.coefficients

        # в зависимости от числа симметрий - разное число фигур
        if num == 0:
            # только кисть, без отражений
            func(x_center, y_center, size, **kwargs)
        elif num < 0:
            # num фигур, простой поворот
            for i in range(0, -num):
                func(x_center*cos_coef[i] + y_center*sin_ycoef[i],
                     y_center*cos_coef[i] - x_center*sin_xcoef[i],
                     size, **kwargs)
        elif num % 2 == 0:
            # num*2 фигур, симметричное отражение
            for i in range(0, num//2):
                x_base_cos, x_base_sin = x_center*cos_coef[i], x_center*sin_xcoef[i]
                y_base_cos, y_base_sin = y_center*cos_coef[i], y_center*sin_ycoef[i]
                func(x_base_cos + y_base_sin,
                     y_base_cos - x_base_sin,
                     size, **kwargs)
                func(y_base_sin - x_base_cos,
                     x_base_sin + y_base_cos,
                     size, **kwargs)
        else:
            self.num_symm = 0
            messagebox.showerror(
                "Исключительная функция симметрии",
                "Внимание!\n\
Не удалось установить заданное симметричное отражение.\n\
Установлена простая (одна) кисть.\n\
Пожалуйста, задайте иное число симметрий.")

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
        elif string == "constant":
            def func(*_):
                return 1.0
        else:
            messagebox.showerror(
                "Ошибка установки функции масштабирования.",
                "Внимание!\n\
Не удалось распознать функцию масштабирования.\n\
Установлена константная функция.")
            def func(*_):
                return 1.0
        self.distance_func_name = string
        self.distance_func = func

    def save_to_png(self):
        u"""Сохранить в файл как картинку, к сожалению
        нету адекватного способа заставить работать на linux"""
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
            img = ImageGrab.grab(
                self.winfo_rootx(),
                self.winfo_rooty(),
                self.winfo_rootx() + self.winfo_width(),
                self.winfo_rooty() + self.winfo_height())
            img.save(filename)

        except ImportError:
            messagebox.showerror(
                "Ошибка",
                "Установите Pillow или pyscreenshot(такая библиотека)")

        except BaseException:
            self.history = []
            messagebox.showerror(
                "Ошибка",
                "В процессе сохранения файла произошла ошибка")
