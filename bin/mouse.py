import sys
import re

class MouseData:
    def __init__(self, btn: int, x: int, y: int, pressed: bool):
        self.btn = btn
        self.x = x
        self.y = y
        self.pressed = pressed

class MouseHandler:
    def __enter__(self):
        sys.stdout.write("\x1b[?1000h\x1b[?1006h") # Enable mouse
        sys.stdout.flush()
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        sys.stdout.write("\x1b[?1000l\x1b[?1006l") # Disable mouse
        sys.stdout.flush()
        return False
    def parse(self, data: str):
        match = re.match(r'␛\[<(\d+);(\d+);(\d+)([mM])', data)
        if match:
            btn, x, y, event_type = match.groups()
            btn = int(btn)
            x = int(x)
            y = int(y)
            down = event_type == "M"

            return MouseData(btn, x, y, down)
        return None