from tkinter import *
import random
from math import sqrt

# стартовый цвет
start_R, start_G, start_B = 150, 150, 150
start_figure_size = 10
canv_size = 700

class Color():
    u"""Класс, обеспечивающий хранение цвета,
и выбор случайного цвета на основе текущего"""

    def __init__(self, r=start_R, g=start_G, b=start_B):
        u"""Инициализация серым цветом"""
        self.r = r
        self.g = g
        self.b = b
        self.code = '#' + '%0.2X' % self.r + '%0.2X' % self.g + '%0.2X' % self.b
        self.palette = []
        self.color_dif = 10

    def decode(self):
        self.r = int(self.code[1:3], 16)
        self.g = int(self.code[3:5], 16)
        self.b = int(self.code[5:7], 16)

    def __iter__(self):
        return self

    def __next__(self):
        u"""Получить следующий цвет."""
        if self.palette:
            self.code = next(self.palette)
        else:
            self.r = self.mutate(self.r)
            self.g = self.mutate(self.g)
            self.b = self.mutate(self.b)
            self.code = '#' + '%0.2X' % self.r + '%0.2X' % self.g + '%0.2X' % self.b
        return self.code

    def mutate(self, component):
        u"""Изменение одной компоненты цвета."""
        result = random.randrange(-self.color_dif, self.color_dif) + component
        if result > 255:
            result = 512 - result
        elif result <= 0:
            result = 50
        return result



class Paint(Canvas):
    """Класс виджета для рисования"""
    def __init__(self, master=None, *ap, **an):
        Canvas.__init__(self, master, *ap, **an)
        self.fig_type = "circle"
        # None в color_pick означает, что будет выбираться автоматически
        self.color_pick = None
        # стартовый цвет
        self.color = Color()
        self.bind("<B1-Motion>", self.mousemove)
        self.define_pallete(self.color)

    def mousemove(self, event):
        """Обработка события движения мышки"""
        self.create_figure(int(event.x), int(event.y))

    def set_style(self, string):
        u"""Сеттер стиля кисти"""
        self.fig_type = string

    def create_figure(self, coordX, coordY):
        u"""Метод, рисующий с отображением (x, y - координаты базовой фигуры)"""
        # переменные размеров окна
        x_size = self.winfo_width()
        y_size = self.winfo_height()

        # изменение цвета
        color = next(self.color)
        x_center = coordX - x_size/2
        y_center = coordY - y_size/2
        # масштаб - в зависимости от расстояния до центра
        size = start_figure_size / ((
            sqrt(x_center*x_center + y_center*y_center)
            / sqrt(x_size*y_size)) + 0.15)

        # переключение разных фигур с помощью self.fig_type
        if self.fig_type == 'triangle':
            create_poly = self.create_polygon
            def figure_function(x1, y1, x2, y2, **kwargs):
                # Треугольник, обращённый углом к центру
                x0 = (x1+x2)/2
                rx = x0-x_size/2
                y0 = (y1+y2)/2
                ry = y0-y_size/2
                diameter = abs(x2-x1)/2
                dx = rx/(sqrt(rx*rx)+0.001) * diameter
                dy = ry/(sqrt(ry*ry)+0.001) * diameter
                create_poly(
                    round(x0 - dx), round(y0 - dy),
                    round(x0 + dx), round(y0 - dy),
                    round(x0 - dx), round(y0 + dy),
                    **kwargs)
        elif self.fig_type == 'circle':
            figure_function = self.create_oval
        elif self.fig_type == 'square':
            figure_function = self.create_rectangle
        else:
            print('Warning')
            return None

        # координаты фигуры
        point1 = coordX - size, coordY - size
        point2 = coordX + size, coordY + size

        self.figure_symmetry(figure_function, point1, point2, color)
        return None

    def figure_symmetry(self, func, point1, point2, color):
        u"""Функция симметричного отображения относительно главных диагоналей."""
        # коэффициенты растяжения для отображения относительно диагоналей
        y1, x1 = point1
        y2, x2 = point2
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        x_k = y_size / x_size
        y_k = x_size / y_size

        # 8 кругов
        kwargs = {'fill':color, 'width':0}
        for A1, A3 in [(x1, x2), (x_size - x1, x_size-x2)]:
            for B2, B4 in [(y_size-y1, y_size-y2), (y1, y2)]:
                func(round(A1), round(B2), round(A3), round(B4), **kwargs)
        for A1, A3 in [(y1 * y_k, y2 * y_k), ((y_size-y1) * y_k, (y_size-y2) * y_k)]:
            for B2, B4 in [(x1 * x_k, x2 * x_k), ((x_size-x1) * x_k, (x_size-x2) * x_k)]:
                func(round(A1), round(B2), round(A3), round(B4), **kwargs)

    def define_pallete(self, index=0):
        """Определение палитры, если возможно, её загрузка из файла"""
        from os.path import isfile
        from itertools import zip_longest, cycle
        if isfile(f"./palette{str(index)}.txt"):
            palette = []
            with open(f"./palette{str(index)}.txt") as palette_text:
                for line in palette_text:
                    palette.extend(
                        ['#'+''.join(hex_code)
                         for hex_code
                         in zip_longest(*[iter(line)] * 6)
                        ])
            self.color.palette = cycle(palette)
        else:
            if self.color.palette:
                self.color.decode()
            self.color.palette = []



class App(Tk):
    u"""Главный класс приложения."""

    def __init__(self):
        u"""Создание холста и запуск цикла отрисовки"""
        super(App, self).__init__()
        self.geometry('{}x{}'.format(canv_size, canv_size))
        self.title('Калейдоскоп')
        # создаем сам холст и помещаем его в окно
        self.canv = Paint(self, bg='white')
        self.canv.grid(row = 0, column = 0, sticky = "wens")
        # чтобы занимал все окно
        self.columnconfigure(index = 0, weight = 1)
        self.rowconfigure(index = 0, weight = 1)

        # добавляем главное меню
        main_menu = Menu(self)


        #меню выбора фигуры
        brush_style = Menu(main_menu)
        brush_style.add_command(label="Кружок",
                                command=lambda: self.canv.set_style("circle"))
        brush_style.add_command(label="Квадрат",
                                command=lambda: self.canv.set_style("square"))
        brush_style.add_command(label="Треугольник",
                                command=lambda: self.canv.set_style("triangle"))

        #меню выбора цвета
        palette_choice = Menu(main_menu)
        palette_choice.add_command(label="Случайная палитра",
                                   command=lambda: self.canv.define_pallete(0))
        palette_choice.add_command(label="Сине-белая палитра",
                                   command=lambda: self.canv.define_pallete(1))
        palette_choice.add_command(label="Палитра 2",
                                   command=lambda: self.canv.define_pallete(2))
        palette_choice.add_command(label="Палитра 3",
                                   command=lambda: self.canv.define_pallete(3))

        #добавляем кнопку очистки холста и панели выбора
        main_menu.add_command(label="Очистить", command = lambda: self.canv.delete("all"))
        main_menu.add_cascade(label="Стиль кисти", menu=brush_style)
        main_menu.add_cascade(label="Палитра", menu=palette_choice)
        self.config(menu = main_menu)

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x, y))

        self.mainloop()


if __name__ == '__main__':
    app = App()
