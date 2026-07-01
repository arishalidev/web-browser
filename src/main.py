import tkinter

from browser import Browser
from url import URL

if __name__ == "__main__":
    b = Browser()
    b.load(URL("https://browser.engineering/graphics.html"))
    tkinter.mainloop()


