import pygame
import neat
import os
import random

# initialize pygame
pygame.init()

# initialize fonts
pygame.font.init()

# game screen size
WINDOW_WIDTH = 550
WINDOW_HEIGHT = 800

# generation variable
GENERATION = 0

# load bird images
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))), \
               pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))), \
               pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]
# load pipe image
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))
# load floor image
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))
# load background image
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bg.png")))
# load score and text font
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    # shorter name to store bird images
    IMAGES = BIRD_IMAGES
    # when the bird jumps, its body must tilt up by 25 degrees
    # when it is falling, it must tilt down by 25 degrees
    MAX_ROTATION = 25
    # how much we're gonna rotate on each frame
    ROTATION_VELOCITY = 20
    # how long we're gonna show each bird animation
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # horizontal position
        self.x = x
        # vertical position
        self.y = y
        # how much the image is actually tilted
        self.tilt = 0
        # helps deal with the physics of our bird (acceleration depends on time)
        self.tick_count = 0
        # store velocity
        self.velocity = 0
        # second variable to store vertical position
        self.height = self.y
        # so we know which image we are currently showing, for good animation
        self.image_count = 0
        # actual current image
        self.image = self.IMAGES[0]

    def jump(self):
        # since pygame starts 0,0 at top left of screen, to go upwards, we need 
        # a negative velocity.
        self.velocity = -10.5
        # keeps track of when we last jumped
        self.tick_count = 0
        # keeps track of where the bird jumped from (pre jump position)
        self.height = self.y

    # we call this every single frame to move our bird
    def move(self):
        # sounds like every action function just changes the velocity while move 
        # performs the actual movement
        # let's us know that a frame happened and tick went by
        self.tick_count += 1
        # calculate displacement (how many pixels we have moved up or down this 
        # frame - in the bird's case, it's only either up or down)
        # this uses the physics formula for displacement
        # tick_count represents time in this case
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count**2
        # when we jump, displacement = -10.5 * 1 + 1.5 = -9 (9 pixels upward)
        # this formula allows us to mathematically implement an arc for our bird's jump
        # terminal velocity check, if the bird has reached terminal velocity (16 pixels down)
        if displacement >= 16:
            # stop accelering by making displacement be 16 regardless
            displacement = 16
        # if we're moving upwards,
        if displacement < 0:
            # let's move upwards a little more, finetunes the jump/movement
            displacement -= 2
        # change the bird's vertical position
        self.y = self.y + displacement
        # as long we're either going up or we're at most 50 pixels below where 
        # we jumped from
        if displacement < 0 or self.y < self.height - 5:
            # if the bird isn't (completely) tilted up
            if self.tilt < self.MAX_ROTATION:
                # tilt the bird up by 25 degrees
                self.tilt = self.MAX_ROTATION
        else:
            # if the bird isn't looking straight down
            if self.tilt > -90:
                # slowly tilt it downwards to make the nosedive look fluid
                self.tilt -= self.ROTATION_VELOCITY
    
    # let's actually draw the bird for the game
    def draw(self, window):
        # we need to keep track of how many ticks/frames we've shown a current image for
        self.image_count += 1

        # this logic is what gets us the flapping wings on the bird
        # the 3 images in self.IMAGES are the different wing positions
        # every 5 frames we move the wing to the next position
        # checking what image I should show based on the current image count
        # if image count is less than 5
        if self.image_count < self.ANIMATION_TIME:
            # display the first flappy bird image (wings are up)
            self.image = self.IMAGES[0]
        # if it gets larger than 5 but not double, less than 10
        elif self.image_count < self.ANIMATION_TIME*2:
            # display the second image (wings are middle)
            self.image = self.IMAGES[1]
        # if frame count is less than 15
        elif self.image_count < self.ANIMATION_TIME*3:
            # display the wings downward
            self.image = self.IMAGES[2]
        # now start moving the wings back up
        elif self.image_count < self.ANIMATION_TIME*4:
            self.image = self.IMAGES[1]
        # restart the animation
        elif self.image_count == self.ANIMATION_TIME*4 + 1:
            self.image = self.IMAGES[0]
            self.image_count = 0
        # Now the bird's wings are flapping up and down. The code below is an
        # alternative
        """
        index = (self.image_count // self.ANIMATION_TIME) % 4
        self.image = self.IMAGES[[0, 1, 2, 1][index]]

        if self.image_count == self.ANIMATION_TIME * 4:
            self.image_count = 0
        """

        # when our bird is going downwards (falling), we don't want the wings to
        # flap
        if self.tilt <= -80:
            self.image = self.IMAGES[1]
            # we are in this animation timeframe if our wings are level
            self.image_count = self.ANIMATION_TIME*2

        # this is how you rotate an image around its center in pygame
        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        # the previous line would rotate the image with respect to its top left
        # corner, here's what change the axis of rotation to the center
        new_rectangle = rotated_image.get_rect(center=self.image.get_rect(topleft = (self.x, self.y)).center)
        window.blit(rotated_image, new_rectangle.topleft)

    # we use this function for when our bird experiences a collision
    def get_mask(self):
        return pygame.mask.from_surface(self.image)
    
