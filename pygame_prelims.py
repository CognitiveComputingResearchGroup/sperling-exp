# Needed to use any and all python resources.
import pygame
import sys

import experiments
from experiments.pygame import *

# Defines common colors
background_one = (0, 0, 0)  # black
background_two = (255, 255, 255)  # white
# red: (255, 0, 0)
# purple: (255, 0, 255)
# light salmon: (255, 160, 122)

# Initializes all pygame functionality.
pygame.init()

# Creates the window and puts a Surface into "screen".
screen = pygame.display.set_mode((1024, 768))
screen_dims = Dimensions(*pygame.display.get_surface().get_size())

# Used for timing within the program.
clock = pygame.time.Clock()

# Used for timed events.
milli_timer = 0

font = pygame.font.SysFont("courier", size=72)

crosshairs = CrossHairs((screen_dims.width // 2, screen_dims.height // 2), 100, (255, 255, 255))
letter = Character('A', (screen_dims.width // 2, screen_dims.height // 2), font, (255, 100, 255))

HORIZ_PADDING = 200
VERT_PADDING = 200

spec = experiments.GridSpec(n_rows=3, n_columns=4, charset_id=experiments.CHARSET_CONSONANTS)

grid_dims = Dimensions(screen_dims.width - 2 * HORIZ_PADDING,
                       screen_dims.height - 2 * VERT_PADDING)

grid_pos = (
    (screen_dims.width - grid_dims.width) / 2,
    (screen_dims.height - grid_dims.height) / 2
)
char_grid = CharacterGrid(grid_spec=spec,
                          pos=grid_pos,
                          font=font,
                          width=grid_dims.width,
                          height=grid_dims.height,
                          horiz_margin=100,
                          vert_margin=100
                          )

all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(crosshairs)
# all_sprites_list.add(letter)

# Main loop of the program.
while True:
    for event in pygame.event.get():
        # Check for exit conditions
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        # elif event.type == pygame.KEYDOWN:
        #     player.MoveKeyDown(event.key)
        # elif event.type == pygame.KEYUP:
        #     player.MoveKeyUp(event.key)

    # Add the amount of milliseconds passed
    # from the last frame.
    milli_timer += clock.get_time()

    screen.fill(background_one)

    char_grid.randomize()
    char_grid.update()
    char_grid.draw(screen)

    # for sprite in char_grid.sprite_group.sprites():
    #     screen.blit(sprite.image, sprite.grid_pos)

    all_sprites_list.update()
    all_sprites_list.draw(screen)

    # Display all images drawn.
    # This removes flickering images and makes it easier for the processor.
    pygame.display.flip()

    # Defines the frame rate. The number is number of frames per second.
    clock.tick(1)
