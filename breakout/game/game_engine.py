"""
GameEngine: owns the paddle, ball, and bricks.

Starter version: single brick type, no lives yet, no score/combo yet.
Ball-brick collision also has a known bug (see game/collision.py) that
Task 1 asks you to fix. If the ball falls below the paddle, it just
resets to the starting position with no consequence - that's what
Task 2 builds on.
"""

import pygame

from game.paddle import Paddle
from game.ball import Ball
from game.brick import Brick
from game.collision import handle_ball_brick_collision
from game.renderer import WIDTH, HEIGHT
from game.brick import Brick, NORMAL, STRONG, UNBREAKABLE

BRICK_ROWS = 4
BRICK_COLS = 8
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 6
BRICK_TOP_MARGIN = 50
STARTING_LIVES = 3
BRICK_POINTS = 10
MAX_MULTIPLIER = 5


class GameEngine:
    def __init__(self):
        self.restart()

    def restart(self):
        """Reset everything for a fresh game."""
        self.paddle = Paddle(x=WIDTH / 2, y=HEIGHT - 30)
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)
        self.bricks = self._build_bricks()
        self.lives = STARTING_LIVES
        self.game_over = False
        self.score = 0
        self.multiplier = 1

    def _brick_kind(self, row, col):
        if row == 0:
            return STRONG                                   # top row: strong
        if row == 2 and col in (0, BRICK_COLS - 1):
            return UNBREAKABLE                              # two steel bricks at the edges
        return NORMAL

    def _build_bricks(self):
        bricks = []
        total_width = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (WIDTH - total_width) / 2
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)
                bricks.append(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, self._brick_kind(row, col)))
        return bricks

    def _reset_ball(self):
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)

    def handle_input(self, keys_pressed):
        dx = 0
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.paddle.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.paddle.speed
        self.paddle.move(dx, WIDTH)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.restart()

    def update(self):
        if self.game_over:
            return

        self.ball.update()
        self.ball.bounce_off_walls(WIDTH)

        if self.ball.get_rect().colliderect(self.paddle.get_rect()) and self.ball.vy > 0:
            self.ball.bounce_off_paddle(self.paddle.get_rect())

        for brick in self.bricks:
            if handle_ball_brick_collision(self.ball, brick):
                if brick.hit():
                    self.bricks.remove(brick)
                    self.score += BRICK_POINTS * self.multiplier   # score at the CURRENT multiplier
                    self.multiplier = min(MAX_MULTIPLIER, self.multiplier + 1)
                break

        if self.ball.is_below(HEIGHT):
            self.multiplier = 1                                    # missed: combo is lost
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.paddle, self.ball, self.bricks)

        remaining = sum(1 for b in self.bricks if b.breakable)
        renderer.draw_text(surface, font, f"Bricks left: {remaining}", (10, 10))

        score_text = f"Score: {self.score}  x{self.multiplier}"
        score_x = (WIDTH - font.size(score_text)[0]) // 2           # centered
        renderer.draw_text(surface, font, score_text, (score_x, 10))

        lives_text = f"Lives: {self.lives}"
        lives_x = WIDTH - font.size(lives_text)[0] - 10
        renderer.draw_text(surface, font, lives_text, (lives_x, 10))

        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - Press R to restart")