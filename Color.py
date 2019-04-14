import random


# стартовый цвет
start_R, start_G, start_B = 150, 150, 150

class Color():
    u"""Класс, обеспечивающий хранение, цвета, и выбор случайного цвета на основе текущего."""

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