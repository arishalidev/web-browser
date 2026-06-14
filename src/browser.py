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

def replace_entity(text, entity, entity_replacement):
    index = text.find(entity)

    while index != -1:
        text = text[0:index] + entity_replacement + text[index+4: -1]
        index = text.find(entity)

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

        self.window.bind("<Down>", self.scroll_down)


    def load(self, url):

        if url.scheme == "http" or url.scheme == "https":
            body = url.request()
        elif url.scheme == "file":
            body = url.getfile()
        else:
            body = ""

        text = lex(body)
        text = replace_entity(text, "&lt;", "<")
        text = replace_entity(text, "&gt;", ">")

        self.display_list = layout(text)
        self.draw()


    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scroll_down(self):
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
