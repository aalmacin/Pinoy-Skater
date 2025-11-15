"""
Pinoy Skater - Pygame Web Version (Pygbag Compatible)
A side-scrolling skating game built with Pygame
Compatible with Pygbag for web deployment
"""

import pygame
import random
import asyncio
from typing import List, Optional
from enum import Enum

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Pinoy Skater"
FPS = 60

# Game speeds
INITIAL_OBSTACLE_INTERVAL = 2.5
INITIAL_ITEM_INTERVAL = 1.0
INITIAL_OBJECT_SPEED = 15
SPEED_INCREASE_INTERVAL = 30.0

# Player constants
PLAYER_X = 100
PLAYER_Y = 130
JUMP_HEIGHT = 180  # Increased for higher jumps
JUMP_DURATION = 1.0

# Position constants
BOTTOM_Y = 130
TOP_Y = 300
VERY_TOP_Y = 400

# Lives
MAX_LIVES = 3

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 139)
DARK_RED = (139, 0, 0)


class GameState(Enum):
    """Enum for different game states"""
    START = 1
    INSTRUCTIONS = 2
    PLAYING = 3
    GAME_OVER = 4


class PlayerState(Enum):
    """Enum for player animation states"""
    NORMAL = 0
    JUMPING = 1
    SITTING = 2


class GameObject:
    """Base class for game objects that move across the screen"""

    def __init__(self, image_path: str, y: float, speed: float = 0):
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))

        self.speed = speed
        self.performing = False
        self.initial_y = y

        # Position: x is left edge, y is bottom edge (converted from Arcade coordinates)
        self.x = SCREEN_WIDTH
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        # Convert from Arcade (bottom-origin) to Pygame (top-origin)
        self.rect.bottom = SCREEN_HEIGHT - y

    def update(self, delta_time: float):
        """Update object position"""
        if self.performing:
            # Move left
            self.x -= self.speed
            self.rect.left = self.x

            # Reset when off screen
            if self.x <= -self.rect.width:
                self.reset()

    def reset(self):
        """Reset object to initial position"""
        self.x = SCREEN_WIDTH
        self.rect.left = self.x
        # Convert from Arcade (bottom-origin) to Pygame (top-origin)
        self.rect.bottom = SCREEN_HEIGHT - self.initial_y
        self.performing = False

    def draw(self, screen: pygame.Surface):
        """Draw the sprite"""
        screen.blit(self.image, self.rect)


class Obstacle(GameObject):
    """Obstacle that damages the player"""

    def __init__(self, image_path: str, y: float, sound_path: Optional[str] = None, is_rock: bool = False):
        super().__init__(image_path, y)
        self.sound = None
        if sound_path:
            try:
                self.sound = pygame.mixer.Sound(sound_path)
            except pygame.error as e:
                print(f"Warning: Could not load sound {sound_path}: {e}")

        # For scaling rocks over time
        self.is_rock = is_rock
        self.original_image = self.image.copy()  # Keep original for scaling
        self.scale_factor = 0.5 if is_rock else 1.0  # Rocks start at 50% size

        # Apply initial scale for rocks
        if is_rock:
            new_width = int(self.original_image.get_width() * self.scale_factor)
            new_height = int(self.original_image.get_height() * self.scale_factor)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            # Update rect with new size
            self.rect = self.image.get_rect()
            self.rect.left = self.x
            self.rect.bottom = SCREEN_HEIGHT - y

    def set_scale(self, scale_factor: float):
        """Scale the obstacle image"""
        if self.is_rock:
            self.scale_factor = scale_factor
            # Scale the original image
            new_width = int(self.original_image.get_width() * scale_factor)
            new_height = int(self.original_image.get_height() * scale_factor)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))

            # Update rect size but maintain position
            old_bottom = self.rect.bottom
            old_left = self.rect.left
            self.rect = self.image.get_rect()
            self.rect.left = old_left
            self.rect.bottom = old_bottom

    def play_sound(self):
        """Play hit sound"""
        if self.sound:
            self.sound.play()


