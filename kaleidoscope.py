from tkinter import *
import random
from math import sqrt

# стартовый цвет
r, g, b = 150, 150, 150
start_figure_size = 10
canv_size = 700


class Color():
    u"""Класс, обеспечивающий хранение цвета,
и выбор случайного цвета на основе текущего"""

    def __init__(self, r=150, g=150, b=150):
        u"""Инициализация серым цветом"""
        self.r = r
        self.g = g
        self.b = b
        self.color_dif = 30

    def randomize(self):
        u"""Получить следующий рандомный цвет."""
        self.r = mutate(self.color_dif, self.r)
        self.g = mutate(self.color_dif, self.g)
        self.b = mutate(self.color_dif, self.b)
        return self

    def get_code(self):
        u"""Конвертация в формат, удобный для tkinter canvas."""
        res = '#' + '%0.2X' % self.r + '%0.2X' % self.g + '%0.2X' % self.b
        return res



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

    def mousemove(self, event):
        """Обработка события движения мышки"""
        self.create_figure(int(event.x), int(event.y))

    def create_figure(self, x, y):
        """Метод, рисующий с отображением (x, y - координаты базовой фигуры)"""
        # тут можно реализовать переключение разных фигур с помощью self.fig_type

        # изначальные координаты кружка
        x1 = x - circle_size
        x2 = x + circle_size
        y1 = y - circle_size
        y2 = y + circle_size

        x_s = self.winfo_width()
        y_s = self.winfo_height()
        color = self.color.get_code()
        self.color.randomize()

        # коэффициенты растяжения для отображения относительно диагоналей
        x_k = y_s / x_s
        y_k = x_s / y_s

        # 8 кругов
        self.create_oval(int(y1 * y_k), int(x1 * x_k), int(y2 * y_k), int(x2 * x_k), \
            fill = color, width = 0)
        self.create_oval(int((-y1 + y_s) * y_k), int(x1 * x_k), int((-y2 + y_s) * y_k), \
            int(x2 * x_k), fill = color, width = 0)
        self.create_oval(int(y1 * y_k), int((-x1 + x_s) * x_k), int(y2 * y_k), \
            int((-x2 + x_s) * x_k), fill = color, width = 0)
        self.create_oval(int((-y1 + y_s) * y_k), int((-x1 + x_s) * x_k), \
            int((-y2 + y_s) * y_k), int((-x2 + x_s) * x_k), fill = color, width = 0)
        self.create_oval(x1, y1, x2, y2, fill = color, width = 0)
        self.create_oval(-x1 + x_s, -y1 + y_s, -x2 + x_s, -y2 + y_s, fill = color, width = 0)
        self.create_oval(x1, -y1 + y_s, x2, -y2 + y_s, fill = color, width = 0)
        self.create_oval(-x1 + x_s, y1, -x2 + x_s, y2, fill = color, width = 0)


def mutate(dif, component):
    u"""Изменение одной компоненты цвета."""
    return (random.randrange(-dif, dif) + component) % 206 + 50


def _figure_symmetry(func, y1, x1, y2, x2, w, h, color):
    u"""Функция симметричного отображения относительно главных диагоналей."""
    # коэффициенты растяжения для отображения относительно диагоналей
    x_k = h / w
    y_k = w / h

    # 8 кругов
    for A1, A3 in [
            (x1, x2),
            (w - x1, w-x2)
    ]:
        for B2, B4 in [
                (h-y1, h-y2),
                (y1, y2)
        ]:
            func(
                round(A1), round(B2),
                round(A3), round(B4),
                fill=color, width=0)
    for A1, A3 in [
            (y1 * y_k, y2 * y_k),
            ((h-y1) * y_k, (h-y2) * y_k)
    ]:
        for B2, B4 in [
                (x1 * x_k, x2 * x_k),
                ((w-x1) * x_k, (w-x2) * x_k)
        ]:
            func(
                round(A1), round(B2),
                round(A3), round(B4),
                fill=color, width=0)



class App(Tk):
    u"""Главный класс приложения."""

    def __init__(self):
        u"""Создание холста и запуск цикла отрисовки"""
        super(App, self).__init__()
        self.geometry('{}x{}'.format(canv_size, canv_size))
        self.title('Калейдоскоп')
        # создаем сам холст и помещаем его в окно
# <<<<<<< oop_refactoring
        self.canv = Paint(self, bg='white')
        self.canv.grid(row = 0, column = 0, sticky = "wens")
        # чтобы занимал все окно
        self.columnconfigure(index = 0, weight = 1)
        self.rowconfigure(index = 0, weight = 1)
        
# =======
#         self.canv = Canvas(self, bg='white')
#         self.canv.grid(row=0, column=0, sticky='wens')
#         # чтобы занимал все окно
#         self.columnconfigure(index=0, weight=1)
#         self.rowconfigure(index=0, weight=1)
#         self.bind('<B1-Motion>', self.create_figure)

# >>>>>>> master
        # добавляем меню с кнопкой очистки холста
        main_menu = Menu(self)
        main_menu.add_command(label="Очистить", command = lambda: self.canv.delete("all"))
        self.config(menu = main_menu)

# <<<<<<< oop_refactoring
# =======
#         self.fig_type = 'circle'
#         # None в color_pick означает, что будет выбираться автоматически
#         self.color_pick = None
#         # стартовый цвет
#         self.color = Color()

# >>>>>>> master
        # добавить меню выбора цвета и меню выбора фигуры

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x, y))

        self.mainloop()
# <<<<<<< oop_refactoring
        


# app = App()
# =======

    def create_figure(self, event):
        u"""Метод, рисующий с отображением."""
        # переменные размеров окна
        x_s = self.winfo_width()
        y_s = self.winfo_height()

        # изменение цвета
        color = self.color.get_code()
        self.color.randomize()
        x0 = event.x - x_s/2
        y0 = event.y - y_s/2
        # масштаб - в зависимости от расстояния до центра
        size = start_figure_size / ((
            sqrt(x0*x0 + y0*y0)
            / sqrt(x_s*y_s)) + 0.15)

        # переключение разных фигур с помощью self.fig_type
        if self.fig_type == 'triangle':
            create_poly = self.canv.create_polygon
            def figure_function(x1, y1, x2, y2, fill, width):
                # Треугольник, обращёныый углом к центру
                x0 = (x1+x2)/2
                rx = x0-x_s/2
                y0 = (y1+y2)/2
                ry = y0-y_s/2
                diameter = abs(x2-x1)/2
                dx = rx/(sqrt(rx*rx)+0.001) * diameter
                dy = ry/(sqrt(ry*ry)+0.001) * diameter
                create_poly(
                    round(x0 - dx), round(y0 - dy),
                    round(x0 + dx), round(y0 - dy),
                    round(x0 - dx), round(y0 + dy),
                    fill=fill, width=width)
        elif self.fig_type == 'circle':
            figure_function = self.canv.create_oval
        elif self.fig_type == 'square':
            figure_function = self.canv.create_rectangle
        else:
            print('Warning')
            return None

        # координаты фигуры
        x1 = event.x - size
        x2 = event.x + size
        y1 = event.y - size
        y2 = event.y + size

        _figure_symmetry(figure_function, y1, x1, y2, x2, x_s, y_s, color)


if __name__ == '__main__':
    app = App()
# >>>>>>> master
