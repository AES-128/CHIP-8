from cpu import CPU
import sys

if len(sys.argv) != 2:
	print("Usage: python3 chip8 <rom>")
	exit()

cpu = CPU()

cpu.load_rom(sys.argv[1])
while True:
	print("\033[?25l") # hide cursor
	cpu.FDE()
