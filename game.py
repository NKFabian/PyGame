import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 800
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TURQUOISE = (64, 224, 208)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
FPS = 60
SPAWN_INTERVAL = 7000  # in milliseconds
MAX_SPEED = 5
MIN_SPEED = 1

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Open World Game")

# Fonts
font = pygame.font.Font(None, 36)

# Helper function to draw a circle
def draw_circle(surface, color, center, radius):
    pygame.draw.circle(surface, color, center, radius)

# Helper function to calculate distance
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Character class
class Character(pygame.sprite.Sprite):
    def __init__(self, name, x, y, color, health, stamina, attack_power):
        super().__init__()
        self.name = name
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        draw_circle(self.image, color, (20, 20), 20)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_health = health
        self.health = health
        self.max_stamina = stamina
        self.stamina = stamina
        self.attack_power = attack_power
        self.weapon = None
        self.direction = 'RIGHT'

    def attack(self, target):
        if self.stamina > 0:
            damage = self.attack_power + (self.weapon.damage if self.weapon else 0)
            target.health -= damage
            self.stamina -= 1

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def restore_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)

# Player class
class Player(Character):
    def __init__(self, x, y):
        super().__init__("Player", x, y, GREEN, 100, 50, 10)
        self.quest_completed = False
        self.points = 0
        self.level_up = False
        self.followers = []
        self.speed = MAX_SPEED
        self.in_red_circle = False
        self.red_circle_timer = 0

    def equip_weapon(self, weapon):
        self.weapon = weapon

    def attack_with_sword(self, target):
        if self.stamina > 0:
            damage = self.max_health * 0.22
            if self.level_up:
                damage *= 1.15
            target.health -= damage
            self.stamina -= 1
            print(f"{self.name} attacks {target.name} with sword for {damage} damage!")

    def level_up_effect(self):
        self.image.fill(TURQUOISE)
        self.attack_power *= 2
        for i in range(2):
            follower = Character(f"Follower{i+1}", self.rect.x + (i * 40), self.rect.y, TURQUOISE, 100, 50, 10)
            self.followers.append(follower)
            all_sprites.add(follower)

    def shoot_ball(self):
        ball = Ball(self.rect.centerx, self.rect.centery, self.direction)
        all_sprites.add(ball)
        balls.add(ball)

    def update(self, dt=0):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = 'LEFT'
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 'RIGHT'
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
            self.direction = 'UP'
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.direction = 'DOWN'

        # Prevent player from moving outside the viewport
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Prevent player from moving through obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if self.direction == 'LEFT':
                    self.rect.left = obstacle.rect.right
                elif self.direction == 'RIGHT':
                    self.rect.right = obstacle.rect.left
                elif self.direction == 'UP':
                    self.rect.top = obstacle.rect.bottom
                elif self.direction == 'DOWN':
                    self.rect.bottom = obstacle.rect.top

        # Adjust player speed based on distance to the nearest mob
        if mobs:
            closest_distance = min([calculate_distance(self.rect.centerx, self.rect.centery, mob.rect.centerx, mob.rect.centery) for mob in mobs])
            self.speed = max(MIN_SPEED, MAX_SPEED - (MAX_SPEED - MIN_SPEED) * (1 - closest_distance / 300))

        # Check if player is in a red circle
        self.in_red_circle = any(pygame.sprite.collide_rect(self, mob) for mob in mobs)
        if self.in_red_circle:
            self.red_circle_timer += dt
            if self.red_circle_timer >= 3000:  # 3 seconds in milliseconds
                end_game()
            elif self.red_circle_timer >= 2000:
                self.image.fill(RED)
            elif self.red_circle_timer >= 1000:
                self.image.fill(ORANGE)
            elif self.red_circle_timer >= 500:
                self.image.fill(YELLOW)
        else:
            self.red_circle_timer = 0
            self.image.fill(GREEN)  # Reset color when not in a red circle

# NPC class
class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        draw_circle(self.image, BLUE, (20, 20), 20)
        self.rect = self.image.get_rect(center=(x, y))

    def give_quest(self, player):
        if not player.quest_completed:
            player.quest_completed = True
            return "Kill all mobs and a boss will appear!"
        return ""

# Mob class
class Mob(Character):
    def __init__(self, x, y):
        super().__init__("Mob", x, y, RED, random.randint(20, 50), 10, random.randint(5, 10))

    def update(self, dt=0):
        # Move towards the player
        direction_vector = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        distance = direction_vector.length()
        if distance != 0:
            direction_vector.normalize_ip()
        self.rect.move_ip(direction_vector * dt / 15)  # Adjust speed as needed

        # End game if mob collides with player
        if pygame.sprite.collide_rect(self, player):
            end_game()

