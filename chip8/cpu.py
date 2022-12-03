# Memory Map:
# +---------------+= 0xFFF (4095) End of Chip-8 RAM
# |               |
# |               |
# | 0x200 to 0xFFF|
# |     Chip-8    |
# | Program / Data|
# |     Space     |
# |               |
# ~~~~~~~~~~~~~~~~~
# |               |
# +---------------+= 0x200 (512) Start of most Chip-8 programs
# | 0x000 to 0x1FF|
# | Reserved for  |
# |  interpreter  |
# +---------------+= 0x000 (0) Start of Chip-8 RAM


class CPU:
	def __init__(self):
		self.registers = [0] * 16 # Sixteen 8-bit general purpose registers from [R0 to RF] (RF is a flag register)
		self.index = 0 # 16-bit
		self.pc = 0 # 16-bit
		self.sp = 0 # 16-bit
		self.memory = [0] * 4096
		self.stack = []

	def load_rom(self, rom_path, start_address = 0x200): # ROM is loaded at 0x200 (most of the time)
		with open(rom_path, "rb") as rom_bytes:
			for idx, byte in enumerate(rom_bytes.read()):
				self.memory[start_address + idx] = byte