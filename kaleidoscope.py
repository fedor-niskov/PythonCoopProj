from tkinter import *
import random

# стартовый цвет
r, g, b = 150, 150, 150
circle_size = 10
color_dif = 30
canv_size = 700

class App(Tk):
	def __init__(self):
		super(App, self).__init__()
		self.geometry("{}x{}".format(canv_size, canv_size))

		# создаем сам холст и помещаем его в окно
		canv = Canvas(self, bg='white')
		canv.grid(row = 0, column = 0, sticky = "wens")
		# чтобы занимал все окно
		self.columnconfigure(index = 0, weight = 1)
		self.rowconfigure(index = 0, weight = 1)
		self.bind('<B1-Motion>', self.create_figure)
		self.fig_type = "circle"
		
		# добавялем меню с кнопкой очистки холста
		main_menu = Menu(self)
		main_menu.add_cascade(label="Очистить", command = lambda: canv.delete("all"))
		self.config(menu = main_menu)


		# центрируем окно по центру экрана
		self.mainloop()
		
	def create_figure(self, event):
		# тут можно реализовать переключение разных фигур с помощью self.fig_type
		pass



app = App()
