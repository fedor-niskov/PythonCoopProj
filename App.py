from tkinter import *
from math import sqrt
from tkinter import filedialog
from tkinter import messagebox

from Paint import Paint


u"""Файл с классом приложения и необходимыми для него классами"""
canv_size = 700
start_figure_size = 10

class FigSizer(Toplevel):
    u"""Окно, которое открывается для выбора размера фигуры"""
    def __init__(self, default_size=start_figure_size):
        Toplevel.__init__(self)
        self.figsize = Scale(self, from_=1, to=50, orient=HORIZONTAL)
        self.figsize.set(default_size)
        self.figsize.pack()
        self.button = Button(self, text='OK', command=self.quit)
        self.button.pack()
        self.title('Выберите размер')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        # по центру экрана
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x, y))


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
                                   command=lambda: self.canv.define_pallete(3))

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
        main_menu.add_command(label='Размер', command=self.select_fig_size)
        self.config(menu=main_menu)

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x, y))

        self.mainloop()

    def select_fig_size(self):
        fs = FigSizer(self.canv.fig_size)
        fs.mainloop()
        self.canv.fig_size = fs.figsize.get()
        fs.destroy()