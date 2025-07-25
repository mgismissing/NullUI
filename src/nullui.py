import sys
import os
import tty
from mouse import MouseHandler, MouseData
from cmp import CMPImage
from typing import Literal, Callable, Any, Self

class Margin:
    def __init__(self, ml: int, mt: int, mr: int, mb: int):
        self.ml = ml
        self.mt = mt
        self.mr = mr
        self.mb = mb

class Style:
    class Box:
        def __init__(self, tl: str, t: str, tr: str, l: str, r: str, bl: str, b: str, br: str):
            self.tl = tl
            self.t = t
            self.tr = tr
            self.top = self.tl + self.t + self.tr
            self.l = l
            self.r = r
            self.center = self.l + " " + self.r
            self.bl = bl
            self.b = b
            self.br = br
            self.bottom = self.bl + self.b + self.br
            self.str = self.top + self.center + self.bottom
        def __str__(self): return self.str
        def __repr__(self): return self.__str__()
    class Sep:
        def __init__(self, t: str, c: str, b: str):
            self.t = t
            self.c = c
            self.b = b
            self.str = self.t + self.c + self.b
        def __str__(self): return self.str
        def __repr__(self): return self.__str__()

class Widget:
    def __init__(self):
        pass

    def __render__(self, scr: Any):
        pass

    __add__ = lambda self, w: [self, w]
    __radd__ = lambda self, l: l + [self]
    __pos__ = lambda self: [self]

class MovableWidget(Widget):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y

class SizableWidget(MovableWidget):
    margin = Margin(0, 0, 0, 0)
    def __init__(self, x: int, y: int, w: int, h: int):
        super().__init__(x, y)
        self.w = w
        self.h = h

class ClickableWidget(SizableWidget):
    margin = Margin(0, 0, 1, 1)

    def __init__(self, x: int, y: int, w: int, h: int, onclick: Callable[[Self, int, int], None]):
        super().__init__(x, y, w, h)
        self.onclick = onclick

def margin_to_rect(widget: SizableWidget) -> tuple[int, int, int, int]:
    return (
        widget.x-widget.margin.ml,
        widget.x+widget.w+widget.margin.mr-1,
        widget.y-widget.margin.mt,
        widget.y+widget.h+widget.margin.mb-1
    )

def in_bounds(bounds: tuple[int, int, int, int], x: int, y: int):
    return bounds[0] <= x <= bounds[1] and bounds[2] <= y <= bounds[3]

def in_widget_bounds(widget: SizableWidget, x: int, y: int):
    return in_bounds(margin_to_rect(widget), x, y)

