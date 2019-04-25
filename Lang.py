u"""Файл с классом диалога для выбора языка"""
from tkinter import Tk, Button, W, E, N, S


class LanguageSelector(Tk):
    u"""Начальный диалог для выбора языка."""
    
    def __init__(self):
        Tk.__init__(self)
        self.lang = '???'
        self.bEn = Button(text='English', command=lambda: self.set_lang('English'))
        self.bEn.grid(sticky=W+E+N+S)
        self.bRu = Button(text='Русский', command=lambda: self.set_lang('Russian'))
        self.bRu.grid(sticky=W+E+N+S)
        self.columnconfigure(0, weight=1)
        for r in range(self.size()[1]):
            self.rowconfigure(r, weight=1)
        # по центру экрана
        x_center = (self.winfo_screenwidth() - self.winfo_width()) / 2
        y_center = (self.winfo_screenheight() - self.winfo_height()) / 2
        self.wm_geometry('+%d+%d' % (x_center, y_center))

    def set_lang(self, l):
        self.lang = l
        self.quit()