class Item(GameObject):
    """Collectible item that gives points and/or health"""

    def __init__(self, image_path: str, y: float, points: int = 0, health: int = 0, sound_path: Optional[str] = None):
        super().__init__(image_path, y)
        self.points = points
        self.health = health  # Amount of health to restore
        self.sound = None
        if sound_path:
            try:
                self.sound = pygame.mixer.Sound(sound_path)
            except pygame.error as e:
                print(f"Warning: Could not load sound {sound_path}: {e}")

    def play_sound(self):
        """Play collection sound"""
        if self.sound:
            self.sound.play()


class Player:
    """The main player character"""

    def __init__(self):
        # Load player sprites for different states
        try:
            self.images = {
                PlayerState.NORMAL: pygame.image.load("images/Skater.png").convert_alpha(),
                PlayerState.JUMPING: pygame.image.load("images/SkaterJump.png").convert_alpha(),
                PlayerState.SITTING: pygame.image.load("images/SkaterSitting.png").convert_alpha()
            }
        except pygame.error as e:
            print(f"Warning: Could not load player images: {e}")
            # Create fallback images
            fallback = pygame.Surface((50, 100))
            fallback.fill((0, 255, 0))
            self.images = {
                PlayerState.NORMAL: fallback,
                PlayerState.JUMPING: fallback.copy(),
                PlayerState.SITTING: fallback.copy()
            }

        self.current_state = PlayerState.NORMAL
        self.current_image = self.images[PlayerState.NORMAL]

        # Position (y is the bottom of the sprite in Arcade coordinates)
        self.x = PLAYER_X
        self.y = PLAYER_Y

        # Create rect for positioning
        self.rect = self.current_image.get_rect()
        self.rect.left = self.x
        # Convert from Arcade (bottom-origin) to Pygame (top-origin)
        self.rect.bottom = SCREEN_HEIGHT - self.y

        # Jump mechanics
        self.is_jumping = False
        self.jump_timer = 0
        self.is_sitting = False

    def update(self, delta_time: float):
        """Update player state and position"""
        # Handle jumping
        if self.is_jumping:
            self.jump_timer += delta_time

            # Simple parabolic jump
            progress = self.jump_timer / JUMP_DURATION
            if progress < 1.0:
                # Parabolic motion
                height = 4 * JUMP_HEIGHT * progress * (1 - progress)
                self.y = PLAYER_Y + height
            else:
                # Jump complete
                self.y = PLAYER_Y
                self.is_jumping = False
                self.jump_timer = 0
                self.current_state = PlayerState.NORMAL
                self.current_image = self.images[PlayerState.NORMAL]
        else:
            self.y = PLAYER_Y

        # Update rect position
        self.rect = self.current_image.get_rect()
        self.rect.left = self.x
        # Convert from Arcade (bottom-origin) to Pygame (top-origin)
        self.rect.bottom = SCREEN_HEIGHT - self.y

    def jump(self):
        """Make the player jump"""
        if not self.is_jumping and not self.is_sitting:
            self.is_jumping = True
            self.jump_timer = 0
            self.current_state = PlayerState.JUMPING
            self.current_image = self.images[PlayerState.JUMPING]

    def sit(self):
        """Make the player sit"""
        if not self.is_jumping and not self.is_sitting:
            self.is_sitting = True
            self.current_state = PlayerState.SITTING
            self.current_image = self.images[PlayerState.SITTING]

    def stand_up(self):
        """Make the player stand up from sitting"""
        if self.is_sitting:
            self.is_sitting = False
            self.current_state = PlayerState.NORMAL
            self.current_image = self.images[PlayerState.NORMAL]

    def draw(self, screen: pygame.Surface):
        """Draw the current player sprite"""
        screen.blit(self.current_image, self.rect)

    def get_hitbox(self) -> pygame.Rect:
        """Get player hitbox for collision detection"""
        # Slightly smaller hitbox for better gameplay
        margin_x = 25
        hitbox = self.rect.copy()
        hitbox.left += margin_x
        hitbox.width -= 2 * margin_x
        return hitbox


