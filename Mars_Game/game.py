import pygame
import sys
import random
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Explorer: Curiosity Path")


MARS_RED = (210, 125, 70)
WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)
BROWN = (101, 67, 33)
CYAN = (0, 255, 255)
SAND = (194, 178, 128)


BASE_PATH = os.path.dirname(__file__)

try:
    rover_img = pygame.image.load(os.path.join(BASE_PATH, "rover.png")).convert_alpha()
    ROVER_IMG = pygame.transform.scale(rover_img, (60, 40))
    crystal_img = pygame.image.load(os.path.join(BASE_PATH, "crystal.png")).convert_alpha()
    CRYSTAL_IMG = pygame.transform.scale(crystal_img, (30, 30))
except:
    ROVER_IMG = pygame.Surface((60, 40));
    ROVER_IMG.fill(DARK_GREY)
    CRYSTAL_IMG = pygame.Surface((30, 30));
    CRYSTAL_IMG.fill(CYAN)


class Particle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.size = random.randint(2, 5)
        self.life = 20
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-1, 1)

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, SAND, (int(self.x), int(self.y)), self.size)


class Rover(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ROVER_IMG
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed, self.energy = 5, 100

    def update(self, keys):
        old_pos = self.rect.copy()
        moved = False
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed; moved = True
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed; moved = True
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed; moved = True
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed; moved = True
        if moved: self.energy -= 0.15
        return old_pos, moved


class Stone(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(30, 60)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, BROWN, [0, 0, size, size])
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH - size), y=random.randint(0, HEIGHT - size))


class Crystal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = CRYSTAL_IMG
        self.rect = self.image.get_rect(x=random.randint(50, WIDTH - 50), y=random.randint(50, HEIGHT - 50))


def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size, bold=True)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def main_menu():
    clock = pygame.time.Clock()
    while True:
        screen.fill(DARK_GREY)
        draw_text("MARS EXPLORER", 60, WIDTH // 2 - 200, HEIGHT // 3)
        draw_text("Press SPACE to Start", 30, WIDTH // 2 - 130, HEIGHT // 2 + 60)
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: return


def end_screen(title, message, color):
    while True:
        screen.fill(DARK_GREY)
        draw_text(title, 60, WIDTH // 2 - 180, HEIGHT // 3, color)
        draw_text(message, 30, WIDTH // 2 - 150, HEIGHT // 2, WHITE)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit();
                sys.exit()


def game_loop():
    clock = pygame.time.Clock()
    rover = Rover()
    all_sprites = pygame.sprite.Group(rover)
    stones = pygame.sprite.Group()
    crystals = pygame.sprite.Group()
    particles, score = [], 0

    for _ in range(8):
        s = Stone();
        stones.add(s);
        all_sprites.add(s)
    for _ in range(5):
        c = Crystal();
        crystals.add(c);
        all_sprites.add(c)

    running = True
    while running:
        clock.tick(60)
        screen.fill(MARS_RED)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        old_pos, moved = rover.update(keys)

        if moved:
            for _ in range(2): particles.append(Particle(rover.rect.centerx, rover.rect.centery))

        if pygame.sprite.spritecollide(rover, stones, False): rover.rect = old_pos

        collected = pygame.sprite.spritecollide(rover, crystals, True)
        for _ in collected:
            score += 1;
            rover.energy = min(100, rover.energy + 15)
            new_c = Crystal();
            crystals.add(new_c);
            all_sprites.add(new_c)

        for p in particles[:]:
            p.move();
            p.draw(screen)
            if p.life <= 0: particles.remove(p)

        all_sprites.draw(screen)
        draw_text(f"ENERGY: {int(rover.energy)}%", 24, 20, 20)
        draw_text(f"CRYSTALS: {score}/10", 24, 20, 50)

        if score >= 10: end_screen("MISSION SUCCESS", f"Collected {score} crystals!", CYAN)
        if rover.energy <= 0: end_screen("MISSION FAILED", "Out of energy.", (255, 50, 50))

        pygame.display.flip()


main_menu()
game_loop()