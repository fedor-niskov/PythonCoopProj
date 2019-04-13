from tkinter import *
import random

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



class App(Tk):
    """Главный класс приложения"""
    def __init__(self):
        super(App, self).__init__()
        self.geometry("{}x{}".format(canv_size, canv_size))
        self.title("Калейдоскоп")
        # создаем сам холст и помещаем его в окно
        self.canv = Paint(self, bg='white')
        self.canv.grid(row = 0, column = 0, sticky = "wens")
        # чтобы занимал все окно
        self.columnconfigure(index = 0, weight = 1)
        self.rowconfigure(index = 0, weight = 1)
        
        # добавляем меню с кнопкой очистки холста
        main_menu = Menu(self)
        main_menu.add_cascade(label="Очистить", command = lambda: self.canv.delete("all"))
        self.config(menu = main_menu)

        # добавить меню выбора цвета и меню выбора фигуры

        # центрируем окно по центру экрана
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry("+%d+%d" % (x, y))

        self.mainloop()
        


app = App()
