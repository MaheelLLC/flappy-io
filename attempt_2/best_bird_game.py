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

def draw_game(window, bird, pipes, floor, score):
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
    
    # draw the floor
    floor.draw(window)

    bird.draw(window)

    # update the pygame display with drawn items
    pygame.display.update()

def best_bird_play():
    # load the best bird
    try:
        with open("best_bird.pkl", "rb") as f:
            best_data = pickle.load(f)
            best_genome = best_data["genome"]
            best_neural_network = best_data["neural_network"]
    except FileNotFoundError:
        print("Error: Best bird file not found. Sucks to be you.")
        return

    bird = bird_class.Bird(230, 350)
    floor = floor_class.Floor(800)
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
        # if there is more than one pair of pipes and the first pair is
        # behind the birds
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].top_pipe_image.get_width():
            # the pipe we should be looking at is the second one
            pipe_index = 1

        bird.move()
        output = best_neural_network.activate([
            bird.y,
            abs(bird.y - pipes[pipe_index].top_pipe_end),
            abs(bird.y - pipes[pipe_index].bottom_pipe_start)])
        
        if output[0] > 0.5:
            bird.jump()

        add_pipe = False
        # intialize the list for pipes to be removed
        remove_pipes = []
        # for every pipe in the game
        for pipe in pipes:
            if pipe.collide(bird):
                print("Bird died lol")
                run = False
                break

            if not pipe.passed and pipe.x < bird.x:
                # make the pipe into a passed one
                pipe.passed = True
                # we are ready to add a new pipe
                add_pipe = True

            if pipe.x + pipe.top_pipe_image.get_width() < 0:
                # add it to the removal list
                remove_pipes.append(pipe)
            
            pipe.move()
    
        if add_pipe:
            score += 1
            pipes.append(pipe_class.Pipe(600))
        
        for removing_pipe in remove_pipes:
            pipes.remove(removing_pipe)

        if bird.y + bird.image.get_height() > WINDOW_HEIGHT or bird.y < 0:
            print("Bird died lol")
            run = False
            break

        floor.move()
        draw_game(window, bird, pipes, floor, score)

# Run the chad
if __name__ == "__main__":
    best_bird_play()