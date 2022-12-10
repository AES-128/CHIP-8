import curses
from time import sleep

def get_diff(d1, d2):
	return (k for k in d1.keys() | d2.keys() if d2.get(k) != d1.get(k))

screen = curses.initscr()
screen.nodelay(1) # getch becayse non-blocking
curses.curs_set(0)
curses.noecho()


# 1 2 3 C -> 1 2 3 4
# 4 5 6 D -> Q W E R
# 7 8 9 E -> A S D F
# A 0 B F -> \ Z X C

keypad_map = {ord(char): idx for idx, char in enumerate("1234QWERASDF\\ZXC")}

def get_key():
	try:
		return keypad_map.get(screen.getch())
	except curses.error:
		return None

def draw_to_screen(prev, video_memory):
	for y, x in get_diff(prev, video_memory):
		c = "██" if video_memory[(y, x)] else "  "
		screen.addstr(y, x * 2, c)

	screen.refresh()

def kill_screen():
	curses.curs_set(1)
	curses.nocbreak()
	screen.keypad(0)
	curses.echo()
	curses.endwin()