# Boss class
class Boss(Character):
    def __init__(self, x, y):
        super().__init__("Boss", x, y, PURPLE, 200, 50, 20)  # Adjust boss health here
        self.hit_once = False

# Weapon class
class Weapon:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        draw_circle(self.image, PURPLE, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 10

    def update(self, dt=0):
        global boss
        if self.direction == 'LEFT':
            self.rect.x -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
        elif self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'DOWN':
            self.rect.y += self.speed

        if not screen.get_rect().contains(self.rect):
            self.kill()

        # Check collision with mobs
        for mob in mobs:
            if pygame.sprite.collide_rect(self, mob):
                mob.health -= 10  # Damage value for ball hit
                if mob.health <= 0:
                    points = random.randint(0, 10)
                    player.points += points
                    mobs.remove(mob)
                    all_sprites.remove(mob)
                self.kill()

        # Check collision with boss
        if boss and pygame.sprite.collide_rect(self, boss):
            if not boss.hit_once:
                boss.image.fill(YELLOW)
                boss.hit_once = True
            else:
                all_sprites.remove(boss)
                boss = None
                check_win_condition()
            self.kill()

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

def check_win_condition():
    global running
    if not boss:
        running = False
        show_congrats_message()

def show_congrats_message():
    screen.fill(WHITE)
    congrats_surface = font.render("Congrats! You won!", True, (0, 0, 0))
    screen.blit(congrats_surface, (SCREEN_WIDTH // 2 - congrats_surface.get_width() // 2, SCREEN_HEIGHT // 2 - congrats_surface.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Display message for 3 seconds

def end_game():
    global running
    running = False
    show_lose_message()

def show_lose_message():
    screen.fill(WHITE)
    lose_surface = font.render("LLLLLLLLLLLLL", True, (0, 0, 0))
    screen.blit(lose_surface, (SCREEN_WIDTH // 2 - lose_surface.get_width() // 2, SCREEN_HEIGHT // 2 - lose_surface.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Display message for 3 seconds

# Game setup
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
npc = NPC(100, 100)
mobs = pygame.sprite.Group([Mob(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(5)])
obstacles = pygame.sprite.Group([Obstacle(random.randint(0, SCREEN_WIDTH - 50), random.randint(0, SCREEN_HEIGHT - 50), 50, 50) for _ in range(5)])
all_sprites = pygame.sprite.Group([player, npc] + mobs.sprites() + obstacles.sprites())
balls = pygame.sprite.Group()
boss = None
story_displayed = False
story_text = ""

# Timer for spawning mobs
pygame.time.set_timer(pygame.USEREVENT, SPAWN_INTERVAL)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(FPS)  # Get the elapsed time in milliseconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            new_mob = Mob(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            mobs.add(new_mob)
            all_sprites.add(new_mob)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not story_displayed and pygame.sprite.collide_rect(player, npc):
                    story_text = npc.give_quest(player)
                    story_displayed = True
                elif story_displayed:
                    story_displayed = False
                    all_sprites.remove(npc)
                    boss = Boss(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
                    all_sprites.add(boss)
                else:
                    for mob in mobs:
                        if pygame.sprite.collide_rect(player, mob):
                            points = random.randint(0, 10)
                            player.points += points
                            mobs.remove(mob)
                            all_sprites.remove(mob)
                            print(f"Player points: {player.points}")
                            if player.points >= 50 and not player.level_up:
                                player.level_up = True
                                player.level_up_effect()
            elif event.key == pygame.K_k:
                if boss and pygame.sprite.collide_rect(player, boss):
                    player.attack_with_sword(boss)
                else:
                    player.shoot_ball()

    if not mobs and not boss and not story_displayed:
        boss = Boss(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        all_sprites.add(boss)

    for follower in player.followers:
        follower.rect.center = player.rect.center

    balls.update(dt)
    player.update(dt)
    mobs.update(dt)
    all_sprites.update()

    screen.fill(WHITE)
    all_sprites.draw(screen)

    if story_displayed:
        text_surface = font.render(story_text, True, (0, 0, 0))
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - text_surface.get_height() // 2))

    points_surface = font.render(f"Points: {player.points}", True, (0, 0, 0))
    screen.blit(points_surface, (10, 10))

    pygame.display.flip()

pygame.quit()
