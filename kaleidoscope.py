u"""Запуск приложения по умолчанию."""
from App import App
from Lang import LanguageSelector
from Dict import Dict
from Dict import load_dict

if __name__ == '__main__':
    ls = LanguageSelector()
    ls.mainloop()
    load_dict(ls.lang)
    ls.destroy()
    app = App()
    app.mainloop()
