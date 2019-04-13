from tkinter import *
import random
from math import sqrt

# стартовый цвет
r, g, b = 150, 150, 150
circle_size = 10
canv_size = 700


class Color():
    """Класс, обеспечивающий хранение цвета и выбор рандомного на основе текущего"""
    def __init__(self, r = 150, g = 150, b = 150):
        self.r = r
        self.g = g
        self.b = b
        self.color_dif = 30
    
    def randomize(self):
        """Получить следующий рандомный цвет"""
        self.r = (random.randrange(-self.color_dif, self.color_dif) + self.r) % 206 + 50
        self.g = (random.randrange(-self.color_dif, self.color_dif) + self.g) % 206 + 50
        self.b = (random.randrange(-self.color_dif, self.color_dif) + self.b) % 206 + 50
        # print(self.r, self.g, self.b)
        return self

    def get_code(self):
        res = "#" + "%0.2X" % self.r + "%0.2X" % self.g + "%0.2X" % self.b
        return res
        



class App(Tk):
    """Главный класс приложения"""
    def __init__(self):
        super(App, self).__init__()
        self.geometry("{}x{}".format(canv_size, canv_size))
        self.title("Калейдоскоп")
        # создаем сам холст и помещаем его в окно
        self.canv = Canvas(self, bg='white')
        self.canv.grid(row = 0, column = 0, sticky = "wens")
        # чтобы занимал все окно
        self.columnconfigure(index = 0, weight = 1)
        self.rowconfigure(index = 0, weight = 1)
        self.bind('<B1-Motion>', self.create_figure)
        
        # добавляем меню с кнопкой очистки холста
        main_menu = Menu(self)
        main_menu.add_cascade(label="Очистить", command = lambda: self.canv.delete("all"))
        self.config(menu = main_menu)

        self.fig_type = "circle"
        # None в color_pick означает, что будет выбираться автоматически
        self.color_pick = None
        # стартовый цвет
        self.color = Color()
        
        # добавить меню выбора цвета и меню выбора фигуры

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry("+%d+%d" % (x, y))

        self.mainloop()
        
    def create_figure(self, event):
        """Метод, рисующий с отображением"""
        # тут можно реализовать переключение разных фигур с помощью self.fig_type
        
        # изначальные координаты кружка
        x1 = int(event.x) - circle_size
        x2 = int(event.x) + circle_size
        y1 = int(event.y) - circle_size
        y2 = int(event.y) + circle_size

        x_s = self.winfo_width()
        y_s = self.winfo_height()
        color = self.color.get_code()
        self.color.randomize()

        # масштаб - в зависимости от расстояния до центра
        size = circle_size / (sqrt((event.x*event.x + event.y*event.y)/(canv_size*canv_size))+.1)
        
        # изначальные координаты кружка
        x1 = event.x - size
        x2 = event.x + size
        y1 = event.y - size
        y2 = event.y + size
        
        def figure_symmetry(func, y1, x1, y2, x2, color):
            # коэффициенты растяжения для отображения относительно диагоналей
            x_k = y_s / x_s
            y_k = x_s / y_s
            
            # 8 кругов
            for A1, A3 in [(x1, x2), (x_s - x1, x_s-x2)]:
                for B2, B4 in [(y_s-y1, y_s-y2),(y1, y2)]:
                    func(round(A1), round(B2), round(A3), round(B4), fill = color, width = 0)
            for A1, A3 in [(y1 * y_k, y2 * y_k), ((-y1 + y_s) * y_k, (-y2 + y_s) * y_k)]:
                for B2, B4 in [(x1 * x_k, x2 * x_k), ((-x1 + x_s) * x_k, (-x2 + x_s) * x_k)]:
                    func(round(A1), round(B2), round(A3), round(B4), fill = color, width = 0)
        figure_symmetry(self.canv.create_oval, y1, x1, y2, x2, color)


app = App()
