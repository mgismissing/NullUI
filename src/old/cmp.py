from specials import make_printable

class CMPImageFlags:
    def __init__(self, is_colored: bool, is_utf16: bool, is_utf32: bool, is_transparent: bool, transparent_char: str | None):
        self.is_colored = is_colored
        self.is_utf16 = is_utf16
        self.is_utf32 = is_utf32
        self.is_transparent = is_transparent
        self.transparent_char = transparent_char
    def from_bytes(b: bytes):
        return CMPImageFlags(
            b[0] & 0x01,
            b[0] & 0x02,
            b[0] & 0x04,
            b[0] & 0x08,
            chr(
                int.from_bytes(b[2:6], byteorder="big") if (b[0] & 0x04)
                else (int.from_bytes(b[2:4], byteorder="big") if (b[0] & 0x02)
                else b[2])
            ) if (b[0] & 0x08) else None
        )

class CMPImage:
    def __init__(self, filename: str):
        with open(filename, "rb") as f:
            data = f.read()
            if not data[0:2] == b"CM": return None
            self.w, self.h = int.from_bytes(data[2:4], byteorder="big"), int.from_bytes(data[4:6], byteorder="big")
            self.flags = CMPImageFlags.from_bytes(data[6:15])
            if not ((not self.flags.is_colored) and (self.flags.is_utf16 or self.flags.is_utf32)):
                raise NotImplementedError()
            
            self.data: list[tuple[int, int, str]] | list[tuple[str]] = []
            if self.flags.is_colored:
                if self.flags.is_utf32:
                    pass
                elif self.flags.is_utf16:
                    pass
                else:
                    pass
            else:
                if self.flags.is_utf32:
                    buf = data[16:(self.w*self.h*4)+16]
                    for chunk in [ buf[i:i+4] for i in range(0, len(buf), 4) ]:
                        self.data.append((chr(int.from_bytes(chunk, byteorder="big"))),)
                elif self.flags.is_utf16:
                    buf = data[16:(self.w*self.h*2)+16]
                    for chunk in [ buf[i:i+2] for i in range(0, len(buf), 2) ]:
                        self.data.append((chr(int.from_bytes(chunk, byteorder="big"))),)
                else:
                    pass
                if self.flags.is_transparent:
                    for i, c in enumerate(self.data):
                        self.data[i] = (("\x00" if c[0] == self.flags.transparent_char else c[0]),)

    def read(self):
        s = ""
        if self.flags.is_colored:
            pass
        else:
            for i, c in enumerate(self.data):
                if self.flags.is_transparent:
                    if c[0] == self.flags.transparent_char:
                        s += c[0]
                    else:
                        s += make_printable(c[0])
                else:
                    s += make_printable(c[0])
                if i % self.w == self.w-1:
                    s += "\n"
        return s[:-1]
