import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 80
        self.speed = 6
        
    def move_up(self):
        if self.y > 0:
            self.y -= self.speed
            
    def move_down(self):
        if self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, CYAN, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))

class AI:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 80
        self.speed = 4
        
    def update(self, ball):
        ball_center_y = ball.y + ball.radius
        paddle_center_y = self.y + self.height // 2
        
        if ball_center_y < paddle_center_y - 10:
            if self.y > 0:
                self.y -= self.speed
        elif ball_center_y > paddle_center_y + 10:
            if self.y < SCREEN_HEIGHT - self.height:
                self.y += self.speed
                
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, RED, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed_x = random.choice([-5, 5])
        self.speed_y = random.uniform(-3, 3)
        self.max_speed = 8
        
    def update(self, player, ai):
        self.x += self.speed_x
        self.y += self.speed_y
        
        if self.y - self.radius <= 0 or self.y + self.radius >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y
            
        if (self.x - self.radius <= player.x + player.width and
            self.x + self.radius >= player.x and
            self.y >= player.y and
            self.y <= player.y + player.height):
            if self.speed_x < 0:
                self.speed_x = -self.speed_x
                hit_pos = (self.y - (player.y + player.height // 2)) / (player.height // 2)
                self.speed_y = hit_pos * 4
                self.speed_x = min(self.speed_x + 0.5, self.max_speed)
                
        if (self.x + self.radius >= ai.x and
            self.x - self.radius <= ai.x + ai.width and
            self.y >= ai.y and
            self.y <= ai.y + ai.height):
            if self.speed_x > 0:
                self.speed_x = -self.speed_x
                hit_pos = (self.y - (ai.y + ai.height // 2)) / (ai.height // 2)
                self.speed_y = hit_pos * 4
                self.speed_x = max(self.speed_x - 0.5, -self.max_speed)
                
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed_x = random.choice([-5, 5])
        self.speed_y = random.uniform(-3, 3)
        
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Modern Tennis Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.big_font = pygame.font.Font(None, 72)
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(30, SCREEN_HEIGHT // 2 - 40)
        self.ai = AI(SCREEN_WIDTH - 45, SCREEN_HEIGHT // 2 - 40)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = ""
        self.winning_score = 5
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
        
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_down()
            
        self.ai.update(self.ball)
        self.ball.update(self.player, self.ai)
        
        if self.ball.x < 0:
            self.ai_score += 1
            self.ball.reset()
            
        if self.ball.x > SCREEN_WIDTH:
            self.player_score += 1
            self.ball.reset()
            
        if self.player_score >= self.winning_score:
            self.game_over = True
            self.winner = "Player"
        elif self.ai_score >= self.winning_score:
            self.game_over = True
            self.winner = "AI"
            
    def draw(self):
        self.screen.fill(BLACK)
        
        for i in range(0, SCREEN_WIDTH, 2):
            for j in range(0, SCREEN_HEIGHT, 2):
                if random.random() < 0.001:
                    pygame.draw.rect(self.screen, WHITE, (i, j, 1, 1))
        
        for i in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 2, i, 4, 10))
        
        if not self.game_over:
            self.player.draw(self.screen)
            self.ai.draw(self.screen)
            self.ball.draw(self.screen)
            
        player_score_text = self.font.render(str(self.player_score), True, CYAN)
        ai_score_text = self.font.render(str(self.ai_score), True, RED)
        self.screen.blit(player_score_text, (SCREEN_WIDTH // 4, 50))
        self.screen.blit(ai_score_text, (3 * SCREEN_WIDTH // 4, 50))
        
        if self.game_over:
            if self.winner == "Player":
                victory_text = self.big_font.render("YOU WIN!", True, GREEN)
            else:
                victory_text = self.big_font.render("AI WINS!", True, RED)
            restart_text = self.font.render("Press R to Play Again", True, WHITE)
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(victory_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
            
        controls_text = self.font.render("Controls: W/S or Up/Down arrows, ESC to quit", True, WHITE)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        self.screen.blit(controls_text, controls_rect)
        
        title_text = self.font.render("First to 5 wins!", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 20))
        self.screen.blit(title_text, title_rect)
        
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()