# this abstraction will actually represent both the top and bottom pipes
class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bottom = 0
        # we're getting the image of the top pipe (which is upside down)
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        # we're also getting the image of the bottom pipe
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False
        self.set_height()

    def set_height(self):
        # the top pipe is going to be at a random location vertically
        self.height = random.randrange(50, 450)
        # to set the top pipe to its random location, we have to use the 
        # top-left corner of the image. To figure out where to draw the pipe
        # on the screen, we need to find out the height of the image and 
        # subtract it on the desired location
        self.top = self.height - self.PIPE_TOP.get_height()
        # let's draw the bottom pipe to be a gap below the top pipe
        self.bottom = self.height + self.GAP

    def move(self):
        # change the x position based on the velocity that the pipe should move
        # each frame.
        self.x -= self.VELOCITY

    def draw(self, window):
        # draw the top pipe at its proper location
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    """
    for collision detection, all objects in a game are placed inside boxes
    (rectangles). A mask is an array of where are all the pixes inside of this
    box. Since the bird is more circular than a box, we need to use a mask to
    see if the bird is actually colliding with a pipe. Since the bird image has
    a transparent background and the actual bird image, pygame can tell whether
    a pixel is transparent or actually part of the bird image. Pygame will create
    a 2D array representation of the png image. We can represent both the bird
    and pipe as 2D pixel arrays and see which pixels collide with other pixels. 
    This can determine whether we had pixel perfect collision (The bird ACTUALLY
    collided with the pipe.
    """
    def collide(self, bird):
        # actually, mask returns a image-sized 2D array of 0s and 1s depending 
        # on whether the pixel at that array location is transparent or not.
        # if it is transparent, the array value is 0. Otherwise, it is 1.
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # offset: how far away these masks are from each other.
        # let's see how far the top pipe is from the bird,
        # since the bird's vertical position can be a decimal, we need to round it
        top_pipe_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_pipe_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # let's find their points of collision with the bird (bottom pipe first)
        # if the bird and bottom pipe don't collide, then this overlap will
        # return None
        # actually, overlap checks if any 1 value from one mask overlaps a 1
        # frmo another mask. The first argument is of course the other mask 
        # we're potentially colliding with. The second argument offset tells
        # pygame where to align mask2 relative to mask1. If any two 1s overlap
        # a collision is detected, a tuple is returned.
        bottom_pipe_point = bird_mask.overlap(bottom_pipe_mask, bottom_pipe_offset)
        top_pipe_point = bird_mask.overlap(top_pipe_mask, top_pipe_offset)
        
        # check if either of these collision points exist
        if bottom_pipe_point or top_pipe_point:
            return True

        return False

# this class represents the floor that the bird can hit
# we need a class floor since the floor is going to be "moving" to make the bird
# look like its moving  
class Base:
    VELOCITY = 5
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # to make the floor "move". We need to draw 2 bases (floors). They'll be
        # following each other. For example, base_2 will follow base_1 until
        # base_1 hits the end of the screen. Then, base_1 will teleport behind
        # base_2 Then, base_1 will follow base_2 until base_2 hits the end of 
        # the screen, and repeats the cycle
        # this gives the illusion that we're moving 1 continuous image
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        # if base_1 reached the end of the screen (completely gets off the screen)
        if self.x1 + self.WIDTH < 0:
            # move it behind base_2
            self.x1 = self.x2 + self.WIDTH
        # if base_2 reaches the end of the screen
        if self.x2 + self.WIDTH < 0:
            # move it behind base_1
            self.x2 = self.x1 + self.WIDTH
        
    def draw(self, window):
        window.blit(self.IMAGE, (self.x1, self.y))
        window.blit(self.IMAGE, (self.x2, self.y))


# draw all of the images on top of each other
def draw_window(window, birds, pipes, base, score, generation, num_birds):
    # blit means draw. Draw whatever I put inside the arguments.
    window.blit(BACKGROUND_IMAGE, (0,0))
    # draw all pipes in array
    for pipe in pipes:
        pipe.draw(window)

    # grab the score and render it into white text
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    # place the score text on the top-right of the screen and keep moving it to
    # the lift if the text gets larger)
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    # print the current generation on the screen
    text = STAT_FONT.render("Generation: " + str(generation), 1, (255, 255, 255))
    window.blit(text, (10, 10))
    # print the current number of surviving birds
    text = STAT_FONT.render("Birds: " + str(num_birds), 1, (255, 255, 255))
    window.blit(text, (10, 50))
    # draw the floor
    base.draw(window)
    for bird in birds:
        # draw the bird
        bird.draw(window)

    pygame.display.update()

