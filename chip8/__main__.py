from cpu import CPU
from display import draw_to_screen, kill_screen
import sys

if len(sys.argv) != 2:
	print("Usage: python3 chip8 <rom>")
	exit()

cpu = CPU()

cpu.load_rom(sys.argv[1])

try:
	while True:
		cpu.FDE()
		draw_to_screen(cpu.prev_video_memory, cpu.video_memory)
except:
	kill_screen()
