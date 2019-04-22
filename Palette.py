u"""Модуль палитры"""
from tkinter import messagebox
from os.path import isfile
DISCRETE_STEP = 1024


class Palette():
    u"""Класс палитры - загрузка из файла, либо установка функциональной зависимости"""
    def __init__(self):
        self.palette = None
        self.color_dif = 10
        self.gradient = 0.
        self.func = None
        self.ready = 0
        self.colours = ([150], [100], [230])

    def __next__(self):
        if self.palette:
            return next(self.palette)
        if self.func:
            self.gradient += self.color_dif / DISCRETE_STEP
            if self.gradient > 1.:
                self.gradient -= 1.0
            result = self.func(self.gradient)
            return result
        return '#000000'

    def load(self, index=-1):
        u"""Определение палитры, если возможно, её загрузка из файла"""
        self.func = None
        self.palette = None
        self.ready = 0
        if index > 0:
            if isfile('./palette{}.txt'.format(str(index))):
                palette = []
                with open('./palette{}.txt'.format(str(index))) as palette_text:
                    for line in palette_text:
                        count = len(line) // 6
                        for i in range(count):
                            position = i * 6
                            palette.append('#' + line[position:position + 6])
                self.gradient = 0.
                self.ready = 1

                def cycle(palette):
                    while True:
                        for element in palette:
                            yield element
                self.palette = cycle(palette)
            else:
                messagebox.showerror(
                    "Ошибка загрузки палитры.",
                    "Внимание!\n\
Не удалось загрузить файл палитры.\n\
Установлено случайное изменение цветов.")
                self.ready = 0
        else:
            if index > -3:
                self.ready = 0
            elif index == -3:
                red = [-420., 861.42857143, -438.61904762, 241.88095238]
                green = [-936., 2131.71428571, -1183.42857143, 212.35714286]
                blue = [-726., 1891.71428571, -1152.69047619, 221.4047619]
                self.colours = (red, green, blue)
                self.ready = 3
                self.func = self.poly
            elif index == -4:
                red = [344.19642857, -366.33928571, 250.46428571]
                green = [42.85714286, -42.71428571, 19.14285714]
                blue = [47.32142857, -47.17857143, 20.07142857]
                self.colours = (red, green, blue)
                self.ready = 2
                self.func = self.poly
            else:
                messagebox.showerror(
                    "Ошибка загрузки палитры.",
                    "Внимание!\n\
Не удалось загрузить цветовой полином.\n\
Пожалуйста, проверьте настройки.")
                self.ready = 0
        if self.ready:
            next(self)
        return index

    def poly(self, time):
        u"""Полином заданной степени, возвращает интерполированное значение цвета"""
        if time > 1.0:
            time = 0.0
        if time < 0.0:
            time = 1.0
        deg = self.ready
        r_coeffs, g_coeffs, b_coeffs = self.colours
        power = [time**(deg - k) for k in range(deg + 1)]
        r_comp = round(sum(r_coeffs[k] * power[k] for k in range(deg + 1)))
        g_comp = round(sum(g_coeffs[k] * power[k] for k in range(deg + 1)))
        b_comp = round(sum(b_coeffs[k] * power[k] for k in range(deg + 1)))
        return '#' + '%0.2X' % r_comp + '%0.2X' % g_comp + '%0.2X' % b_comp