class Screen:
    default_color = ""
    default_buf = ""
    square_box = Style.Box("┌", "─", "┐", "│", "│", "└", "─", "┘")
    null_box = Style.Box("🮣", "─", "┐", "│", "│", "└", "─", "🮠")
    chamfered_box = Style.Box("🮣", "─", "🮢", "│", "│", "🮡", "─", "🮠")
    rounded_box = Style.Box("╭", "─", "╮", "│", "│", "╰", "─", "╯")

    connected_sep = Style.Sep("┬", "│", "┴")
    notch_sep = Style.Sep("│", "│", "│")
    dashed_notch_sep = Style.Sep("╎", "╎", "╎")
    dotted_notch_sep = Style.Sep("┊", "┊", "┊")

    def __enter__(self, autoclear: bool = True):
        self.autoclear = True
        sys.stdout.write("\033[?25l\033[2J")
        sys.stdout.flush()
        self.tty_fileno = sys.stdin.fileno()
        self.tty_default = tty.tcgetattr(self.tty_fileno)
        tty.setraw(self.tty_fileno)
        self.reset_buf()
        self.children: list[Widget] = []
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        tty.tcsetattr(self.tty_fileno, tty.TCSADRAIN, self.tty_default)
        sys.stdout.write("\033[?25h\033[2J\033[H")
        sys.stdout.flush()
        return False
        
    def reset_buf(self):
        self.buf = ("\033[2J" if self.autoclear else "") + "\033[H" + self.default_buf

    def move(self, x: int, y: int):
        self.buf += f"\033[{y};{x}H"
    def home(self):
        self.move(1, 1)
    
    def print(self, s: str):
        self.buf += s
    def print_at(self, x: int, y: int, s: str):
        self.move(x, y)
        self.print(s)
    
    def draw_box(self, x: int, y: int, w: int, h: int, box_style: Style.Box):
        self.print_at(x, y, f"{box_style.tl}{box_style.t*w}{box_style.tr}")
        for oy in range(h):
            self.print_at(x, y+oy+1, box_style.l)
            self.print_at(x+w+1, y+oy+1, box_style.r)
        self.print_at(x, y+h+1, f"{box_style.bl}{box_style.b*w}{box_style.br}")
    def draw_filled_box(self, x: int, y: int, w: int, h: int, box_style: Style.Box):
        self.print_at(x, y, f"{box_style.tl}{box_style.t*w}{box_style.tr}")
        for oy in range(h):
            self.print_at(x, y+oy+1, f"{box_style.l}{" "*w}{box_style.r}")
        self.print_at(x, y+h+1, f"{box_style.bl}{box_style.b*w}{box_style.br}")
    
    def draw_open_box(self, x: int, y: int, w: int, h: int, left: bool, top: bool, right: bool, bottom: bool, box_style: Style.Box):
        if left and top and right and bottom: self.draw_box(x, y, w, h, box_style)
        if top: self.print_at(x, y+{0 if left else 1}, f"{box_style.tl if left else ""}{box_style.t*w}{box_style.tr if right else ""}")
        for oy in range(h):
            if left: self.print_at(x, y+oy+1, box_style.l)
            if right: self.print_at(x+w+1, y+oy+1, box_style.r)
        if bottom: self.print_at(x, y+h+1+{0 if left else 1}, f"{box_style.bl if left else ""}{box_style.b*w}{box_style.br if right else ""}")
    def draw_open_filled_box(self, x: int, y: int, w: int, h: int, left: bool, top: bool, right: bool, bottom: bool, box_style: Style.Box):
        if left and top and right and bottom: self.draw_box(x, y, w, h, box_style)
        self.print_at(x, y, f"{box_style.tl if left else " "}{(box_style.t if top else " ")*w}{box_style.tr if right else " "}")
        for oy in range(h):
            self.print_at(x, y+oy+1, f"{box_style.l if left else " "}{" "*w}{box_style.r if right else " "}")
        self.print_at(x, y+h+1, f"{box_style.bl if left else " "}{(box_style.b if bottom else " ")*w}{box_style.br if right else " "}")

    def handle_mouse(self, data: str, mouse: MouseHandler):
        out = mouse.parse(data)
        if out:
            buttons: list[ClickableWidget] = list(filter(lambda child: isinstance(child, ClickableWidget), self.children))
            for button in buttons:
                if (not out.pressed) and (out.btn == 0) and in_widget_bounds(button, out.x, out.y):
                    button.onclick(button, out.x - button.x, out.y - button.y)
                    break
        return out
    
    def __render__(self):
        for child in self.children:
            child.__render__(self)
    
    def add_child(self, w: Widget | list[Widget]):
        wl = w if type(w) == list else [w]
        for widget in wl:
            self.children.append(widget)
        return self
    
    __add__ = lambda self, w: self.add_child(w)
    __iadd__ = lambda self, w: self.__add__(w)

    def show(self):
        self.__render__()
        sys.stdout.write(self.buf)
        sys.stdout.flush()

class Label(SizableWidget):
    def __init__(self, x: int, y: int, w: int, h: int, text: str):
        super().__init__(x, y, w, h)
        self.text = text
    
    def __render__(self, scr: Screen):
        for l, y in enumerate(range(self.y, self.y+self.h)):
            scr.print_at(self.x, y, self.text[self.w*l:self.w*(l+1)].ljust(self.w, " "))

class ProgressBar(Label):
    def __init__(self, x: int, y: int, w: int, h: int, progress: int = 0, max_progress: int = 100):
        super().__init__(x, y, w, h, "")
        self.progress = progress
        self.max_progress = max_progress
    
    def __render__(self, scr: Screen):
        for y in range(self.y, self.y+self.h):
            blocks = int(self.w * 8 * (self.progress / self.max_progress))
            s = ""
            while blocks >= 8:
                s += "█"
                blocks -= 8
            match blocks:
                case 7: s += "▉"
                case 6: s += "▊"
                case 5: s += "▋"
                case 4: s += "▌"
                case 3: s += "▍"
                case 2: s += "▎"
                case 1: s += "▏"
            scr.print_at(self.x, y, s.ljust(self.w, " ")[:self.w])

