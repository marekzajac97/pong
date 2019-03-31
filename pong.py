import pygame
import sys
import time
import configparser
from pygame.locals import *
from random import randint
from numpy import linspace
# from numpy import random

pygame.init()

# Read config from the file
config = configparser.ConfigParser()
config.read('config.ini')
try:
    WINDOW_WIDTH = int(config['GENERAL']['WINDOW WIDTH'])
    WINDOW_HEIGHT = int(config['GENERAL']['WINDOW HEIGHT'])
    MAX_POINTS = int(config['GENERAL']['POINTS TO WIN'])
    AI_ENABLE = config['GENERAL']['ENABLE AI'] in ['true', '1', 't', 'y', 'yes']
    AI_SKILL_LVL = int(config['GENERAL']['AI SKILL'])
    PADDLE_SIZE = [int(config['PADDLE SETTINGS']['PADDLE WIDTH']), int(config['PADDLE SETTINGS']['PADDLE HEIGHT'])]
    PADDLE_OFFSET = [int(config['PADDLE SETTINGS']['PADDLE OFFSET X AXIS']),
                     int(config['PADDLE SETTINGS']['PADDLE OFFSET Y AXIS'])]
    PADDLE_SPEED = int(config['PADDLE SETTINGS']['PADDLE SPEED'])  # pixels per clock tick ( 60 ms )
    BALL_SIZE = int(config['BALL SETTINGS']['BALL SIZE'])
    MIN_BALL_SPEED = int(config['BALL SETTINGS']['MINIMAL BALL SPEED'])
    MAX_BALL_SPEED = int(config['BALL SETTINGS']['MAXIMAL BALL SPEED'])
except:
    print("incorrect configuration file!")
    sys.exit()
# Check whether values are correct
if(WINDOW_HEIGHT <= 0 or WINDOW_WIDTH <= 0 or MAX_POINTS <= 0 or PADDLE_SIZE[0] <= 0 or PADDLE_SIZE[1] <= 0 or
        PADDLE_OFFSET[0] <= 0 or PADDLE_OFFSET[1] <= 0 or PADDLE_SPEED <= 0 or BALL_SIZE <= 0 or MIN_BALL_SPEED <= 0 or
        AI_SKILL_LVL < 1 or AI_SKILL_LVL > 5 or MIN_BALL_SPEED > MAX_BALL_SPEED):
        print("incorrect configuration file!")
        sys.exit()

# Make a 9 element vector containing ball speeds from min to max with equal step
ball_speeds = linspace(MIN_BALL_SPEED, MAX_BALL_SPEED, 9, True)
ball_speeds = [round(elem) for elem in ball_speeds]

# Set up AI skill parameters
ai_skill = []
ai_return_to_middle = False
if AI_SKILL_LVL == 1:
        ai_skill = [1, 0.2]
        ai_return_to_middle = False
elif AI_SKILL_LVL == 2:
        ai_skill = [1, 0.6]
        ai_return_to_middle = False
elif AI_SKILL_LVL == 3:
        ai_skill = [0.8, 0.6]
        ai_return_to_middle = False
elif AI_SKILL_LVL == 4:
        ai_skill = [0.75, 0.6]
        ai_return_to_middle = True
elif AI_SKILL_LVL == 5:
        ai_skill = [0.65, 1]
        ai_return_to_middle = True
else:
        ai_skill = [0.8, 0.5]  # default is lvl 3
        ai_return_to_middle = False

MIDDLE = round(WINDOW_HEIGHT/2)


# Some flags
player1_win = False
player2_win = False
pause = False

# States of the paddles
UP1 = False
DOWN1 = False
UP2 = False
DOWN2 = False

# Directions of the ball
UPLEFT = 0
DOWNLEFT = 1
UPRIGHT = 2
DOWNRIGHT = 3

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (169, 169, 169)
GREY = (128, 128, 128)

# Create the main surface

