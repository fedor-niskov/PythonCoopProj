from tkinter import *
import random

# стартовый цвет
r, g, b = 150, 150, 150
circle_size = 10
color_dif = 30
canv_size = 700

# класс, обеспечивающий хранение цвета и выбор рандомного на основе текущего
class Color():
    def __init__(self):
        self.r = 150
        self.g = 150
        self.b = 150
    
    def get_rand_color(self):
        self.r = (random.randrange(-color_dif, color_dif) + r) % 206 + 50
        self.g = (random.randrange(-color_dif, color_dif) + g) % 206 + 50
        self.b = (random.randrange(-color_dif, color_dif) + b) % 206 + 50
        res = "#" + "%0.2X" % self.r + "%0.2X" % self.g + "%0.2X" % self.b
        return res

    def get_code(self):
        res = "#" + "%0.2X" % self.r + "%0.2X" % self.g + "%0.2X" % self.b
        return res
        



class App(Tk):
    def __init__(self):
        super(App, self).__init__()
        self.geometry("{}x{}".format(canv_size, canv_size))
        self.title("Калейдоскоп")
        # создаем сам холст и помещаем его в окно
        canv = Canvas(self, bg='white')
        canv.grid(row = 0, column = 0, sticky = "wens")
        # чтобы занимал все окно
        self.columnconfigure(index = 0, weight = 1)
        self.rowconfigure(index = 0, weight = 1)
        self.bind('<B1-Motion>', self.create_figure)
        
        # добавялем меню с кнопкой очистки холста
        main_menu = Menu(self)
        main_menu.add_cascade(label="Очистить", command = lambda: canv.delete("all"))
        self.config(menu = main_menu)

        self.fig_type = "circle"
        # None в color_pick означает, что будет выбираться автоматически
        self.color_pick = None
        # стартовый цвет
        

        # добавить меню выбора цвета и меню выбора фигуры

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry("+%d+%d" % (x, y))

        self.mainloop()
        
    def create_figure(self, event):
        # тут можно реализовать переключение разных фигур с помощью self.fig_type
        pass

    # функция для рандомного выбора цвета на основе предыдущего использованного
    def get_rand_color():
        global r, g, b
        # +50 для убирания темных (черного)
        r = (random.randrange(-color_dif, color_dif) + r) % 206 + 50
        g = (random.randrange(-color_dif, color_dif) + g) % 206 + 50
        b = (random.randrange(-color_dif, color_dif) + b) % 206 + 50
        res = "#" + "%0.2X" % r + "%0.2X" % g + "%0.2X" % b
        return res


app = App()
