from tkinter import *
import random
from math import sqrt
from tkinter import filedialog

# стартовый цвет
start_R, start_G, start_B = 150, 150, 150
start_figure_size = 10
canv_size = 700


class Color():
    u"""Класс, обеспечивающий хранение цвета,
и выбор случайного цвета на основе текущего."""

    def __init__(self, r=start_R, g=start_G, b=start_B):
        u"""Инициализация серым цветом."""
        self.r = r
        self.g = g
        self.b = b
        self.code = '#' + '%0.2X' % self.r + '%0.2X' % self.g + '%0.2X' % self.b
        self.palette = []
        self.color_dif = 10
        self.random_color = 1

    def decode(self):
        u"""Декодирование последнего цвета из hex в RGB."""
        self.r = int(self.code[1:3], 16)
        self.g = int(self.code[3:5], 16)
        self.b = int(self.code[5:7], 16)

    def __iter__(self):
        return self

    def __next__(self):
        u"""Получить следующий цвет."""
        res = self.code
        if self.palette:
            self.code = next(self.palette)
        else:
            if self.random_color == -1:
                self.r = self.randomize(self.r)
                self.g = self.randomize(self.g)
                self.b = self.randomize(self.b)
            elif self.random_color == -2:
                self.r = self.mutate(self.r)
                self.g = self.mutate(self.g)
                self.b = self.mutate(self.b)
            self.code = '#' + '%0.2X' % self.r + '%0.2X' % self.g + '%0.2X' % self.b
        return res

    def mutate(self, component):
        u"""Плавное изменение одной компоненты цвета."""
        result = random.randrange(-self.color_dif, self.color_dif) + component
        if result > 255:
            result = 511 - result
        elif result <= 50:
            result = 50
        return result

    def randomize(self, component):
        u"""Получить следующий рандомный цвет"""
        result = (random.randrange(-self.color_dif, self.color_dif) + component) % 206 + 50
        return result


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
    """Класс виджета для рисования."""

    def __init__(self, master=None, *ap, **an):
        Canvas.__init__(self, master, *ap, **an)
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
        # очистка хвоста истории после undo (т.е. нельзя будет сделать его redo)
        while self.history and self.history[-1].time > self.time:
            self.history.pop()
        # счёт времени
        self.time += 1

    def mouseup(self, event):
        pass

    def cleanup(self):
        self.history = []
        self.time = 0
        self.delete("all")

    def undo(self):
        if self.time > 0:
            self.time -= 1
        self.repaint()

    def redo(self):
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
        with open(filename, "w") as f:
            for h in self.history:
                f.write(
                    str(h.x) + " " +
                    str(h.y) + " " +
                    h.color + " " +
                    h.type + " " +
                    h.distance + " " +
                    "\n")

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
        with open(filename, "r") as f:
            self.history = []
            self.time = 1
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
        size = start_figure_size * self.distance_func(x_center, y_center)

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
            from os.path import isfile
            from tkinter import messagebox
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



class App(Tk):
    u"""Главный класс приложения."""

    def __init__(self):
        u"""Создание холста и запуск цикла отрисовки"""
        super(App, self).__init__()
        self.geometry('{}x{}'.format(canv_size, canv_size))
        self.title('Калейдоскоп')
        # создаем сам холст и помещаем его в окно
        self.canv = Paint(self, bg='white')
        self.canv.grid(row=0, column=0, sticky='wens')
        # чтобы занимал все окно
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

        # добавляем главное меню
        main_menu = Menu(self)

        # меню выбора фигуры
        brush_style = Menu(main_menu)
        brush_style.add_command(label='Кружок',
                                command=lambda: self.canv.set_style('circle'))
        brush_style.add_command(label='Квадрат',
                                command=lambda: self.canv.set_style('square'))
        brush_style.add_command(label='Треугольник',
                                command=lambda: self.canv.set_style('triangle'))

        # меню выбора цвета
        palette_choice = Menu(main_menu)
        palette_choice.add_command(label='Случайная палитра',
                                   command=lambda: self.canv.define_pallete(-1))
        palette_choice.add_command(label='Плавная случайная палитра',
                                   command=lambda: self.canv.define_pallete(-2))
        palette_choice.add_command(label='Палитра 1',
                                   command=lambda: self.canv.define_pallete(1))
        palette_choice.add_command(label='Палитра 2',
                                   command=lambda: self.canv.define_pallete(2))
        palette_choice.add_command(label='Палитра 3',
                                   command=lambda: self.canv.define_pallete(5))

        # меню выбора масштабирования
        scale_choice = Menu(main_menu)
        scale_choice.add_command(
            label='Константа',
            command=lambda: self.canv.set_scale_function('const'))
        scale_choice.add_command(
            label='Обратное расстояние до центра',
            command=lambda: self.canv.set_scale_function('inverse_dist'))
        scale_choice.add_command(
            label='Манхэттенское расстояние до центра',
            command=lambda: self.canv.set_scale_function('manhatten'))
        scale_choice.add_command(
            label='Квадрат расстояния до центра',
            command=lambda: self.canv.set_scale_function('square_dist'))
        scale_choice.add_command(
            label='Масштабирование, обратное Манхэттенскому',
            command=lambda: self.canv.set_scale_function('inv_Chebushev'))

        # меню работы с файлами
        file_menu = Menu(main_menu)
        file_menu.add_command(
            label='Загрузить...',
            command=self.canv.load)
        file_menu.add_command(
            label='Сохранить...',
            command=self.canv.save)

        # добавляем кнопку очистки холста и панели выбора
        main_menu.add_cascade(label='Файл', menu=file_menu)
        main_menu.add_command(label='Очистить', command=self.canv.cleanup)
        main_menu.add_command(label='Отменить', command=self.canv.undo)
        main_menu.add_command(label='Повторить', command=self.canv.redo)
        main_menu.add_cascade(label='Стиль кисти', menu=brush_style)
        main_menu.add_cascade(label='Масштабирование', menu=scale_choice)
        main_menu.add_cascade(label='Палитра', menu=palette_choice)
        self.config(menu=main_menu)

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x, y))

        self.mainloop()


if __name__ == '__main__':
    app = App()
