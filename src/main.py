import tkinter

from browser import Browser
from url import URL

if __name__ == "__main__":
    b = Browser()
    b.load(URL("https://example.com"))
    tkinter.mainloop()


