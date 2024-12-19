import pygame
import os

FLOOR_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "floor.png")))

class Floor:
    # the floors must move so the bird looks like it's moving
    VELOCITY = 5
    # get the floor width using the image size
    WIDTH = FLOOR_IMAGE.get_width()
    # now grab the actual image
    IMAGE = FLOOR_IMAGE

    def __init__(self, y):
        # vertical position of the floor
        self.y = y
        # horizontal position of the first floor segment
        self.floor1_x = 0
        # horizontal position of the second floor segment
        self.floor2_x = self.WIDTH

    def move(self):
        # make both floor segments move to the left
        self.floor1_x -= self.VELOCITY
        self.floor2_x -= self.VELOCITY

        # if floor1 reached the end of the screen
        if self.floor1_x + self.WIDTH < 0:
            # move it behind floor2
            self.floor1_x = self.floor2_x + self.WIDTH
        # if floor2 reaches the end of the screen
        if self.floor2_x + self.WIDTH < 0:
            # move it behind floor1
            self.floor2_x = self.floor1_x + self.WIDTH
    
    def draw(self, window):
        # draw floor1
        window.blit(self.IMAGE, (self.floor1_x, self.y))
        # draw floor2
        window.blit(self.IMAGE, (self.floor2_x, self.y))