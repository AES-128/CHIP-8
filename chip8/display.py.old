def get_diff(d1, d2):
	return (k for k in d1.keys() | d2.keys() if d2.get(k) != d1.get(k))

def draw_to_screen(prev, video_memory):
	for y, x in get_diff(prev, video_memory):
		c = "##" if video_memory[(y, x)] else "  "
		print(f"\033[{y};{x * 2}f{c}")

	print("\033[H")
