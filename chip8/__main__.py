from cpu import CPU
from chip_io import draw_to_screen, kill_screen, get_key
import sys

def get_diff(d1, d2):
	return list(k for k in d1.keys() | d2.keys() if d2.get(k) != d1.get(k))

if len(sys.argv) != 2:
	print("Usage: python3 chip8 <rom>")
	exit()

cpu = CPU()

cpu.load_rom(sys.argv[1])

try:
	while True:
		cpu.FDE()
		draw_to_screen(cpu.prev_video_memory, cpu.video_memory)
		cpu.current_key = get_key() # high cpu usage, need to somehow add a delay (so may need to be on a seperate thread)
except KeyboardInterrupt:
	pass

kill_screen()