class Box(SizableWidget):
    def __init__(self, x: int, y: int, w: int, h: int, filled: bool, box_style: Style.Box):
        super().__init__(x, y, w, h)
        self.filled = filled
        self.box_style = box_style
    
    def __render__(self, scr: Screen):
        if self.filled:
            scr.draw_filled_box(self.x, self.y, self.w, self.h, self.box_style)
        else:
            scr.draw_box(self.x, self.y, self.w, self.h, self.box_style)

class Image(MovableWidget):
    def __init__(self, x: int, y: int, image: CMPImage):
        super().__init__(x, y)
        self.image = image
    
    def __render__(self, scr: Screen):
        for y, l in enumerate(self.image.read().splitlines()):
            for x, c in enumerate(l):
                if c != "\x00":
                    scr.print_at(self.x+x, self.y+y, c)

class ClickableLabel(ClickableWidget):
    margin = Margin(0, 0, 0, 0)

    def __init__(self, x: int, y: int, w: int, h: int, text: str, onclick: Callable[[Self, int, int], None]):
        super().__init__(x, y, w, h, onclick)
        self.text = text
    
    def __render__(self, scr: Screen):
        for l, y in enumerate(range(self.y, self.y+self.h)):
            scr.print_at(self.x, y, self.text[self.w*l:self.w*(l+1)].ljust(self.w, " "))

class Button(ClickableLabel):
    margin = Margin(0, 0, 2, 2)

    def set_side(self, side: Literal["l", "c", "r", None]):
        self.side = side
        match side:
            case "l": self.margin = Margin(0, 0, 1, 2)
            case "c": self.margin = Margin(-1, 0, 1, 2)
            case "r": self.margin = Margin(-1, 0, 2, 2)
            case None: self.margin = Button.margin

    def __init__(self, x: int, y: int, w: int, h: int, text: str, box_style: Style.Box, onclick: Callable[[Self, int, int], None], side: Literal["l", "c", "r", None] = None):
        super().__init__(x, y, w, h, text, onclick)
        self.box_style = box_style
        self.set_side(side)
    
    def __render__(self, scr: Screen):
        match self.side:
            case "l": scr.draw_open_filled_box(self.x, self.y, self.w, self.h, True, True, False, True, self.box_style)
            case "c": scr.draw_open_filled_box(self.x, self.y, self.w, self.h, False, True, False, True, self.box_style)
            case "r": scr.draw_open_filled_box(self.x, self.y, self.w, self.h, False, True, True, True, self.box_style)
            case None: scr.draw_filled_box(self.x, self.y, self.w, self.h, self.box_style)
        for l, y in enumerate(range(self.y, self.y+self.h)):
            scr.print_at(self.x+1, y+1, self.text[self.w*l:self.w*(l+1)].ljust(self.w, " "))

class ButtonGroup(ClickableWidget):
    def __init__(self, x: int, y: int, sep_style: Style.Sep, children: list[Button]):
        self.sep_style = sep_style

        w = h = 0
        self.children = children
        for i, child in enumerate(self.children):
            if child.h > h: h = child.h

            child.x = x + w
            child.y = y
            child.set_side(None if len(self.children) == 1 else ("l" if i == 0 else ("r" if i == len(self.children)-1 else "c")))
            
            w += margin_to_rect(child)[2] + 1
        for child in self.children: child.h = h
        h += 1

        def clicked(self, x: int, y: int):
            for child in self.children:
                if in_widget_bounds(child, self.x+x, self.y+y):
                    child.onclick(child, self.x+x-child.x+child.margin.ml, self.y+y-child.y+child.margin.mt)
                    break
        super().__init__(x, y, w, h, clicked)
    
    def __render__(self, scr: Screen):
        for child in self.children:
            child.__render__(scr)
        cx = 0
        for i, child in enumerate(self.children):
            if i < len(self.children)-1:
                cx += margin_to_rect(child)[2] + 1
                scr.print_at(self.x+cx, self.y, self.sep_style.t)
                scr.print_at(self.x+cx, self.y+1, self.sep_style.c)
                scr.print_at(self.x+cx, self.y+2, self.sep_style.b)
