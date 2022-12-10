from collections import defaultdict as dd
from random import randint

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

DEBUG = True

if DEBUG:
	log_file = open("log.out", "w+")

FONT_START_ADDR = 0x50
font = [
	0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
	0x20, 0x60, 0x20, 0x20, 0x70, # 1
	0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
	0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
	0x90, 0x90, 0xF0, 0x10, 0x10, # 4
	0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
	0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
	0xF0, 0x10, 0x20, 0x40, 0x40, # 7
	0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
	0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
	0xF0, 0x90, 0xF0, 0x90, 0x90, # A
	0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
	0xF0, 0x80, 0x80, 0x80, 0xF0, # C
	0xE0, 0x90, 0x90, 0x90, 0xE0, # D
	0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
	0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

class CPU:
	def __init__(self, start_address = 0x200):
		self.registers = [0] * 16 # Sixteen 8-bit general purpose registers from [R0 to RF] (RF is a flag register)
		self.index = 0 # 16-bit
		self.pc = start_address # 16-bit
		self.delay_timer = 0
		self.sound_timer = 0
		self.memory = [0] * 4096
		self.stack = []
		self.current_opcode = 0
		self.video_memory = dd(lambda: 0)
		self.prev_video_memory = dd(lambda: 0)
		self.table = {
			0xE0	:	self._00E0_CLEAR,
			0xEE	:	self._00EE_RETURN,
			0x1		:	self._1NNN_JUMP,
			0x2		:	self._2NNN_CALL,
			0x3		:	self._3XKK_SKIP,
			0x4		:	self._4XKK_SKIP,
			0x5		:	self._5XY0_SKIP,
			0x6		:	self._6XKK_LOAD,
			0x7		:	self._7XKK_ADD,
			0x8		:	self._8XYN_ALU,
			0x9		:	self._9XY0_SKIP,
			0xA		:	self._ANNN_LOAD,
			0xB		:	self._BNNN_JUMP,
			0xC		:	self._CXKK_RAND,
			0xD		:	self._DXYN_DRAW,
			0xE		:	self._EXKK_KEY,
			0xF		:	self._FXKK_TIMER,
			0x1E	:	self._FX1E_ADD,
			0x29	:	self._FX29_LD,
			0x55	:	self._FX55_LD,
			0x33	:	self._FX33_BCD,
			0x65	:	self._FX65_LD,
		}
		self.current_key = None
		self.load_fonts()

	def load_fonts(self):
		for idx in range(len(font)):
			self.memory[FONT_START_ADDR + idx] = font[idx]

	def get_nth_bit(self, n):
		return (self.current_opcode >> 4 * (4 - n)) & 0xF

	def _00E0_CLEAR(self):
		self.video_memory = dd(lambda: 0)

	def _00EE_RETURN(self):
		self.pc = self.stack.pop()

	def _1NNN_JUMP(self):
		self.pc = self.current_opcode & 0xFFF

	def _2NNN_CALL(self):
		self.stack.append(self.pc)
		self.pc = self.current_opcode & 0xFFF

	def _3XKK_SKIP(self): # Skip if registers[x] == kk
		x = self.get_nth_bit(2)
	
		if self.registers[x] == self.current_opcode & 0xFF:
			self.pc += 2

	def _4XKK_SKIP(self): # Skip if registers[x] != kk
		x = self.get_nth_bit(2)
	
		if self.registers[x] != self.current_opcode & 0xFF:
			self.pc += 2

	def _5XY0_SKIP(self): # Skip if registers[x] == registers[y]
		x = self.get_nth_bit(2)
		y = self.get_nth_bit(3)

		if self.registers[x] == self.registers[y]:
			self.pc += 2

	def _6XKK_LOAD(self):
		x = self.get_nth_bit(2)
		self.registers[x] = self.current_opcode & 0xFF

	def _7XKK_ADD(self):
		x = self.get_nth_bit(2)
		self.registers[x] += self.current_opcode & 0xFF
		self.registers[x] %= 256 # emulate overflow (registers are only 8 bits)

	def _8XYN_ALU(self):
		x = self.get_nth_bit(2)
		y = self.get_nth_bit(3)
		n = self.get_nth_bit(4)

		if n == 0:		self.registers[x] = self.registers[y]
		elif n == 1:	self.registers[x] |= self.registers[y]
		elif n == 2:	self.registers[x] &= self.registers[y]
		elif n == 3:	self.registers[x] ^= self.registers[y]
		elif n == 4:	# Another ADD instruction, but it affects the flag register
			self.registers[x] += self.registers[y]
			carry, self.registers[x] = divmod(self.registers[x], 256)
			self.registers[0xF] = int(bool(carry)) # Returns 0 if there is no overflow, else it returns 1
		elif n == 5:
			self.registers[0xF] = int(self.registers[x] > self.registers[y])
			self.registers[x] -= self.registers[y]
			self.registers[x] %= 256
		elif n == 6:
			self.registers[x] = self.registers[y] # for different programs, this line may need to remain in or out
			self.registers[0xF] = self.registers[x] & 1
			self.registers[x] >>= 1
		elif n == 7:
			self.registers[0xF] = int(self.registers[y] > self.registers[x])
			self.registers[x] = self.registers[y] - self.registers[x]
			self.registers[x] %= 256
		elif n == 0xE:
			self.registers[x] = self.registers[y] # for different programs, this line may need to remain in or out
			self.registers[0xF] = self.registers[x] & 0b1000000000000000
			self.registers[x] <<= 1

	def _9XY0_SKIP(self): # Skip if registers[x] != registers[y]
		x = self.get_nth_bit(2)
		y = self.get_nth_bit(3)

		if self.registers[x] != self.registers[y]:
			self.pc += 2

	def _ANNN_LOAD(self):
		self.index = self.current_opcode & 0xFFF

	def _BNNN_JUMP(self):
		self.pc = self.registers[0] + self.current_opcode & 0xFFF

	def _CXKK_RAND(self):
		x = self.get_nth_bit(2)
		self.registers[x] = randint(0, 256) & self.current_opcode & 0xFF

	def _DXYN_DRAW(self):
		# Sprites are composed of rows of bytes
		self.prev_video_memory = self.video_memory.copy()

		x = self.get_nth_bit(2)
		y = self.get_nth_bit(3)
		n = self.get_nth_bit(4)

		dx = self.registers[x] # take modulus so that sprite can wrap across edge
		dy = self.registers[y]
		self.registers[0xF] = 0

		for row in range(n):
			sprite_byte = self.memory[self.index + row]

			for column in range(8):
				sprite_pixel = sprite_byte & (0x80 >> column)
				screen_pixel = self.video_memory[(dy + row, dx + column)]
				self.video_memory[(dy + row, dx + column)] = sprite_pixel
				self.registers[0xF] = screen_pixel # collision

	def _EXKK_KEY(self):
		x = self.get_nth_bit(2)
		kk = self.current_opcode & 0xFF
		cond = 1 if kk == 0x9E else 0 # oof

		if cond * (self.current_key == self.registers[x]):
			pc += 2

	def _FXKK_TIMER(self):
		x = self.get_nth_bit(2)
		kk = self.current_opcode & 0xFF

		if kk == 0x07:
			self.registers[x] = self.delay_timer
		elif kk == 0x15:
			self.delay_timer = self.registers[x]
		elif kk == 0x18:
			self.sound_timer = self.registers[x]

	def _FX1E_ADD(self):
		self.index += self.registers[self.get_nth_bit(2)]
		
	def _FX33_BCD(self):
		x = self.get_nth_bit(2)
		bin_val = self.registers[x]

		for idx in range(2, -1, -1):
			bin_val, digit = divmod(bin_val, 10)
			self.memory[self.index + idx] = digit

	def _FX55_LD(self):
		x = self.get_nth_bit(2)

		for idx in range(x + 1):
			self.memory[self.index + idx] = self.registers[idx]

	def _FX65_LD(self):
		x = self.get_nth_bit(2)

		for idx in range(x + 1):
			self.registers[idx] = self.memory[self.index + idx]

	def load_rom(self, rom_path): # ROM is loaded at 0x200 (most of the time)
		with open(rom_path, "rb") as rom_bytes:
			for idx, byte in enumerate(rom_bytes.read()):
				self.memory[self.pc + idx] = byte

	def get_func(self):
		if self.current_opcode in (0xE0, 0xEE):
			return self.current_opcode

		first_byte = self.current_opcode >> 12

		if first_byte in [*range(1, 0xE)]:
			return first_byte

		else:
			return self.current_opcode & 0xFF
	
	def _FX29_LD(self):
		x = self.get_nth_bit(2)
		self.index = FONT_START_ADDR + 5 * self.registers[x]

	def FDE(self):
		self.current_opcode = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]
		self.pc += 2
		instruction = self.table.get(self.get_func())
		if self.delay_timer: self.delay_timer -= 1
		if self.sound_timer: self.sound_timer -= 1

		if instruction:
			instruction()
		elif DEBUG:
			log_file.write(f"Instruction {hex(self.current_opcode)} not implemented\n")
