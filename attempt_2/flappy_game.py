import pygame
import bird_class
import pipe_class
import floor_class
import os

# Initialize Pygame
pygame.init()

# Load Background Image
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "background.png")))
WINDOW_WIDTH = BACKGROUND_IMAGE.get_width()
WINDOW_HEIGHT = BACKGROUND_IMAGE.get_height()
FONT = pygame.font.SysFont('aptos', 50)

# Function to Draw the Game
def draw_game(window, bird, pipes, floor, score):
    window.blit(BACKGROUND_IMAGE, (0,0))

    # Draw Pipes
    for pipe in pipes:
        pipe.draw(window)

    # Display Score
    text = FONT.render(f"Score: {score}", 1, (255, 255, 255))
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    # Draw Floor and Bird
    floor.draw(window)
    bird.draw(window)

    pygame.display.update()

# Function for Player to Play the Game
def play_game():
    # Initialize Bird, Floor, and Pipes
    bird = bird_class.Bird(230, 350)
    floor = floor_class.Floor(800)
    pipes = [pipe_class.Pipe(700)]

    # Display Game Window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
    score = 0
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(30)

        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()  # Player makes the bird jump

        # Determine Pipe to Look At
        pipe_index = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].top_pipe_image.get_width():
            pipe_index = 1

        # Move Bird
        bird.move()

        # Manage Pipes
        add_pipe = False
        remove_pipes = []

        for pipe in pipes:
            if pipe.collide(bird):
                print("Bird crashed! Lol.")
                run = False
                break

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            if pipe.x + pipe.top_pipe_image.get_width() < 0:
                remove_pipes.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(pipe_class.Pipe(600))

        for pipe in remove_pipes:
            pipes.remove(pipe)

        if bird.y + bird.image.get_height() > WINDOW_HEIGHT or bird.y < 0:
            print("Bird fell!")
            run = False
            break

        floor.move()
        draw_game(window, bird, pipes, floor, score)

# Run the Player Game
if __name__ == "__main__":
    play_game()