main_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
surface_rect = main_surface.get_rect()
pygame.display.set_caption("Pong Game")


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player_number):

        # Set parameters for the paddle
        pygame.sprite.Sprite.__init__(self)

        self.player_number = player_number
        self.image = pygame.Surface(PADDLE_SIZE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.speed = PADDLE_SPEED

        # Establish the location of each paddle

        if self.player_number == 1:
            self.rect.centerx = main_surface.get_rect().left
            self.rect.centerx += PADDLE_OFFSET[0]
        elif self.player_number == 2:
            self.rect.centerx = main_surface.get_rect().right
            self.rect.centerx -= PADDLE_OFFSET[0]
        self.rect.centery = main_surface.get_rect().centery

    def move(self):
        # Move the paddle depending on the UP and DOWN flags' states
        if self.player_number == 1:
            if UP1 and (self.rect.y > PADDLE_OFFSET[1]):
                self.rect.y -= self.speed
            elif DOWN1 and (self.rect.bottom < WINDOW_HEIGHT - PADDLE_OFFSET[1]):
                self.rect.y += self.speed

        if self.player_number == 2:
            if UP2 and (self.rect.y > PADDLE_OFFSET[1]):
                self.rect.y -= self.speed
            elif DOWN2 and (self.rect.bottom < WINDOW_HEIGHT - PADDLE_OFFSET[1]):
                self.rect.y += self.speed


class Ball(pygame.sprite.Sprite):
    def __init__(self):

        # Ball parameters
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([BALL_SIZE, BALL_SIZE], SRCALPHA, 32)
        self.image.convert_alpha()  # Make the background of the rectangular sprite transparent
        pygame.draw.circle(self.image, WHITE, (int(BALL_SIZE/2), int(BALL_SIZE/2)), int(BALL_SIZE/2))  # Ball shape
        self.rect = self.image.get_rect()
        self.rect.centerx = surface_rect.centerx  # Position in the center
        self.rect.centery = surface_rect.centery
        self.direction = randint(0, 3)  # Random direction at the beginning
        self.speed = MIN_BALL_SPEED

    def move(self):
        # Move the ball depending on its current direction
        if self.direction == UPLEFT:
            self.rect.x -= self.speed
            self.rect.y -= self.speed
        elif self.direction == UPRIGHT:
            self.rect.x += self.speed
            self.rect.y -= self.speed
        elif self.direction == DOWNLEFT:
            self.rect.x -= self.speed
            self.rect.y += self.speed
        elif self.direction == DOWNRIGHT:
            self.rect.x += self.speed
            self.rect.y += self.speed

    def change_direction(self):
        # Change the direction of the ball if it hits the boundaries
        if self.rect.y < 0 and self.direction == UPLEFT:
            self.direction = DOWNLEFT
        if self.rect.y < 0 and self.direction == UPRIGHT:
            self.direction = DOWNRIGHT
        if self.rect.bottom > surface_rect.bottom and self.direction == DOWNLEFT:
            self.direction = UPLEFT
        if self.rect.bottom > surface_rect.bottom and self.direction == DOWNRIGHT:
            self.direction = UPRIGHT


def paddle_hit():
    # Change direction of the ball on the paddle-ball collision
    if pygame.sprite.collide_rect(ball, paddle2):
        if ball.direction == UPRIGHT:
            ball.direction = UPLEFT
        elif ball.direction == DOWNRIGHT:
            ball.direction = DOWNLEFT
        ai_predict()
    elif pygame.sprite.collide_rect(ball, paddle1):
        if ball.direction == UPLEFT:
            ball.direction = UPRIGHT
        elif ball.direction == DOWNLEFT:
            ball.direction = DOWNRIGHT
        ai_predict()


def ai_predict():
    # predict ball position / calculate where the paddle should be (for AI)
    global ai_move_point
    # copy ball parameters
    direction = ball.direction
    position_x = ball.rect.x
    position_y = ball.rect.y
    # make a simple simulation of the ball movement
    while position_x < (WINDOW_WIDTH - PADDLE_OFFSET[0]):
        if direction == DOWNRIGHT:
            position_x += WINDOW_HEIGHT - position_y + BALL_SIZE
            position_y = WINDOW_HEIGHT - BALL_SIZE
            direction = UPRIGHT
        elif direction == UPRIGHT:
            position_x += position_y
            position_y = 0
            direction = DOWNRIGHT
        else:
            break
    if direction == DOWNRIGHT:
        ai_move_point = position_x - (WINDOW_WIDTH - PADDLE_OFFSET[0])
    elif direction == UPRIGHT:
        ai_move_point = WINDOW_HEIGHT - (position_x - (WINDOW_WIDTH - PADDLE_OFFSET[0]))
    else:
        ai_move_point = MIDDLE
    # add a slight misalignment (simulate human error)
    # ai_move_point += round(random.normal(0, PADDLE_SIZE[1]/4))


# Fonts for the scoreboard/game paused/game over text
basic_font = pygame.font.SysFont("MS Sans Serif", 120)
game_over_font_big = pygame.font.SysFont("MS Sans Serif", 72)
game_over_font_small = pygame.font.SysFont("MS Sans Serif", 50)
pause_font = pygame.font.SysFont("MS Sans Serif", 25)

# Create paddle and ball objects
paddle1 = Paddle(1)
paddle2 = Paddle(2)
ball = Ball()

# Group them into one render plain
all_sprites = pygame.sprite.RenderPlain(paddle1, paddle2, ball)

# Set up player scores
player1_score = 0
player2_score = 0

# Get a clock
clock = pygame.time.Clock()

# For counting iterations of the main loop
counter = 0

# Move point for AI, middle of the screen by default
ai_move_point = MIDDLE

# Main loop
while True:

    # Clock tick - game's framerate
    clock.tick(60)

    # If the ball is outside of boundaries put it back in the center
    if ball.rect.x > WINDOW_WIDTH:
        ball.rect.centerx = surface_rect.centerx
        ball.rect.centery = surface_rect.centery
        ball.direction = randint(0, 1)
        ai_predict()
    elif ball.rect.x < 0:
        ball.rect.centerx = surface_rect.centerx
        ball.rect.centery = surface_rect.centery
        ball.direction = randint(2, 3)
        ai_predict()

    # Check if the AI is enabled
    if not AI_ENABLE:
        # If not, make the second paddle to be controlled with the mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()  # get the cursor coordinates
        if mouse_y < paddle2.rect.centery - round(0.5*PADDLE_SIZE[0]):  # if the cursor is above the paddle move it up
            UP2 = True
            DOWN2 = False
        elif mouse_y > paddle2.rect.centery + round(0.5*PADDLE_SIZE[0]):  # if the cursor is below move the paddle down
            UP2 = False
            DOWN2 = True
        else:  # if the cursor is in the middle of the paddle don't move it
            UP2 = False
            DOWN2 = False
    else:
        # AI stuff
        if ball.rect.centerx > ai_skill[0] * WINDOW_WIDTH or (ai_move_point == MIDDLE and ai_return_to_middle):
            # after certain distance from the ball is reached move the paddle automatically to predicted position
            # give AI more time to react on higher difficulty levels
            if ai_move_point > paddle2.rect.centery + PADDLE_SPEED:
                UP2 = False
                DOWN2 = True
            elif ai_move_point < paddle2.rect.centery - PADDLE_SPEED:
                UP2 = True
                DOWN2 = False
            else:
                UP2 = False
                DOWN2 = False
        elif ball.rect.centerx > ai_skill[1] * WINDOW_WIDTH and (ball.direction == UPRIGHT or ball.direction == DOWNRIGHT):
            # move the paddle up or down depending on how far the ball is from the middle of the paddle
            if ball.rect.centery < paddle2.rect.centery - PADDLE_SPEED:
                UP2 = True
                DOWN2 = False
            elif ball.rect.centery > paddle2.rect.centery + PADDLE_SPEED:
                UP2 = False
                DOWN2 = True
            else:
                UP2 = False
                DOWN2 = False
        else:
            UP2 = False
            DOWN2 = False

    # Check for the specific events
    for event in pygame.event.get():
        # stop the program if QUIT or ESCAPE were pressed
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            # Player 1 input for steering the paddle
            elif event.key == K_UP:
                UP1 = True
                DOWN1 = False
            elif event.key == K_DOWN:
                UP1 = False
                DOWN1 = True
            # P - pause button
            elif event.key == K_p:
                if not pause:
                    pause = True
                else:
                    pause = False
            # R - reset scoreboard button
            elif event.key == K_r:
                player1_score = 0
                player2_score = 0
            # Keys 1-9 - set the ball speed
            elif event.key == K_1:
                ball.speed = ball_speeds[0]
            elif event.key == K_2:
                ball.speed = ball_speeds[1]
            elif event.key == K_3:
                ball.speed = ball_speeds[2]
            elif event.key == K_4:
                ball.speed = ball_speeds[3]
            elif event.key == K_5:
                ball.speed = ball_speeds[4]
            elif event.key == K_6:
                ball.speed = ball_speeds[5]
            elif event.key == K_7:
                ball.speed = ball_speeds[6]
            elif event.key == K_8:
                ball.speed = ball_speeds[7]
            elif event.key == K_9:
                ball.speed = ball_speeds[8]
        elif event.type == KEYUP:
            # Stop the first paddle when up key or down key is released
            if event.key == K_DOWN:
                DOWN1 = False
            elif event.key == K_UP:
                UP1 = False

    # Render scoreboard and position it
    score_board_1 = basic_font.render(str(player1_score), True, GREY, BLACK)
    score_board_2 = basic_font.render(str(player2_score), True, GREY, BLACK)
    score_board_1_rect = score_board_1.get_rect()
    score_board_2_rect = score_board_2.get_rect()
    score_board_1_rect.centerx = surface_rect.centerx - round(0.15*WINDOW_WIDTH)
    score_board_1_rect.centery = surface_rect.top + round(0.15*WINDOW_HEIGHT)
    score_board_2_rect.centerx = surface_rect.centerx + round(0.15*WINDOW_WIDTH)
    score_board_2_rect.centery = surface_rect.top + round(0.15*WINDOW_HEIGHT)

    # Reset the main surface
    main_surface.fill(BLACK)

    # Draw scoreboard
    main_surface.blit(score_board_1, score_board_1_rect)
    main_surface.blit(score_board_2, score_board_2_rect)

    # Draw a dotted line in the middle [MAY CAUSE LAGS]
    # for i in range(0, WINDOW_HEIGHT, 10):
    #     dotted_line = pygame.Rect(surface_rect.centerx, i, 5, 10)
    #     pygame.draw.rect(main_surface, GREY, dotted_line)

    # Draw a simple line instead
    line = pygame.Rect(surface_rect.centerx, 0, 5, WINDOW_HEIGHT)
    pygame.draw.rect(main_surface, GREY, line)

    # Draw paddles and ball
    all_sprites.draw(main_surface)

    if not pause:
        # if the game is not paused - call functions for moving paddles and ball / checking for collisions
        paddle1.move()
        paddle2.move()
        ball.move()
        ball.change_direction()
        paddle_hit()
    else:
        # if paused, just display "GAME PAUSED" text in the corner
        pause_txt = pause_font.render("GAME PAUSED", True, WHITE, BLACK)
        pause_txt_rect = pause_txt.get_rect()
        pause_txt_rect.x = 5
        pause_txt_rect.y = 5
        main_surface.blit(pause_txt, pause_txt_rect)

    # add scores for the players when the ball hits the left or right side of the screen
    if ball.rect.x > WINDOW_WIDTH:
        player1_score += 1
    elif ball.rect.x < 0:
        player2_score += 1

    # update the screen
    pygame.display.update()

    # at the beginning of the game
    if counter == 0:
        # add some delay
        time.sleep(1)
        # tell AI where the ball is going to hit
        ai_predict()

    # break the main loop if one of the players wins
    if player1_score == MAX_POINTS:
        player1_win = True
        break
    elif player2_score == MAX_POINTS:
        player2_win = True
        break

    # increment the counter
    counter += 1

# GAME OVER screen loop
while True:

    for event in pygame.event.get():
        # stop the program if QUIT or ESCAPE were pressed
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    # Reset the main surface
    main_surface.fill(BLACK)

    # Render GAME OVER text as well as the player name
    if player1_win:
        game_over = game_over_font_big.render("GAME OVER", True, WHITE, BLACK)
        game_over1 = game_over_font_small.render("Player 1 Wins", True, WHITE, BLACK)
    elif player2_win:
        game_over = game_over_font_big.render("GAME OVER", True, WHITE, BLACK)
        game_over1 = game_over_font_small.render("Player 2 Wins", True, WHITE, BLACK)

    # Position the text
    game_over_rect = game_over.get_rect()
    game_over_rect.centerx = surface_rect.centerx
    game_over_rect.centery = surface_rect.centery - 50
    game_over1_rect = game_over1.get_rect()
    game_over1_rect.centerx = game_over_rect.centerx
    game_over1_rect.centery = game_over_rect.centery + 75

    # Display the text
    main_surface.blit(game_over, game_over_rect)
    main_surface.blit(game_over1, game_over1_rect)

    # Update the screen
    pygame.display.update()
