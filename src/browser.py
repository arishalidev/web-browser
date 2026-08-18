import socket
import tkinter
import tkinter.font
from typing import Literal

WIDTH, HEIGHT = 800, 600
H_STEP, V_STEP = 13, 18
SCROLL_STEP = 100
FONTS = {}

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out

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

        self.display_list = Layout(self.text).display_list
        self.draw()

    def load_blank(self):
        self.display_list = []
        self.draw()


    def draw(self):
        self.canvas.delete("all")
        for x, y, c, z in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + V_STEP < self.scroll: continue

            self.canvas.create_text(x, y - self.scroll, font=z, text=c, anchor="nw")

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
        self.display_list = Layout(self.text).display_list

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

class Layout():

    def __init__(self, tokens):
        self.display_list = []
        self.line = []

        self.cursor_x = H_STEP
        self.cursor_y = V_STEP

        self.weight: Literal["normal", "bold"] = "normal"
        self.style: Literal["roman", "italic"] = "roman"
        self.size = 12

        self.current_centered = False

        for tok in tokens:
            self.token(tok)

        self.flush()


    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)

        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += V_STEP
        elif tok.tag == "h1 class=\"title\"":
            self.current_centered = True
        elif tok.tag == "/h1":
            self.flush()
            self.cursor_y += V_STEP
            self.current_centered = False

    def word(self, word):
        font = get_font(
            weight=self.weight,
            style=self.style,
            size=self.size
        )

        w = font.measure(word)

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

        # Check if cursor reaches end of window
        if self.cursor_x + w > WIDTH - H_STEP:
            self.flush()

    def flush(self):
        if not self.line: return

        metrics = []
        for x, word, font in self.line:
            metrics.append(font.metrics())

        max_ascents = []
        for metric in metrics:
            max_ascents.append(metric["ascent"])
        max_ascent = max(max_ascents)

        baseline = self.cursor_y + 1.25 * max_ascent
        starting_pos_centered = (WIDTH / 2) - (self.cursor_x // 2)
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")

            if self.current_centered:
                x = x + starting_pos_centered

            self.display_list.append((x, y, word, font))

        max_descents = []
        for metric in metrics:
            max_descents.append(metric["descent"])
        max_descent = max(max_descents)

        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = H_STEP
        self.line = []

def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            weight=weight,
            slant=style,
            size=size
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]


