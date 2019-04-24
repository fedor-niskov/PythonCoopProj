u"""Файл с классом приложения и необходимыми для него классами"""
from tkinter import Button, HORIZONTAL, Menu, Scale, Tk, Toplevel

from Paint import Paint

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
                              length=len(text) * 8)
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
        self.main_menu = Menu(self)

        # меню выбора фигуры
        self.brush_style = Menu(self.main_menu)
        self.brush_style.add_command(label='Кружок',
                                command=lambda: self.canv.set_style('circle'))
        self.brush_style.add_command(label='Квадрат',
                                command=lambda: self.canv.set_style('square'))
        self.brush_style.add_command(label='Треугольник',
                                command=lambda: self.canv.set_style('triangle'))

        # меню выбора цвета
        self.palette_choice = Menu(self.main_menu)
        self.palette_choice.add_command(label='Случайная палитра',
                                        command=lambda: self.canv.color.define_palette(-1))
        self.palette_choice.add_command(label='Плавная случайная палитра',
                                        command=lambda: self.canv.color.define_palette(-2))
        self.palette_choice.add_command(label='Палитра цвета сердца (полином)',
                                        command=lambda: self.canv.color.define_palette(-4))
        self.palette_choice.add_command(label='Палитра 1',
                                        command=lambda: self.canv.color.define_palette(1))
        self.palette_choice.add_command(label='Палитра 2',
                                        command=lambda: self.canv.color.define_palette(2))
        self.palette_choice.add_command(label='Палитра 3',
                                        command=lambda: self.canv.color.define_palette(3))

        # меню выбора масштабирования
        self.scale_choice = Menu(self.main_menu)
        self.scale_choice.add_command(
            label='Константа',
            command=lambda: self.canv.set_scale_function('constant'))
        self.scale_choice.add_command(
            label='Обратное расстояние до центра',
            command=lambda: self.canv.set_scale_function('inverse_dist'))
        self.scale_choice.add_command(
            label='Манхэттенское расстояние до центра',
            command=lambda: self.canv.set_scale_function('manhatten'))
        self.scale_choice.add_command(
            label='Квадрат расстояния до центра',
            command=lambda: self.canv.set_scale_function('square_dist'))
        self.scale_choice.add_command(
            label='Масштабирование, обратное Манхэттенскому',
            command=lambda: self.canv.set_scale_function('inv_Chebushev'))

        # меню выбора стандартных функций
        self.func_choice = Menu(self.main_menu)
        self.func_choice.add_command(
            label='Кардиоида',
            command=lambda: self.canv.heart(1))
        self.func_choice.add_command(
            label='Сердечко',
            command=lambda: self.canv.heart(2))

        # меню работы с файлами
        self.file_menu = Menu(self.main_menu)
        self.file_menu.add_command(
            label='Загрузить...',
            command=self.canv.load)
        self.file_menu.add_command(
            label='Сохранить...',
            command=self.canv.save)
        self.file_menu.add_command(
            label='Сохранить картинку...',
            command=self.canv.save_to_png)

        # добавляем кнопки и менюшки
        self.main_menu.add_cascade(label='Файл', menu=self.file_menu)
        self.main_menu.add_command(label='Очистить', command=self.canv.cleanup)
        self.main_menu.add_command(label='Undo', command=self.canv.undo)
        self.main_menu.add_command(label='Redo', command=self.canv.redo)
        self.main_menu.add_cascade(label='Станд. функции', menu=self.func_choice)
        self.main_menu.add_cascade(label='Стиль кисти', menu=self.brush_style)
        self.main_menu.add_cascade(label='Масштабирование', menu=self.scale_choice)
        self.main_menu.add_cascade(label='Палитра', menu=self.palette_choice)
        self.main_menu.add_command(label='Размер', command=self.select_fig_size)
        self.main_menu.add_command(label='Симметрия', command=self.select_num_symm)
        self.config(menu=self.main_menu)

        # центрируем окно по центру экрана
        self.update_idletasks()
        x_center = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y_center = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x_center, y_center))

        # self.mainloop()

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