class ParallaxLayer:
    """A single parallax scrolling layer"""

    def __init__(self, image_path1: str, image_path2: str, speed: float):
        try:
            self.image1 = pygame.image.load(image_path1).convert_alpha()
            self.image2 = pygame.image.load(image_path2).convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load parallax images: {e}")
            self.image1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image1.fill((100, 100, 255))
            self.image2 = self.image1.copy()

        # Position sprites by their left edge
        self.x1 = 0
        self.x2 = SCREEN_WIDTH

        self.rect1 = self.image1.get_rect()
        self.rect2 = self.image2.get_rect()

        self.rect1.left = self.x1
        self.rect1.bottom = SCREEN_HEIGHT
        self.rect2.left = self.x2
        self.rect2.bottom = SCREEN_HEIGHT

        self.speed = speed

    def update(self, delta_time: float):
        """Update parallax layer position"""
        # Move based on speed
        self.x1 -= self.speed
        self.x2 -= self.speed

        # Reset positions for seamless looping
        if self.x1 <= -SCREEN_WIDTH:
            self.x1 = SCREEN_WIDTH
        if self.x2 <= -SCREEN_WIDTH:
            self.x2 = SCREEN_WIDTH

        # Update rect positions
        self.rect1.left = self.x1
        self.rect2.left = self.x2

    def draw(self, screen: pygame.Surface):
        """Draw both sprites"""
        screen.blit(self.image1, self.rect1)
        screen.blit(self.image2, self.rect2)


