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
        self.width = 50
        self.height = 30
        self.speed = 5
        self.bullets = []
        self.shoot_cooldown = 0
        
    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
            
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet = Bullet(self.x + self.width // 2, self.y, -8, CYAN)
            self.bullets.append(bullet)
            self.shoot_cooldown = 15
            
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
                
    def draw(self, screen):
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        for bullet in self.bullets:
            bullet.draw(screen)

class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed_x = 1
        self.speed_y = 20
        self.enemy_type = enemy_type
        self.colors = [RED, PURPLE, YELLOW]
        self.points = [10, 20, 30]
        
    def move(self):
        self.x += self.speed_x
        
    def move_down(self):
        self.y += self.speed_y
        self.speed_x *= -1
        
    def draw(self, screen):
        color = self.colors[self.enemy_type % len(self.colors)]
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, 10, 10))
        pygame.draw.rect(screen, WHITE, (self.x + 25, self.y + 5, 10, 10))

class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 3
        self.height = 10
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Modern Invader Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 50)
        self.enemies = []
        self.enemy_bullets = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.victory = False
        self.enemy_shoot_timer = 0
        self.create_enemies()
        
    def create_enemies(self):
        for row in range(5):
            for col in range(10):
                enemy_type = row // 2
                x = col * 60 + 80
                y = row * 50 + 50
                self.enemies.append(Enemy(x, y, enemy_type))
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.shoot()
                if event.key == pygame.K_r and (self.game_over or self.victory):
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
        
    def update(self):
        if self.game_over or self.victory:
            return
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
            
        self.player.update()
        
        should_move_down = False
        for enemy in self.enemies:
            enemy.move()
            if enemy.x <= 0 or enemy.x >= SCREEN_WIDTH - enemy.width:
                should_move_down = True
                
        if should_move_down:
            for enemy in self.enemies:
                enemy.move_down()
                
        self.enemy_shoot_timer += 1
        if self.enemy_shoot_timer > 60 and self.enemies:
            if random.random() < 0.02:
                shooter = random.choice(self.enemies)
                bullet = Bullet(shooter.x + shooter.width // 2, shooter.y + shooter.height, 4, RED)
                self.enemy_bullets.append(bullet)
            self.enemy_shoot_timer = 0
            
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.enemy_bullets.remove(bullet)
                
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet.x < enemy.x + enemy.width and 
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and 
                    bullet.y + bullet.height > enemy.y):
                    self.score += enemy.points[enemy.enemy_type]
                    self.enemies.remove(enemy)
                    self.player.bullets.remove(bullet)
                    break
                    
        for bullet in self.enemy_bullets[:]:
            if (bullet.x < self.player.x + self.player.width and 
                bullet.x + bullet.width > self.player.x and
                bullet.y < self.player.y + self.player.height and 
                bullet.y + bullet.height > self.player.y):
                self.lives -= 1
                self.enemy_bullets.remove(bullet)
                if self.lives <= 0:
                    self.game_over = True
                    
        for enemy in self.enemies:
            if enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                
        if not self.enemies:
            self.victory = True
            
    def draw(self):
        self.screen.fill(BLACK)
        
        for i in range(0, SCREEN_WIDTH, 2):
            for j in range(0, SCREEN_HEIGHT, 2):
                if random.random() < 0.001:
                    pygame.draw.rect(self.screen, WHITE, (i, j, 1, 1))
        
        if not (self.game_over or self.victory):
            self.player.draw(self.screen)
            
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
            
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
            
        if self.victory:
            victory_text = self.big_font.render("VICTORY!", True, GREEN)
            restart_text = self.font.render("Press R to Play Again", True, WHITE)
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(victory_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
            
        controls_text = self.font.render("Controls: A/D or Arrow Keys to move, SPACE to shoot, ESC to quit", True, WHITE)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
        self.screen.blit(controls_text, controls_rect)
        
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