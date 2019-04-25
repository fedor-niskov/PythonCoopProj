u"""Основной модуль рисования на холсте, сохранения и загрузки истории"""

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
        # число симметрии
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
        self.color.define_palette(-1)
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
            omega = 2 * pi / num
        elif self.num_symm < 0:
            num = - self.num_symm
            omega = 2 * pi / num
        else:
            num = 0
        cos_coef = [cos(omega * i) for i in range(num)]
        sin_ycoef = [sin(omega * i) * y_coef for i in range(num)]
        sin_xcoef = [sin(omega * i) * x_coef for i in range(num)]
        self.coefficients = cos_coef, sin_ycoef, sin_xcoef

    def mousemove(self, event):
        u"""Обработка события движения мышки."""
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        self.history.append(HistoryRecord(
            x=event.x / x_size,
            y=event.y / y_size,
            color=self.color.code,
            type=self.fig_type,
            distance=self.distance_func_name,
            size=self.fig_size,
            time=self.time,
            snum=self.num_symm
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
            initialdir=".",
            title=Dict['save_file_dialog_title'],
            filetypes=(("kaleidoscope files", "*.kld"),)
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
                Dict['save_file_error_title'],
                Dict['save_file_error'])

    def load(self):
        u"""Загрузка картинки из файла"""
        filename = filedialog.askopenfilename(
            initialdir=".",
            title=Dict['load_file_dialog_title'],
            filetypes=(("kaleidoscope files", "*.kld"),)
        )
        if not filename:
            return
        if not filename.endswith('.kld'):
            filename += '.kld'
        self.history = []
        self.time = 1
        try:
            with open(filename, "r") as f:
                for line in f.readlines():
                    line = line.split()
                    self.history.append(HistoryRecord(
                        x=float(line[0]),
                        y=float(line[1]),
                        color=line[2],
                        type=line[3],
                        distance=line[4],
                        size=float(line[5]),
                        time=1,
                        snum=int(line[6])
                    ))
        except BaseException:
            self.history = []
            messagebox.showerror(
                Dict['load_file_error_title'],
                Dict['load_file_error'])
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
            if h.snum != self.num_symm:
                self.num_symm = h.snum
                self.recalculate_coefficients()
            self.num_symm = h.snum
            self.set_scale_function(h.distance)
            self.create_figure(h.x * x_size, h.y * y_size, x_size, y_size)
        self.color.decode()

    def set_style(self, string):
        u"""Сеттер стиля кисти"""
        self.fig_type = string

    def create_figure(self, coord_x, coord_y, x_size, y_size):
        u"""Метод, рисующий с отображением (x, y - координаты базовой фигуры)"""
        # переменные размеров окна
        x_half_size, y_half_size = x_size / 2, y_size / 2
        x_center = coord_x - x_half_size
        y_center = coord_y - y_half_size

        # масштаб - в зависимости от расстояния до центра
        size = self.fig_size * self.distance_func(x_center, y_center, x_size, y_size)

        # переключение разных фигур с помощью self.fig_type
        if self.fig_type == 'triangle':
            create_poly = self.create_polygon

            def figure_function(x_center, y_center, size, **kwargs):
                # Треугольник, обращённый углом к центру
                x_half_size, y_half_size, delta = size
                from math import copysign
                x_0 = x_half_size + x_center
                y_0 = y_half_size + y_center
                # дельты размеров треугольника
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
            def figure_function(x_center, y_center, size, **kwargs):
                x_half_size, y_half_size, delta = size
                x_base, y_base = x_half_size + x_center, y_half_size + y_center
                self.create_oval(
                    x_base - delta, y_base - delta,
                    x_base + delta, y_base + delta,
                    **kwargs)
            messagebox.showerror(
                Dict['brush_error_title'],
                Dict['brush_error'])
        # фигур симметричное отражение, от координат центра отсчитанное
        self.figure_symmetry(
            figure_function,
            (x_center, y_center),
            (x_half_size, y_half_size, size),
            self.num_symm)

    def figure_symmetry(self, func, base_point, size, num):
        u"""Функция симметричного отображения относительно главных диагоналей."""
        # изменение цвета, заполнение цвета, канва фигуры
        kwargs = {'fill': next(self.color), 'width': 0}

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
                func(x_center * cos_coef[i] + y_center * sin_ycoef[i],
                     y_center * cos_coef[i] - x_center * sin_xcoef[i],
                     size, **kwargs)
        elif num % 2 == 0:
            # num*2 фигур, симметричное отражение
            for i in range(0, num // 2):
                x_base_cos, x_base_sin = x_center * cos_coef[i], x_center * sin_xcoef[i]
                y_base_cos, y_base_sin = y_center * cos_coef[i], y_center * sin_ycoef[i]
                func(x_base_cos + y_base_sin,
                     y_base_cos - x_base_sin,
                     size, **kwargs)
                func(y_base_sin - x_base_cos,
                     x_base_sin + y_base_cos,
                     size, **kwargs)
        else:
            self.num_symm = 0
            messagebox.showerror(
                Dict['symm_error_title'],
                Dict['symm_error'])

    def set_scale_function(self, string=''):
        u"""Выбор масштабирущей функции"""
        from math import sqrt
        fig_min_size = 0.5
        fig_div_size = 3
        if string == 'manhatten':
            def func(x_center, y_center, x_size, y_size):
                rho = (abs(x_center) + abs(y_center)) * START_FIGURE_SIZE
                rho = rho / fig_div_size
                screen_factor = x_size + y_size
                return rho / screen_factor + fig_min_size
        elif string == 'square_dist':
            def func(x_center, y_center, x_size, y_size):
                rho = x_center * x_center + y_center * y_center
                rho = rho / fig_div_size
                screen_factor = x_size * y_size
                return rho / screen_factor * START_FIGURE_SIZE + fig_min_size
        elif string == 'inv_Chebushev':
            def func(x_center, y_center, x_size, y_size):
                coef = START_FIGURE_SIZE
                rho = min(abs(x_center), abs(y_center)) + coef * coef
                rho = rho * fig_div_size
                screen_factor = sqrt(x_size * y_size) + fig_min_size
                return screen_factor / rho
        elif string == "inverse_dist":
            def func(x_center, y_center, x_size, y_size):
                rho = x_center * x_center + y_center * y_center
                rho = sqrt(rho * fig_div_size * fig_div_size)
                screen_factor = x_size * y_size
                return 1 / (rho / sqrt(screen_factor) + 0.15) + fig_min_size
        elif string == "constant":
            def func(*_):
                return 1.0
        else:
            def func(*_):
                return 1.0
            messagebox.showerror(
                Dict['scale_error_title'],
                Dict['scale_error'])
        self.distance_func_name = string
        self.distance_func = func

    def paint_function(self, func, steps):
        u"""Функция отрисовки параметрической функции
        func: (float, int, int) -> (float, float)
        func(t, x, y), где t in [0,1)
        с шагом дискретизации 1/steps"""
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        for time in range(0, steps):
            x_coord, y_coord = func(time / steps, x_size, y_size)
            self.history.append(HistoryRecord(
                x=x_coord / x_size,
                y=y_coord / y_size,
                color=self.color.code,
                type=self.fig_type,
                distance=self.distance_func_name,
                size=self.fig_size,
                time=self.time,
                snum=self.num_symm
            ))
            self.create_figure(x_coord, y_coord, x_size, y_size)

    def heart(self, index=0):
        """Сердечко <3
        Обычная кардиоида, в двух вариантах исполнения"""
        from math import sin, cos, pi, sqrt
        if index == 2:
            def func1(time, x_size, y_size):
                x_coord = 16. * sin(time * pi * 2.) ** 3
                y_coord = -13. * cos(time * pi * 2.) + 5. * cos(4. * pi * time) +\
                    2. * cos(6. * pi * time) + cos(8. * pi * time)
                return x_coord * x_size / 128 + x_size / 2, y_coord * y_size / 128 + y_size / 4
            self.color.define_palette(-2 - index)
            self.paint_function(func1, 1000)
        if index == 1:
            def func2(time, x_size, y_size):
                x_coord = cos(time * pi * 2.)
                y_coord = -sin(time * pi * 2.) - sqrt(abs(x_coord))
                return x_coord * x_size / 7 + x_size / 2, y_coord * y_size / 8 + y_size / 4
            self.color.define_palette(-2 - index)
            self.paint_function(func2, 1000)

    def save_to_png(self):
        u"""Сохранить в файл как картинку, к сожалению
        нету адекватного способа заставить работать на linux"""
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title=Dict['save_pic_dialog_title'],
            filetypes=(("png file", "*.png"),)
        )
        if not filename:
            return
        try:
            if platform in ("linux", "linux2"):
                import pyscreenshot as ImageGrab
            else:
                from PIL import ImageGrab
            img = ImageGrab.grab((
                self.winfo_rootx(),
                self.winfo_rooty(),
                self.winfo_rootx() + self.winfo_width(),
                self.winfo_rooty() + self.winfo_height()))
            img.save(filename)

        except ImportError:
            messagebox.showerror(
                Dict['save_pic_import_error_title'],
                Dict['save_pic_import_error'])

        except BaseException:
            self.history = []
            messagebox.showerror(
                Dict['save_pic_error_title'],
                Dict['save_pic_error'])
