import pygame

pygame.init()
clock = pygame.time.Clock()

scale = 15
width, height = 64 * scale, 32 * scale
screen = pygame.display.set_mode((width, height))

keypad_map = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
}

def update_keypad_state(keypad_state):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key in keypad_map:
            key_index = keypad_map[event.key]
            keypad_state[key_index] = True
        elif event.type == pygame.KEYUP and event.key in keypad_map:
            key_index = keypad_map[event.key]
            keypad_state[key_index] = False


def draw_to_screen(video_memory, diff):
	for y, x in diff:
		if video_memory[(y, x)]:
			pygame.draw.rect(screen, (255, 255, 255), (x * scale, y * scale, scale, scale))
		else:
			pygame.draw.rect(screen, (0, 0, 0), (x * scale, y * scale, scale, scale))

	pygame.display.flip()


def tick_clock():
    clock.tick(400)