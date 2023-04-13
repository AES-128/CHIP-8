from cpu import CPU
from chip_io import draw_to_screen, update_keypad_state, tick_clock
import sys
from random import random

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

		if (diff := get_diff(cpu.prev_video_memory, cpu.video_memory)):
			draw_to_screen(cpu.video_memory, diff)
			cpu.prev_video_memory = cpu.video_memory.copy()
		
		tick_clock()

except KeyboardInterrupt:
	pass
