import nullui as nui
import sys
import os
from specials import make_printable
from cmp import CMPImage
import cooltext as ct
import time
firsttime = True
running = True
with nui.Screen() as scr:
    with nui.MouseHandler() as mouse:
        size = os.get_terminal_size()
        def settings_button_onclick(b: nui.Button, x: int, y: int) -> None:
            pass
        def exit_button_onclick(b: nui.Button, x: int, y: int) -> None:
            global running
            running = False
        ((((scr + (cmdbuf_label := nui.Label(1, size.lines, size.columns, 1, ""))) + (desktop_box := nui.Box(1, 2, (size.columns - 2), (size.lines - 4), True, nui.Screen.rounded_box))) + (quickbar_buttons := nui.ButtonGroup((size.columns - 10), 3, nui.Screen.connected_sep, ((+(settings_button := nui.Button(0, 0, 3, 1, " 󰖷 ", nui.Screen.rounded_box, settings_button_onclick))) + (exit_button := nui.Button(0, 0, 3, 1, " 󰖭 ", nui.Screen.rounded_box, exit_button_onclick)))))) + (mousecur := nui.Label(1, 1, 1, 1, "🮰")))
        cmdbuf = ""
        max_cmdbuf = 16
        while running:
            cmdvalid = False
            scr.reset_buf()
            if (not firsttime):
                char = make_printable(sys.stdin.read(1))
                cmdbuf = (cmdbuf + char)[:max_cmdbuf]
                cmdmouse = scr.handle_mouse(cmdbuf, mouse)
                if cmdmouse:
                    mousecur.x, mousecur.y = cmdmouse.x, cmdmouse.y
                    cmdbuf = ""
                elif (cmdbuf == "exit"):
                    cmdbuf = ""
                    running = False
                elif (char == "␍"):
                    cmdbuf = ""
                elif (char == "␡"):
                    cmdbuf = cmdbuf[:((-2) if (cmdbuf[(-1)] == "␡") else (-1))]
            cmdbuf_label.text = ((cmdbuf + ("▏" if (len(cmdbuf) < max_cmdbuf) else "█")).ljust((max_cmdbuf + 1), " ") + ct.sevenseg((max_cmdbuf - len(cmdbuf))).rjust(2, " "))
            scr.show()
            firsttime = False