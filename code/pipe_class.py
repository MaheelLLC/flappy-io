import pygame
import os
import random

# load the pipe image from files
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))

class Pipe:
    # the gap between the two pipes
    PIPE_GAP = 200
    # how fast the pipes move to the left
    VELOCITY = 5
    # the highest the pipes can be
    MIN_PIPE_HEIGHT = 50
    # the lowest the pipes can be
    MAX_PIPE_HEIGHT = 500

    def __init__(self, x):
        # horizontal position
        self.x = x
        # store the bottom end of the top pipe
        self.top_pipe_end = 0
        # store the top end of the top pipe (where we draw the pipe from)
        self.top_pipe_start = 0
        # bottom pipe draw location (top end of bottom pipe)
        self.bottom_pipe_start = 0

        # the top pipe image
        self.top_pipe_image = pygame.transform.flip(PIPE_IMAGE, False, True)
        # bottom pipe image
        self.bottom_pipe_image = PIPE_IMAGE

        # a conditional to determine if the bird pipe passed the pipes
        self.passed = False

        # let's initialize the locations of the pipe pair
        self.set_height()

        # compute the mask of the top pipe
        self.top_pipe_mask = pygame.mask.from_surface(self.top_pipe_image)
        # the mask of the bottom pipe
        self.bottom_pipe_mask = pygame.mask.from_surface(self.bottom_pipe_image)

    def set_height(self):
        # pick a random location for the top pipe
        self.top_pipe_end = random.randrange(self.MIN_PIPE_HEIGHT, self.MAX_PIPE_HEIGHT)
        # calculate where we should draw the top pipe using the pipe's height
        # and its randomized bottom end location
        self.top_pipe_start = self.top_pipe_end - self.top_pipe_image.get_height()
        # draw the bottom pipe a gap below the top pipe
        self.bottom_pipe_start = self.top_pipe_end + self.PIPE_GAP

    def move(self):
        # move the pipes horizontally, "velocity" pixels
        self.x -= self.VELOCITY

    def draw(self, window):
        # draw the top pipe at its proper location
        window.blit(self.top_pipe_image, (self.x, self.top_pipe_start))
        # draw the bottom pipe at its proper location
        window.blit(self.bottom_pipe_image, (self.x, self.bottom_pipe_start))

    def collide(self, bird):
        # grab the manhattan distance between bird and top pipe
        top_pipe_offset = (self.x - bird.x, self.top_pipe_start - round(bird.y))
        # the manhattan distance between bird and bottom pipe
        bottom_pipe_offset = (self.x - bird.x, self.bottom_pipe_start - round(bird.y))

        # grab the bird's mask
        bird_mask = bird.get_mask()
        # collision points between visible pixels of bird and top pipe
        # calculated using mask overlap
        top_pipe_points = bird_mask.overlap(self.top_pipe_mask, top_pipe_offset)
        # collision points between bird and bottom pipe
        bottom_pipe_points = bird_mask.overlap(self.bottom_pipe_mask, bottom_pipe_offset)

        # if collision points exist for either pipe
        if bottom_pipe_points or top_pipe_points:
            # notify the collision occurred
            return True
        # no collision has occurred
        return False