# main game loop 
def main(genomes, config):
    global GENERATION
    GENERATION += 1
    # we're passing a list of genomes. Each genome represents a neural_network
    neural_networks = []
    # we need a list for the genomes since we'll give each of them their 
    # fitness value
    genome_list = []
    # since we want all birds in the same population and generation to run at
    # the same time, we need to make a birds array.
    birds = []

    # NEAT actually gives us a list of genome objects (genomes). NEAT starts 
    # with these genomes which are encodings of potential neural networks (node 
    # genes and connection genes). Then, NEAT (we actually do it in the next 
    # line) constructs the neural network from the genome.
    # for each genome given by neat
    for genome_id, genome in genomes:
        # create the neural network using this genome
        neural_network = neat.nn.FeedForwardNetwork.create(genome, config)
        # add it to the list of neural networks
        neural_networks.append(neural_network)
        # give it a corresponding Bird to control
        birds.append(Bird(230, 350))
        # set its initial fitness to 0
        genome.fitness = 0
        # add this genome to the genome list for later usage (keep track of its
        # fitness and change it as we desire)
        genome_list.append(genome)


    base = Base(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
    score = 0
    # we have a universal flag to determine whether the game should be running
    # we need to implement a clock so we can set the framerate so the game
    # runs at a constant speed rather than depending on how fast my computer is.
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        # grab external events like keyboard events
        for event in pygame.event.get():
            # if the event is a quit keyboard click
            if event.type == pygame.QUIT:
                # leave the game loop
                run = False
                # quit the game actually
                pygame.quit()
                quit()
        # We are feeding 3 numbers as input to the neural networks. 2 of them
        # represent the bird's distance from the top and bottom pipes.
        # However, we need to know exactly which pair of pipes we are referring
        # to since there can be two pairs of pipes on the screen at the same time.
        # initialize the index of the pipe pair to watch for
        pipe_index = 0
        # if there are surviving birds
        if len(birds) > 0:
            # if there is more than one pair of pipes and the first pair is
            # behind the birds
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                # the pipe we should be looking at is the second one
                pipe_index = 1
        # if there are no birds left
        else:
            # quit this generation
            run = False
            break

        for index_3, bird in enumerate(birds):
            bird.move()
            # if the bird has survived a frame from moving, add a little fitness
            genome_list[index_3].fitness += 0.1

            # holds the value of the output of the neural network
            # the arguments are the inputs that we feed the neural networks:
            # the bird's y position, the top pipe's vertical distance from
            # the bird's position, and the bottom pipe's vertical distance from
            # the bird's position. output is actually a list
            output = neural_networks[index_3].activate([bird.y, 
                                                       abs(bird.y - pipes[pipe_index].height),
                                                       abs(bird.y - pipes[pipe_index].bottom)])
            # if the output reached the jump threshold 0.5
            # if we had multiple output neurons, then, this list would've been
            # more than just 1 element
            if output[0] > 0.5:
                # make the bird jump
                bird.jump()
        
        """ PIPE CYCLE START """
        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for index, bird in enumerate(birds):
                # if the bird collided with the pipe
                if pipe.collide(bird):
                    # we want to discourage the bird from hitting the pipe
                    genome_list[index].fitness -= 1
                    birds.pop(index)
                    neural_networks.pop(index)
                    genome_list.pop(index)

                # if the bird has passed the pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            
            # if the pipe is completely off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)


            pipe.move()
            
        # if we passed 1 pipe, we need to make another and add to the score
        if add_pipe:
            score += 1
            for surviving_genome in genome_list:
                surviving_genome.fitness += 5
            pipes.append(Pipe(600))

        # remove pipes that we have passed
        for removing_pipe in remove_pipes:
            pipes.remove(removing_pipe)

        """PIPE CYCLE END"""

        for index_2, bird in enumerate(birds):
            # if the bird has hit the ground
            if bird.y + bird.image.get_height() > 730 or bird.y < 0:
                birds.pop(index_2)
                neural_networks.pop(index_2)
                genome_list.pop(index_2)

        base.move()
        draw_window(window, birds, pipes, base, score, GENERATION, num_birds=len(birds))
    

def run(configuration_file_path):
    # connects the config file to our code, by connecting all of our subheadings
    # in our text file, we're telling neat all the properties that we're setting
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                    neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                    configuration_file_path)
    
    population = neat.Population(config)
    # stats reporters, gives us the terminal output that details the NEAT run
    # like generation statistics
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # 50 means how many generations we are gonna run.
    # it also calls the main function 50 times and pass it all of the genomes
    # and config file. Main will generate a game based on all of the birds
    # (in reality, genomes) that were given.
    winner = population.run(main, 50)

if __name__ == "__main__":
    # this gives us the path of the directory that we're currently in
    local_directory = os.path.dirname(__file__)
    # now, we can grab the configuration file using the local directory
    configuration_file_path = os.path.join(local_directory, "config-feedforward.txt")
    run(configuration_file_path)

