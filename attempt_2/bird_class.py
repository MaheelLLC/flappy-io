import pygame
import os

# store images of bird
image_1 = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird1.png')))
image_2 = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird2.png')))
image_3 = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird3.png')))

BIRD_IMAGES = [image_1, image_2, image_3]

class Bird:
    # shorter name to store bird images
    IMAGES = BIRD_IMAGES
    # max tilt (the most the bird image will angle up)
    MAX_ROTATION = 25
    # rotational velocity (for fluid downward tilting)
    ROTATIONAL_VELOCITY = 20
    # how long we're gonna show each bird wing image (wing animation time)
    ANIMATION_TIME = 5
    # gravity constant
    GRAVITY = 3

    def __init__(self, x, y):
        # horizontal position, stays constant actually
        self.x = x
        # vertical position
        self.y = y
        # image tilt for animation (The bird's angle)
        self.angle = 0
        # store frame count for movement and animation
        self.frame_count = 0
        # current velocity
        self.velocity = 0
        # starting jump height (at what height did the bird's jump start)
        self.jump_height = self.y
        # stores frame count to determine which wing position to show
        self.image_count = 0
        # current image of bird
        self.image = self.IMAGES[0]
        # mask of bird (an array of 1s and 0s depicting non-transparent pixels)
        self.bird_mask = pygame.mask.from_surface(self.image)


    def jump(self):
        # give it an upwards velocity
        self.velocity = -10.5
        # use frame count to store when we just jumped (now)
        self.frame_count = 0
        # jump_height is useful now, track where the bird just jumped from
        self.jump_height = self.y

    def move(self):
        # move to the next frame
        self.frame_count += 1
        # calculate displacement using its corresponding phyics formula
        # acceleration value comes from trial and error
        # min is to ensure that the bird doesn't go past terminal velocity
        displacement = min(self.velocity * self.frame_count + 0.5 * self.GRAVITY * self.frame_count**2, 16)
        # if we're moving upward
        if displacement < 0:
            # finetune the jump
            displacement -= 2
        # make the bird actually move using displacement
        self.y = self.y + displacement

        # if the bird is going up (the or case is to delay the downward tilt)
        if displacement < 0 or self.y < self.jump_height - 5:
            # if the bird isn't completely tilted up
            if self.angle < self.MAX_ROTATION:
                # tilt the bird upwards
                self.angle = self.MAX_ROTATION
        else:
            # if the bird isn't looking straight down
            if self.angle > -90:
                # increase its downward angle so the bird looks like it's
                # nosediving
                self.angle -= self.ROTATIONAL_VELOCITY
    
    def draw(self, window):
        # move into the next frame
        self.image_count += 1
        
        # every wing animation should last 5 frames. We can find out if it's
        # been 5 frames using image_count. For the wings to flap up and down, 
        # we need 4 wing states [up, middle, down, middle]. We repeat this
        # list for proper animation.
        index = (self.image_count // self.ANIMATION_TIME) % 4
        # list of 4 wing states
        wing_states = [0, 1, 2, 1]
        # grab the current wing state, that is the image we'll show of the bird
        self.image = self.IMAGES[wing_states[index]]

        # restart the frame count of we're repeating the wing animation cycle
        if self.image_count == self.ANIMATION_TIME * 4:
            self.image_count = 0
        
        # when our bird is falling
        if self.angle <= -80:
            # we don't want the wings to flap
            self.image = self.IMAGES[1]
            # set the frame count to prepare for the next animation
            self.image_count = self.ANIMATION_TIME*2

        # using given angle, rotate the image around its topleft corner
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        # move both the rectangle and image back to its original center
        # (the center before the rotation) to achieve a rotation around its
        # center instead of topleft
        new_rectangle = rotated_image.get_rect(center=self.image.get_rect(topleft = (self.x, self.y)).center)
        # draw the properly rotated image
        window.blit(rotated_image, new_rectangle.topleft)
    
    def get_mask(self):
        # get the bird's mask to enforce pixel perfect collision
        return self.bird_mask
    
