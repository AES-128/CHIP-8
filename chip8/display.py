import curses


def get_diff(d1, d2):
	return (k for k in d1.keys() | d2.keys() if d2.get(k) != d1.get(k))

screen = curses.initscr()
curses.curs_set(0)

def draw_to_screen(prev, video_memory):
	for y, x in get_diff(prev, video_memory):
		c = "@@" if video_memory[(y, x)] else "  "
		screen.addstr(y, x * 2, c)
		
	screen.refresh()

def kill_screen():
	curses.curs_set(1)
	curses.nocbreak()
	screen.keypad(0)
	curses.echo()
	curses.endwin()