class PinoySkaterGame:
    """Main game application"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Create display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)

        # Clock for framerate
        self.clock = pygame.time.Clock()

        # Game state
        self.game_state = GameState.START
        self.running = True

        # UI elements
        self.start_button = None
        self.start_button_rect = None

        # Game objects
        self.player: Optional[Player] = None
        self.obstacles: List[Obstacle] = []
        self.items: List[Item] = []

        # Background
        self.background = None
        self.background_rect = None
        self.parallax_layers: List[ParallaxLayer] = []

        # Game state variables
        self.score = 0
        self.lives = MAX_LIVES
        self.time_elapsed = 0
        self.obstacle_timer = 0
        self.item_timer = 0
        self.heart_timer = 0
        self.heart_interval = random.uniform(20.0, 30.0)  # Random 20-30 seconds
        self.speed_multiplier = 1.0
        self.parallax_timer = 0

        # Sounds
        self.button_click_sound = None
        self.game_over_sound = None

        # Hit effect
        self.hit_sprite = None
        self.hit_sprite_rect = None
        self.hit_timer = 0
        self.show_hit = False

        # Hearts for lives display
        self.heart_image = None
        self.heart_rects = []

        # Fonts
        self.large_font = pygame.font.Font(None, 72)
        self.medium_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)

        # Screen images
        self.start_bg = None
        self.instructions_bg = None
        self.gameover_bg = None

        self.setup()

    def setup(self):
        """Set up the game"""
        # Load sounds
        try:
            self.button_click_sound = pygame.mixer.Sound("sounds/clicked_button.ogg")
            self.game_over_sound = pygame.mixer.Sound("sounds/gameover.ogg")
        except pygame.error as e:
            print(f"Warning: Could not load sound files: {e}")

        # Load background music
        try:
            pygame.mixer.music.load("sounds/bg.ogg")
            pygame.mixer.music.set_volume(0.5)  # Set to 50% volume
        except pygame.error as e:
            print(f"Warning: Could not load background music: {e}")

        # Setup start screen
        self.setup_start_screen()

    def setup_start_screen(self):
        """Setup start screen elements"""
        try:
            # Load and scale background to match screen size
            bg_image = pygame.image.load("images/StartScreenImage.png").convert()
            self.start_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

            self.start_button = pygame.image.load("images/StartButton.png").convert_alpha()
            # Scale button proportionally based on screen size
            scale_factor = min(SCREEN_WIDTH / 1200, SCREEN_HEIGHT / 700)  # Original design was 1200x700
            button_scale = scale_factor * 2
            self.start_button = pygame.transform.scale(self.start_button,
                                                      (int(self.start_button.get_width() * button_scale),
                                                       int(self.start_button.get_height() * button_scale)))
            self.start_button_rect = self.start_button.get_rect()
            # In Pygame, Y increases downward (opposite of Arcade), so + moves down
            self.start_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(100 * scale_factor))
        except pygame.error as e:
            print(f"Warning: Could not load start screen images: {e}")

        try:
            # Load and scale instructions background to match screen size
            inst_image = pygame.image.load("images/InstructionsImage.png").convert()
            self.instructions_bg = pygame.transform.scale(inst_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            pass

        try:
            # Load and scale game over background to match screen size
            go_image = pygame.image.load("images/GameOverScreenImage.png").convert()
            self.gameover_bg = pygame.transform.scale(go_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            pass

    def setup_game(self):
        """Setup game elements"""
        # Reset game state
        self.score = 0
        self.lives = MAX_LIVES
        self.time_elapsed = 0
        self.obstacle_timer = 0
        self.item_timer = 0
        self.heart_timer = 0
        self.heart_interval = random.uniform(20.0, 30.0)  # Random 20-30 seconds
        self.speed_multiplier = 1.0
        self.parallax_timer = 0

        # Start background music (loop indefinitely)
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Warning: Could not play background music: {e}")

        # Create player
        self.player = Player()

        # Setup background
        try:
            self.background = pygame.image.load("images/NonMovingBG.png").convert()
            self.background_rect = self.background.get_rect()
            self.background_rect.left = 0
            self.background_rect.bottom = SCREEN_HEIGHT

            # Setup parallax layers
            self.parallax_layers = [
                ParallaxLayer("images/clouds_01.png", "images/clouds_02.png", 1),
                ParallaxLayer("images/Mountains_01.png", "images/Mountains_02.png", 5),
                ParallaxLayer("images/Road_01.png", "images/Road_02.png", 100)
            ]
        except pygame.error as e:
            print(f"Warning: Background images not found: {e}")
            self.background = None
            self.parallax_layers = []

        # Create obstacles pool
        self.obstacles = []
        try:
            # Rocks - start small and grow to full size after 3 minutes
            for _ in range(5):
                self.obstacles.append(
                    Obstacle("images/Rock.png", BOTTOM_Y, "sounds/ouch.ogg", is_rock=True)
                )
            # Birds - always full size
            for _ in range(5):
                self.obstacles.append(
                    Obstacle("images/Bird.png", TOP_Y, "sounds/ouch.ogg", is_rock=False)
                )
        except Exception as e:
            print(f"Warning: Could not create obstacles: {e}")

        # Create items pool (no hearts here - they spawn on timer)
        self.items = []
        try:
            # Candy (top) - high points
            for _ in range(5):
                self.items.append(
                    Item("images/Candy.png", VERY_TOP_Y, points=200, sound_path="sounds/candy.ogg")
                )
            # Coins (bottom) - medium points
            for _ in range(10):
                self.items.append(
                    Item("images/Coin.png", BOTTOM_Y, points=100, sound_path="sounds/coin_pickup.ogg")
                )
        except Exception as e:
            print(f"Warning: Could not create items: {e}")

        # Create heart item (single item, spawns rarely)
        self.heart = None
        try:
            self.heart = Item("images/Heart.png", TOP_Y, points=50, health=1, sound_path="sounds/coin_pickup.ogg")
        except Exception as e:
            print(f"Warning: Could not create heart item: {e}")

        # Setup hit effect
        try:
            self.hit_sprite = pygame.image.load("images/Hit.png").convert_alpha()
            self.hit_sprite_rect = self.hit_sprite.get_rect()
        except pygame.error:
            print("Warning: Hit effect image not found")

        # Setup heart sprites for lives
        try:
            self.heart_image = pygame.image.load("images/Heart.png").convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image,
                                                     (int(self.heart_image.get_width() * 0.8),
                                                      int(self.heart_image.get_height() * 0.8)))
            self.heart_rects = []
            for i in range(MAX_LIVES):
                rect = self.heart_image.get_rect()
                rect.left = 30 + i * 55
                rect.top = 30
                self.heart_rects.append(rect)
        except pygame.error:
            print("Warning: Heart image not found")

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.on_mouse_press(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.game_state == GameState.PLAYING:
                    self.on_mouse_motion(event.pos)

            elif event.type == pygame.KEYDOWN:
                self.on_key_press(event.key)

            elif event.type == pygame.KEYUP:
                self.on_key_release(event.key)

    def on_mouse_press(self, pos):
        """Handle mouse clicks"""
        if self.game_state == GameState.START:
            if self.start_button_rect and self.start_button_rect.collidepoint(pos):
                if self.button_click_sound:
                    self.button_click_sound.play()
                self.game_state = GameState.INSTRUCTIONS
            elif not self.start_button_rect:
                self.game_state = GameState.INSTRUCTIONS

        elif self.game_state == GameState.INSTRUCTIONS:
            if self.button_click_sound:
                self.button_click_sound.play()
            self.setup_game()
            self.game_state = GameState.PLAYING

        elif self.game_state == GameState.GAME_OVER:
            if self.button_click_sound:
                self.button_click_sound.play()
            self.setup_game()
            self.game_state = GameState.PLAYING

    def on_mouse_motion(self, pos):
        """Handle mouse motion"""
        if self.player:
            x, y = pos
            # In Pygame, Y=0 is at top, Y increases downward
            # Convert thresholds from Arcade coordinates
            # Arcade: y > 400 = very high, y <= 120 = very low
            # Pygame: y < 300 = very high (jump), y > 580 = very low (sit)
            if y < 300:  # Mouse at top of screen
                self.player.jump()
            elif y >= 300 and y < 580:  # Mouse in middle
                self.player.stand_up()
            elif y >= 580:  # Mouse at bottom
                self.player.sit()

    def on_key_press(self, key):
        """Handle key presses"""
        if self.game_state == GameState.PLAYING and self.player:
            if key in (pygame.K_w, pygame.K_UP):
                self.player.jump()
            elif key in (pygame.K_s, pygame.K_DOWN):
                self.player.sit()

    def on_key_release(self, key):
        """Handle key releases"""
        if self.game_state == GameState.PLAYING and self.player:
            if key in (pygame.K_s, pygame.K_DOWN):
                self.player.stand_up()

    def update(self, delta_time: float):
        """Update game logic"""
        if self.game_state == GameState.PLAYING:
            self.update_game(delta_time)

    def update_game(self, delta_time: float):
        """Update game state"""
        # Update time
        self.time_elapsed += delta_time

        # Update speed multiplier
        self.speed_multiplier = 1.0 + (int(self.time_elapsed / SPEED_INCREASE_INTERVAL) * 0.5)

        # Update rock scale - for the first minute, all rocks grow uniformly
        # After 1 minute, rocks spawn with random sizes (set in spawn_obstacle)
        if self.time_elapsed < 60.0:
            # First minute: gradually grow from 50% to 100%
            rock_scale_progress = min(self.time_elapsed / 60.0, 1.0)  # 60 seconds = 1 minute
            rock_scale = 0.5 + (rock_scale_progress * 0.5)  # Scale from 0.5 to 1.0
            for obstacle in self.obstacles:
                if obstacle.is_rock:
                    obstacle.set_scale(rock_scale)

        # Update parallax layers
        self.parallax_timer += delta_time
        if self.parallax_timer >= 0.1:
            for layer in self.parallax_layers:
                layer.update(0.1)
            self.parallax_timer = 0

        # Update player
        if self.player:
            self.player.update(delta_time)

        # Spawn obstacles
        self.obstacle_timer += delta_time
        if self.obstacle_timer >= INITIAL_OBSTACLE_INTERVAL:
            self.spawn_obstacle()
            self.obstacle_timer = 0

        # Spawn items
        self.item_timer += delta_time
        if self.item_timer >= INITIAL_ITEM_INTERVAL:
            self.spawn_item()
            self.item_timer = 0

        # Spawn heart (rare, every 20-30 seconds)
        self.heart_timer += delta_time
        if self.heart_timer >= self.heart_interval:
            self.spawn_heart()
            self.heart_timer = 0
            # Set next random interval
            self.heart_interval = random.uniform(20.0, 30.0)

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.speed = INITIAL_OBJECT_SPEED * self.speed_multiplier
            obstacle.update(delta_time)

        # Update items
        for item in self.items:
            item.speed = INITIAL_OBJECT_SPEED * self.speed_multiplier
            item.update(delta_time)

        # Update heart
        if self.heart and self.heart.performing:
            self.heart.speed = INITIAL_OBJECT_SPEED * self.speed_multiplier
            self.heart.update(delta_time)

        # Check collisions
        self.check_collisions()

        # Update hit effect
        if self.show_hit:
            self.hit_timer += delta_time
            if self.hit_timer >= 0.5:
                self.show_hit = False
                self.hit_timer = 0

        # Check game over
        if self.lives <= 0:
            self.game_state = GameState.GAME_OVER
            if self.game_over_sound:
                self.game_over_sound.play()

    def spawn_obstacle(self):
        """Spawn a random obstacle"""
        available = [obs for obs in self.obstacles if not obs.performing]
        if available:
            obstacle = random.choice(available)
            obstacle.performing = True
            obstacle.x = SCREEN_WIDTH
            obstacle.rect.left = obstacle.x
            # Convert from Arcade (bottom-origin) to Pygame (top-origin)
            obstacle.rect.bottom = SCREEN_HEIGHT - obstacle.initial_y

            # After 1 minute, assign random size to rocks for variety
            if obstacle.is_rock and self.time_elapsed >= 60.0:
                random_scale = random.uniform(0.5, 1.0)  # Random size between 50% and 100%
                obstacle.set_scale(random_scale)

    def spawn_item(self):
        """Spawn a random item"""
        available = [item for item in self.items if not item.performing]
        if available:
            item = random.choice(available)
            item.performing = True
            item.x = SCREEN_WIDTH
            item.rect.left = item.x
            # Convert from Arcade (bottom-origin) to Pygame (top-origin)
            item.rect.bottom = SCREEN_HEIGHT - item.initial_y

    def spawn_heart(self):
        """Spawn the heart (rare health item)"""
        if self.heart and not self.heart.performing:
            self.heart.performing = True
            self.heart.x = SCREEN_WIDTH
            self.heart.rect.left = self.heart.x
            # Convert from Arcade (bottom-origin) to Pygame (top-origin)
            self.heart.rect.bottom = SCREEN_HEIGHT - self.heart.initial_y

    def check_collisions(self):
        """Check for collisions between player and objects"""
        if not self.player:
            return

        player_hitbox = self.player.get_hitbox()

        # Check obstacle collisions
        for obstacle in self.obstacles:
            if obstacle.performing:
                if player_hitbox.colliderect(obstacle.rect):
                    obstacle.reset()
                    obstacle.play_sound()
                    self.lives -= 1

                    # Show hit effect
                    self.show_hit = True
                    self.hit_timer = 0
                    if self.hit_sprite_rect:
                        self.hit_sprite_rect.left = self.player.x + obstacle.rect.width
                        self.hit_sprite_rect.centery = obstacle.rect.centery

        # Check item collisions
        for item in self.items:
            if item.performing:
                if player_hitbox.colliderect(item.rect):
                    item.reset()
                    item.play_sound()
                    self.score += item.points

        # Check heart collision
        if self.heart and self.heart.performing:
            if player_hitbox.colliderect(self.heart.rect):
                self.heart.reset()
                self.heart.play_sound()
                self.score += self.heart.points
                # Restore health
                self.lives = min(self.lives + self.heart.health, MAX_LIVES)

    def draw(self):
        """Render the screen"""
        self.screen.fill(SKY_BLUE)

        if self.game_state == GameState.START:
            self.draw_start_screen()
        elif self.game_state == GameState.INSTRUCTIONS:
            self.draw_instructions_screen()
        elif self.game_state == GameState.PLAYING:
            self.draw_game_screen()
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_start_screen(self):
        """Draw the start screen"""
        if self.start_bg:
            self.screen.blit(self.start_bg, (0, 0))

        if self.start_button and self.start_button_rect:
            self.screen.blit(self.start_button, self.start_button_rect)
        else:
            # Fallback text
            title = self.large_font.render("PINOY SKATER", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(title, title_rect)

            start_text = self.medium_font.render("Click to Start", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(start_text, start_rect)

    def draw_instructions_screen(self):
        """Draw the instructions screen"""
        if self.instructions_bg:
            self.screen.blit(self.instructions_bg, (0, 0))
        else:
            self.screen.fill(DARK_BLUE)

        # Draw title
        title = self.medium_font.render("HOW TO PLAY", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Draw instructions
        instructions = [
            "Move mouse UP or press W to JUMP",
            "Move mouse DOWN or press S to DUCK",
            "",
            "Avoid obstacles (rocks and birds)",
            "Collect coins and candy for points",
            "",
            "Click to continue..."
        ]

        y_pos = SCREEN_HEIGHT // 2 + 100
        for line in instructions:
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos -= 40

    def draw_game_screen(self):
        """Draw the game screen"""
        # Draw background
        if self.background:
            self.screen.blit(self.background, self.background_rect)

        # Draw parallax layers
        for layer in self.parallax_layers:
            layer.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            if obstacle.performing:
                obstacle.draw(self.screen)

        # Draw items
        for item in self.items:
            if item.performing:
                item.draw(self.screen)

        # Draw heart (if spawned)
        if self.heart and self.heart.performing:
            self.heart.draw(self.screen)

        # Draw player
        if self.player:
            self.player.draw(self.screen)

        # Draw hit effect
        if self.show_hit and self.hit_sprite:
            self.screen.blit(self.hit_sprite, self.hit_sprite_rect)

        # Draw lives (hearts)
        if self.heart_image:
            for i, rect in enumerate(self.heart_rects):
                if i < self.lives:
                    self.screen.blit(self.heart_image, rect)

        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 70))

    def draw_game_over_screen(self):
        """Draw the game over screen"""
        if self.gameover_bg:
            self.screen.blit(self.gameover_bg, (0, 0))
        else:
            self.screen.fill(DARK_RED)

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Draw game over text
        title = self.large_font.render("GAME OVER", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(title, title_rect)

        score_text = self.medium_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        restart_text = self.small_font.render("Click to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(restart_text, restart_rect)

    async def run(self):
        """Main game loop (async for pygbag compatibility)"""
        while self.running:
            # Calculate delta time
            delta_time = self.clock.tick(FPS) / 1000.0

            # Handle events
            self.handle_events()

            # Update game state
            self.update(delta_time)

            # Draw everything
            self.draw()

            # Yield control to the browser (required for pygbag)
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    """Main function to run the game"""
    game = PinoySkaterGame()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
