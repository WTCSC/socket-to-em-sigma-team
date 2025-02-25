import sys,os
import curses

def draw_menu(stdscr):
    # ASCII value for key pressed
    k = 0

    cursor_x = 0
    cursor_y = 0

    # Clear and refresh
    stdscr.clear()
    stdscr.refresh()

    while k != KeyboardInterrupt:
        # Begin screen initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = len("Message: ")
        cursor_y = (height - 1)

        chatbox_title = "Message: "[:height - 1]

        start_x_chatbox_title = int(0)
        start_y = int(height - 1)

        stdscr.addstr(start_y, start_x_chatbox_title, chatbox_title, curses.COLOR_BLACK)

        stdscr.refresh()

        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()