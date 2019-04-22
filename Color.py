u"""Модуль работы с цветом"""
from random import randrange
from Palette import Palette

# стартовый цвет
START_R, START_G, START_B = 150, 150, 150


class Color():
    u"""Класс, обеспечивающий хранение, цвета, и выбор случайного цвета на основе текущего."""

    def __init__(self, red=START_R, green=START_G, blue=START_B):
        u"""Инициализация серым цветом."""
        self.red = red
        self.green = green
        self.blue = blue
        self.code = '#' + '%0.2X' % self.red + '%0.2X' % self.green + '%0.2X' % self.blue
        self.palette = Palette()
        self.color_dif = 30
        self.random_color = 1

    def decode(self):
        u"""Декодирование последнего цвета из hex в RGB."""
        self.red = int(self.code[1:3], 16)
        self.green = int(self.code[3:5], 16)
        self.blue = int(self.code[5:7], 16)

    def __next__(self):
        u"""Получить следующий цвет."""
        result = self.code
        if self.palette.ready:
            self.code = next(self.palette)
        else:
            if self.random_color == -1:
                self.red = self.randomize(self.red)
                self.green = self.randomize(self.green)
                self.blue = self.randomize(self.blue)
            elif self.random_color == -2:
                self.red = self.mutate(self.red)
                self.green = self.mutate(self.green)
                self.blue = self.mutate(self.blue)
            else:
                self.red = self.randomize(self.red)
                self.green = self.randomize(self.green)
                self.blue = self.randomize(self.blue)
            self.code = '#' + '%0.2X' % self.red + '%0.2X' % self.green + '%0.2X' % self.blue
        return result

    def mutate(self, component):
        u"""Плавное изменение одной компоненты цвета."""
        result = randrange(-self.color_dif, self.color_dif) + component
        if result > 255:
            result = 511 - result
        elif result <= 50:
            result = 50
        return result

    def randomize(self, component):
        u"""Получить следующий рандомный цвет"""
        result = randrange(-self.color_dif, self.color_dif) + component
        result = result % (256 - self.color_dif) + self.color_dif
        return result

    def define_palette(self, index=-1):
        u"""Загрузка палитры"""
        self.random_color = index
        self.palette.load(index)
