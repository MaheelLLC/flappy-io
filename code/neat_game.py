import pygame
import bird_class
import pipe_class
import floor_class
import os
import neat
import pickle

# initialize pygame
pygame.init()

# load background image
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "background.png")))
# set game window width
WINDOW_WIDTH = BACKGROUND_IMAGE.get_width()
# set game window height
WINDOW_HEIGHT = BACKGROUND_IMAGE.get_height()
# set game font: shows score, generation, and number of birds
FONT = pygame.font.SysFont('aptos', 50)
# set current generation
GENERATION = 0

# save the best bird
def save_best_bird(genome, neural_network):
    best_bird_data = {
        "genome": genome,
        "neural_network": neural_network
    }
    with open("best_bird.pkl", "wb") as f:
        pickle.dump(best_bird_data, f)
    print("Best bird saved successfully!")

def draw_game(window, birds, pipes, floor, score, generation, num_birds):
    # draw the background image
    window.blit(BACKGROUND_IMAGE, (0,0))

    # draw all pipes in array
    for pipe in pipes:
        pipe.draw(window)

    # grab the score and render it into white text
    text = FONT.render("Score: " + str(score), 1, (255, 255, 255))
    # place the score text on the top right of the screen
    # if the score gets too large, move it to the left
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    # print the current generation on the screen
    text = FONT.render("Generation: " + str(generation), 1, (255, 255, 255))
    window.blit(text, (10, 10))
    # print the current number of surviving birds
    text = FONT.render("Birds: " + str(num_birds), 1, (255, 255, 255))
    window.blit(text, (10, 50))
    
    # draw the floor
    floor.draw(window)

    # draw all birds in array
    for bird in birds:
        bird.draw(window)

    # update the pygame display with drawn items
    pygame.display.update()

def main(genomes, config):
    # grab the current generation
    global GENERATION
    # each time this function runs, we are in a new generation
    GENERATION += 1
    # list of active neural networks
    neural_networks = []
    # list of corresponding genomes, index matches with the neural networks
    genome_list = []
    # list of birds controlled by neural networks
    # index matches with the other two
    birds = []

    # NEAT actually gives us a list of genome objects (genomes). NEAT starts 
    # with these genomes which are encodings of potential neural networks (node 
    # genes and connection genes).
    # for each genome given by NEAT
    for genome_id, genome in genomes:
        # construct the neural network from the genome
        neural_network = neat.nn.FeedForwardNetwork.create(genome, config)
        # add it to the list of neural networks
        neural_networks.append(neural_network)
        # give it a corresponding Bird to control
        birds.append(bird_class.Bird(230, 350))
        # set its initial fitness to 0
        genome.fitness = 0
        # add this genome to the genome list for later usage (keep track of its
        # fitness and change it as we desire)
        genome_list.append(genome)

    # create the floor object
    floor = floor_class.Floor(800)
    # create the first pipe and put it in the pipes list
    pipes = [pipe_class.Pipe(700)]

    # display the game window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
    # initialize the score
    score = 0
    # to ensure the game runs at a consistent framerate, set up a clock
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
        
        pipe_index = 0
        # if there are surviving birds
        if len(birds) > 0:
            # if there is more than one pair of pipes and the first pair is
            # behind the birds
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].top_pipe_image.get_width():
                # the pipe we should be looking at is the second one
                pipe_index = 1
        # if there are no birds left
        else:
            # quit this generation
            run = False
            break
        # for every bird still playing the game
        for index_3, bird in enumerate(birds):
            # move the bird
            bird.move()
            # if the bird has survived a frame from moving, add a little fitness
            genome_list[index_3].fitness += 0.1

            # holds the value of the output of the neural network
            # the arguments are the inputs that we feed the neural networks:
            # the bird's y position, the top pipe's vertical distance from
            # the bird's position, and the bottom pipe's vertical distance from
            # the bird's position. output is actually a list
            output = neural_networks[index_3].activate([bird.y, 
                        abs(bird.y - pipes[pipe_index].top_pipe_end),
                        abs(bird.y - pipes[pipe_index].bottom_pipe_start)])
            # if the output reached the jump threshold which is 0.5
            if output[0] > 0.5:
                # make the bird jump
                bird.jump()

        # initialize the conditional for adding pipes
        add_pipe = False
        # intialize the list for pipes to be removed
        remove_pipes = []
        # for every pipe in the game
        for pipe in pipes:
            # for each bird
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
                    # make the pipe into a passed one
                    pipe.passed = True
                    # we are ready to add a new pipe
                    add_pipe = True
            
            # if the pipe is completely off the screen
            if pipe.x + pipe.top_pipe_image.get_width() < 0:
                # add it to the removal list
                remove_pipes.append(pipe)
            
            # move the pipe
            pipe.move()

        # if we are ready to add a new pipe to the game
        if add_pipe:
            # add 1 point to game score
            score += 1
            # for each genome still in the game
            for surviving_genome in genome_list:
                # give them 5 points for getting through said pipe
                surviving_genome.fitness += 5
            pipes.append(pipe_class.Pipe(600))
        
        # save the best bird if score hits 50
        if score >= 35:
            save_best_bird(genome_list[0], neural_networks[0])
            run = False
            break

        # if we have any pipes that need to be removed
        for removing_pipe in remove_pipes:
            # remove the pipe
            pipes.remove(removing_pipe)

        for index_2, bird in enumerate(birds):
            # if the bird has hit the ground or flew to the sky
            if bird.y + bird.image.get_height() > 800 or bird.y < 0:
                birds.pop(index_2)
                neural_networks.pop(index_2)
                genome_list.pop(index_2)

        floor.move()
        draw_game(window, birds, pipes, floor, score, GENERATION, len(birds))

def run(configuration_file_path):
    # connects the config file to our code, by connecting all of our subheadings
    # in our text file, we're telling neat all the properties that we're setting
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                    neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                    configuration_file_path)
    # generate the genome population
    population = neat.Population(config)
    # stats reporters, gives us the terminal output that details the NEAT run
    # with information such as generation statistics
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # 50 means how many generations we are gonna run.
    # it also calls the main function 50 times and pass it all of the genomes
    # and config file. Main will generate a game based on all of the birds
    # (in reality, genomes) that were given.
    # put the population through my main game loop and if we get a winner,
    # return him
    winner = population.run(main, 50)

if __name__ == "__main__":
    # this gives us the path of the directory that we're currently in
    local_directory = os.path.dirname(__file__)
    # now, we can grab the configuration file using the local directory
    configuration_file_path = os.path.join(local_directory, "config-feedforward.txt")
    run(configuration_file_path)