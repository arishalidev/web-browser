import socket
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
        text = text[0:index] + entity_replacement + text[index+4: len(text)]
        index = text.find(entity)

    return text


class Browser:
    def __init__(self, test_mode = False):
        self.display_list = None
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack(fill="both", expand=1)

        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("<MouseWheel>", self.mouse_scroll)
        self.window.bind("<Configure>", self.resize)

        self.current_host = ("", None)
        self.test_mode = test_mode
        self.text = ""

    def load(self, url):

        if url.blank:
            self.load_blank()

        body = ""

        try:
            match url.scheme:
                case "http" | "https":
                    body = url.request(url.host == self.current_host[0], self.current_host[1])
                    self.current_host = (url.host, url.socket)
                case "file":
                    body = url.getfile()

            body = replace_entity(body, "&lt;", "<")
            body = replace_entity(body, "&gt;", ">")

            if not url.view_source:
                self.text = lex(body)
            else:
                self.text = body

        except (socket.gaierror, AttributeError):
            self.load_blank()
            return

        self.display_list = layout(self.text)
        self.draw()

    def load_blank(self):
        self.display_list = []
        self.draw()


    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + V_STEP < self.scroll: continue

            self.canvas.create_text(x, y - self.scroll, text=c)

        self.draw_scroll_bar()

    def scroll_down(self, e):
        page_height = self.display_list[-1][1]
        if self.scroll + HEIGHT < page_height:
            self.scroll += SCROLL_STEP
            self.draw()

    def scroll_up(self, e):
        if not self.scroll <= 0:
            self.scroll -= SCROLL_STEP
            self.draw()

    # only works on mac
    def mouse_scroll(self, e):

        page_height = self.display_list[-1][1]

        # only allow scrolling down when at top of page, and only allow scrolling up when at bottom of page
        if (not self.scroll <= 0 or e.delta < 0) and (self.scroll + HEIGHT - V_STEP < page_height or e.delta > 0):
            self.scroll += e.delta * - 3
            self.draw()

    def resize(self, e):
        if e.widget != self.window:
            return

        global WIDTH, HEIGHT
        WIDTH, HEIGHT = e.width, e.height

        self.draw()
        self.display_list = layout(self.text)

    def draw_scroll_bar(self):
        page_height = self.display_list[-1][1] if self.display_list else 0

        if page_height <= HEIGHT:
            return

        scroll_bar_height = (HEIGHT / page_height) * HEIGHT
        scroll_bar_width = 12

        x_margin = 4

        y_start = ((self.scroll / page_height) * HEIGHT)
        y_end = y_start +  scroll_bar_height

        self.canvas.create_rectangle(WIDTH - scroll_bar_width - x_margin, y_start, WIDTH - x_margin, y_end, fill="blue")

def layout(text):
    display_list = []
    cursor_x, cursor_y = H_STEP, V_STEP
    for c in text:

        if c == "\n":
            cursor_y += V_STEP + 6
            cursor_x = H_STEP
            continue

        display_list.append((cursor_x, cursor_y, c))
        cursor_x += H_STEP


        # Check if cursor reaches end of window
        if cursor_x >= WIDTH - H_STEP:
            cursor_y += V_STEP
            cursor_x = H_STEP

    return display_list
