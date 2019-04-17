u"""Файл с классом приложения и необходимыми для него классами"""
from tkinter import Toplevel, Scale, HORIZONTAL, Button, Tk, Menu

from Paint import Paint, HistoryRecord

START_CANVAS_SIZE = 700
START_FIGURE_SIZE = 10
START_SYMMETRY_NUMBER = 8
_DEBUG = True

class FigSizer(Toplevel):
    u"""Окно, которое открывается для выбора размера фигуры"""
    def __init__(self, default_size=START_FIGURE_SIZE):
        Toplevel.__init__(self)
        self.figsize = Scale(self, from_=1, to=50, orient=HORIZONTAL)
        self.figsize.set(default_size)
        self.figsize.pack()
        self.button = Button(self, text='OK', command=self.quit)
        self.button.pack()
        self.title('Выберите размер')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        # по центру экрана
        x_center = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y_center = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x_center, y_center))

class NumSymmetry(Toplevel):
    u"""Окошко выбора числа симметричных отражений"""
    def __init__(self, default_num_symm=START_SYMMETRY_NUMBER):
        text = 'Число больше нуля - симметричные отражения, меньше нуля - симметричные повороты'
        Toplevel.__init__(self)
        self.num_symm = Scale(self, from_=-8, to=16,
                              orient=HORIZONTAL,
                              length=len(text)*8)
        self.num_symm.set(default_num_symm)
        self.num_symm.pack()
        self.button = Button(self, text=text, command=self.quit)
        self.button.pack()
        self.title('Выбор числа отражений, ноль - одна кисть')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        # по центру экрана
        x_center = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y_center = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x_center, y_center))

class App(Tk):
    u"""Главный класс приложения."""

    def __init__(self):
        u"""Создание холста и запуск цикла отрисовки"""
        super(App, self).__init__()
        self.geometry('{y}x{y}'.format(y=START_CANVAS_SIZE))
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
                                   command=lambda: self.canv.color.define_palette(-1))
        palette_choice.add_command(label='Плавная случайная палитра',
                                   command=lambda: self.canv.color.define_palette(-2))
        palette_choice.add_command(label='Палитра цвета сердца (полином)',
                                   command=lambda: self.canv.color.define_palette(-4))
        palette_choice.add_command(label='Палитра 1',
                                   command=lambda: self.canv.color.define_palette(1))
        palette_choice.add_command(label='Палитра 2',
                                   command=lambda: self.canv.color.define_palette(2))
        palette_choice.add_command(label='Палитра 3',
                                   command=lambda: self.canv.color.define_palette(3))

        # меню выбора масштабирования
        scale_choice = Menu(main_menu)
        scale_choice.add_command(
            label='Константа',
            command=lambda: self.canv.set_scale_function('constant'))
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

        # меню выбора стандартных функций
        func_choice = Menu(main_menu)
        func_choice.add_command(
            label='Кардиоида',
            command=lambda: self.heart(1))
        func_choice.add_command(
            label='Сердечко',
            command=lambda: self.heart(2))

        # меню работы с файлами
        file_menu = Menu(main_menu)
        file_menu.add_command(
            label='Загрузить...',
            command=self.canv.load)
        file_menu.add_command(
            label='Сохранить...',
            command=self.canv.save)

        file_menu.add_command(
            label='Сохранить картинку...',
            command=self.canv.save_to_png)

        # добавляем кнопки и менюшки
        main_menu.add_cascade(label='Файл', menu=file_menu)
        main_menu.add_command(label='Очистить', command=self.canv.cleanup)
        main_menu.add_command(label='Undo', command=self.canv.undo)
        main_menu.add_command(label='Redo', command=self.canv.redo)
        main_menu.add_cascade(label='Станд. функции', menu=func_choice)
        main_menu.add_cascade(label='Стиль кисти', menu=brush_style)
        main_menu.add_cascade(label='Масштабирование', menu=scale_choice)
        main_menu.add_cascade(label='Палитра', menu=palette_choice)
        main_menu.add_command(label='Размер', command=self.select_fig_size)
        main_menu.add_command(label='Симметрия', command=self.select_num_symm)
        self.config(menu=main_menu)

        # центрируем окно по центру экрана
        self.update_idletasks()
        x_center = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y_center = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x_center, y_center))

        self.mainloop()

    def select_fig_size(self):
        """Установка размера фигуры"""
        fig_sizer = FigSizer(self.canv.fig_size)
        fig_sizer.mainloop()
        self.canv.fig_size = fig_sizer.figsize.get()
        fig_sizer.destroy()

    def select_num_symm(self):
        u"""Установка числа симметричных отражений"""
        num_symmetry = NumSymmetry(self.canv.num_symm)
        num_symmetry.mainloop()
        num_symm = num_symmetry.num_symm.get()
        if num_symm > 0:
            self.canv.num_symm = num_symm * 2
        else:
            self.canv.num_symm = num_symm
        self.canv.recalculate_coefficients()
        num_symmetry.destroy()

    def paint_function(self, func, steps):
        u"""Функция отрисовки параметрической функции
        func: (float, int, int) -> (float, float)
        func(t, x, y), где t in [0,1)
        с шагом дискретизации 1/steps"""
        x_size = self.winfo_width()
        y_size = self.winfo_height()
        for time in range(0, steps):
            x_coord, y_coord = func(time /steps, x_size, y_size)
            self.canv.history.append(HistoryRecord(
                x=x_coord/x_size,
                y=y_coord/y_size,
                color=self.canv.color.code,
                type = self.canv.fig_type,
                distance = self.canv.distance_func_name,
                size = self.canv.fig_size,
                time = self.canv.time,
                snum = self.canv.num_symm
            ))
            self.canv.create_figure(x_coord, y_coord, x_size, y_size)

    def heart(self, index=0):
        """Сердечко <3
        Обычная кардиоида, в двух вариантах исполнения"""
        from math import sin, cos, pi, sqrt
        if index == 2:
            def func1(time, x_size, y_size):
                x_coord = 16.*sin(time*pi*2.)**3
                y_coord = -13.*cos(time*pi*2.)+5.*cos(4.*pi*time)+2.*cos(6.*pi*time)+cos(8.*pi*time)
                return x_coord*x_size/128 + x_size/2, y_coord*y_size/128 + y_size/4
            self.canv.color.define_palette(-2 - index)
            self.paint_function(func1, 1000)
        if index == 1:
            def func2(time, x_size, y_size):
                x_coord = cos(time*pi*2.)
                y_coord = -sin(time*pi*2.)-sqrt(abs(x_coord))
                return x_coord*x_size/7 + x_size/2, y_coord*y_size/8 + y_size/4
            self.canv.color.define_palette(-2 - index)
            self.paint_function(func2, 1000)
