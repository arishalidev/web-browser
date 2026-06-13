import tkinter

WIDTH, HEIGHT = 800, 600
H_STEP, V_STEP = 13, 18
SCROLL_STEP = 100


def lex(body):
    in_tag = False
    text = ""
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

class Browser:
    def __init__(self):
        self.display_list = None
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

        self.window.bind("<Down>", self.scrolldown)


    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()


    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

def layout(text):
    display_list = []
    cursor_x, cursor_y = H_STEP, V_STEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += H_STEP

        if cursor_x >= WIDTH - H_STEP:
            cursor_y += V_STEP
            cursor_x = H_STEP

    return display_list
