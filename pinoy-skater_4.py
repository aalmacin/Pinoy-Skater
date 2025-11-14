"""
Pinoy Skater - Modern Version
A side-scrolling skating game built with Python Arcade library
Compatible with Python 3.13.5+
"""

import arcade
import random
from typing import List, Optional
from enum import Enum

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Pinoy Skater"

# Game speeds
INITIAL_OBSTACLE_INTERVAL = 3.0
INITIAL_ITEM_INTERVAL = 1.0
INITIAL_OBJECT_SPEED = 10
SPEED_INCREASE_INTERVAL = 30.0

# Player constants
PLAYER_X = 100
PLAYER_Y = 130
JUMP_HEIGHT = 30
JUMP_DURATION = 1.0

# Position constants
BOTTOM_Y = 130
TOP_Y = 300
VERY_TOP_Y = 400

# Lives
MAX_LIVES = 3


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
        self.sprite = arcade.Sprite(image_path)
        self.speed = speed
        self.performing = False
        self.initial_y = y

        # Position sprite: x starts at 1200 (right edge), y is bottom of sprite
        # In Arcade, positioning is by center, so adjust
        self.x = SCREEN_WIDTH  # Start at right edge (1200)
        self.sprite.center_x = self.x + self.sprite.width / 2
        self.sprite.center_y = y + self.sprite.height / 2

    def update(self, delta_time: float):
        """Update object position"""
        if self.performing:
            # Move left
            self.x -= self.speed
            self.sprite.center_x = self.x + self.sprite.width / 2

            # Reset when off screen (left edge)
            if self.x <= -self.sprite.width:
                self.reset()

    def reset(self):
        """Reset object to initial position"""
        self.x = SCREEN_WIDTH
        self.sprite.center_x = self.x + self.sprite.width / 2
        self.sprite.center_y = self.initial_y + self.sprite.height / 2
        self.performing = False

    def draw(self):
        """Draw the sprite"""
        arcade.draw_sprite(self.sprite)


class Obstacle(GameObject):
    """Obstacle that damages the player"""

    def __init__(self, image_path: str, y: float, sound_path: Optional[str] = None):
        super().__init__(image_path, y)
        try:
            self.sound = arcade.load_sound(sound_path) if sound_path else None
        except Exception as e:
            print(f"Warning: Could not load sound {sound_path}: {e}")
            self.sound = None

    def play_sound(self):
        """Play hit sound"""
        if self.sound:
            arcade.play_sound(self.sound)


class Item(GameObject):
    """Collectible item that gives points"""

    def __init__(self, image_path: str, y: float, points: int, sound_path: Optional[str] = None):
        super().__init__(image_path, y)
        self.points = points
        try:
            self.sound = arcade.load_sound(sound_path) if sound_path else None
        except Exception as e:
            print(f"Warning: Could not load sound {sound_path}: {e}")
            self.sound = None

    def play_sound(self):
        """Play collection sound"""
        if self.sound:
            arcade.play_sound(self.sound)


class Player:
    """The main player character"""

    def __init__(self):
        # Load player sprites for different states
        self.sprites = {
            PlayerState.NORMAL: arcade.Sprite("images/Skater.png"),
            PlayerState.JUMPING: arcade.Sprite("images/SkaterJump.png"),
            PlayerState.SITTING: arcade.Sprite("images/SkaterSitting.png")
        }

        self.current_state = PlayerState.NORMAL
        self.current_sprite = self.sprites[PlayerState.NORMAL]

        # Position (y is the bottom of the sprite in original)
        self.x = PLAYER_X
        self.y = PLAYER_Y  # This is the bottom position

        # Set initial position (convert from bottom to center)
        for sprite in self.sprites.values():
            sprite.center_x = self.x + sprite.width / 2
            sprite.center_y = self.y + sprite.height / 2

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
                self.current_sprite = self.sprites[PlayerState.NORMAL]
        else:
            self.y = PLAYER_Y

        # Update all sprite positions
        for sprite in self.sprites.values():
            sprite.center_x = self.x + sprite.width / 2
            sprite.center_y = self.y + sprite.height / 2

    def jump(self):
        """Make the player jump"""
        if not self.is_jumping and not self.is_sitting:
            self.is_jumping = True
            self.jump_timer = 0
            self.current_state = PlayerState.JUMPING
            self.current_sprite = self.sprites[PlayerState.JUMPING]

    def sit(self):
        """Make the player sit"""
        if not self.is_jumping and not self.is_sitting:
            self.is_sitting = True
            self.current_state = PlayerState.SITTING
            self.current_sprite = self.sprites[PlayerState.SITTING]

    def stand_up(self):
        """Make the player stand up from sitting"""
        if self.is_sitting:
            self.is_sitting = False
            self.current_state = PlayerState.NORMAL
            self.current_sprite = self.sprites[PlayerState.NORMAL]

    def draw(self):
        """Draw the current player sprite"""
        arcade.draw_sprite(self.current_sprite)

    def get_hitbox(self) -> tuple:
        """Get player hitbox for collision detection (x, y, width, height)"""
        # Return bottom-left x, y and dimensions
        # Slightly smaller hitbox for better gameplay (50px margin on x as in original)
        margin_x = 25
        return (
            self.x + margin_x,
            self.y,
            self.current_sprite.width - 2 * margin_x,
            self.current_sprite.height
        )


class ParallaxLayer:
    """A single parallax scrolling layer"""

    def __init__(self, image_path1: str, image_path2: str, speed: float):
        # Create two sprites for seamless scrolling
        # Position sprites at their left edge (x position), bottom-aligned
        self.sprite1 = arcade.Sprite(image_path1)
        self.sprite2 = arcade.Sprite(image_path2)

        # Position sprites by their left edge, starting at x=0 and x=SCREEN_WIDTH
        self.x1 = 0
        self.x2 = SCREEN_WIDTH

        # Update sprite positions (convert from left-edge to center)
        self.sprite1.center_x = self.x1 + self.sprite1.width / 2
        self.sprite1.center_y = self.sprite1.height / 2
        self.sprite2.center_x = self.x2 + self.sprite2.width / 2
        self.sprite2.center_y = self.sprite2.height / 2

        self.speed = speed

    def update(self, delta_time: float):
        """Update parallax layer position"""
        # Move based on speed (called every 0.1 seconds like original)
        self.x1 -= self.speed
        self.x2 -= self.speed

        # Reset positions for seamless looping
        if self.x1 <= -SCREEN_WIDTH:
            self.x1 = SCREEN_WIDTH
        if self.x2 <= -SCREEN_WIDTH:
            self.x2 = SCREEN_WIDTH

        # Update sprite positions
        self.sprite1.center_x = self.x1 + self.sprite1.width / 2
        self.sprite2.center_x = self.x2 + self.sprite2.width / 2

    def draw(self):
        """Draw both sprites"""
        arcade.draw_sprite(self.sprite1)
        arcade.draw_sprite(self.sprite2)


class PinoySkaterGame(arcade.Window):
    """Main game application"""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set background color
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Game state
        self.game_state = GameState.START

        # UI elements
        self.start_button: Optional[arcade.Sprite] = None
        self.instructions_button: Optional[arcade.Sprite] = None
        self.restart_button: Optional[arcade.Sprite] = None

        # Game objects
        self.player: Optional[Player] = None
        self.obstacles: List[Obstacle] = []
        self.items: List[Item] = []

        # Background
        self.background: Optional[arcade.Sprite] = None
        self.parallax_layers: List[ParallaxLayer] = []

        # Game state
        self.score = 0
        self.lives = MAX_LIVES
        self.time_elapsed = 0
        self.obstacle_timer = 0
        self.item_timer = 0
        self.speed_multiplier = 1.0
        self.parallax_timer = 0  # For updating parallax every 0.1 seconds

        # Sounds
        self.button_click_sound: Optional[arcade.Sound] = None
        self.game_over_sound: Optional[arcade.Sound] = None
        self.background_music: Optional[arcade.Sound] = None

        # Hit effect
        self.hit_sprite: Optional[arcade.Sprite] = None
        self.hit_timer = 0
        self.show_hit = False

        # Hearts for lives display
        self.heart_sprites: List[arcade.Sprite] = []

        self.setup()

    def setup(self):
        """Set up the game"""
        # Load sounds (with error handling for missing files)
        try:
            self.button_click_sound = arcade.load_sound("sounds/clicked_button.ogg")
            self.game_over_sound = arcade.load_sound("sounds/gameover.ogg")
            # Note: arcade doesn't have built-in music looping like pygame
            # You would need to handle music separately or use pygame.mixer
        except FileNotFoundError as e:
            print(f"Warning: Could not load sound file: {e}")

        # Setup start screen
        self.setup_start_screen()

    def setup_start_screen(self):
        """Setup start screen elements"""
        try:
            self.start_button = arcade.Sprite("images/StartButton.png",
                                            center_x=SCREEN_WIDTH // 2,
                                            center_y=SCREEN_HEIGHT // 2 - 100,
                                            scale=2)
        except Exception as e:
            print(f"Warning: Start button image not found: {e}")
            self.start_button = None

    def setup_game(self):
        """Setup game elements"""
        # Reset game state
        self.score = 0
        self.lives = MAX_LIVES
        self.time_elapsed = 0
        self.obstacle_timer = 0
        self.item_timer = 0
        self.speed_multiplier = 1.0
        self.parallax_timer = 0

        # Create player
        self.player = Player()

        # Setup background (try to load images, fallback to colors)
        try:
            self.background = arcade.Sprite("images/NonMovingBG.png")
            self.background.center_x = self.background.width / 2
            self.background.center_y = self.background.height / 2

            # Setup parallax layers (each needs two images for seamless scrolling)
            self.parallax_layers = [
                ParallaxLayer("images/clouds_01.png", "images/clouds_02.png", 1),
                ParallaxLayer("images/Mountains_01.png", "images/Mountains_02.png", 5),
                ParallaxLayer("images/Road_01.png", "images/Road_02.png", 100)
            ]
        except FileNotFoundError as e:
            print(f"Warning: Background images not found: {e}")
            self.background = None
            self.parallax_layers = []

        # Create obstacles pool
        self.obstacles = []
        try:
            # Rocks
            for _ in range(5):
                self.obstacles.append(
                    Obstacle("images/Rock.png", BOTTOM_Y, "sounds/ouch.ogg")
                )
            # Birds
            for _ in range(5):
                self.obstacles.append(
                    Obstacle("images/Bird.png", TOP_Y, "sounds/ouch.ogg")
                )
            print(f"Created {len(self.obstacles)} obstacles")
        except FileNotFoundError as e:
            print(f"Warning: Could not load obstacle images: {e}")

        # Create items pool
        self.items = []
        try:
            # Candy (top)
            for _ in range(5):
                self.items.append(
                    Item("images/Candy.png", VERY_TOP_Y, 200, "sounds/candy.ogg")
                )
            # Coins (bottom)
            for _ in range(10):
                self.items.append(
                    Item("images/Coin.png", BOTTOM_Y, 100, "sounds/coin_pickup.ogg")
                )
            print(f"Created {len(self.items)} items")
        except FileNotFoundError as e:
            print(f"Warning: Could not load item images: {e}")

        # Setup hit effect
        try:
            self.hit_sprite = arcade.Sprite("images/Hit.png")
        except FileNotFoundError:
            print("Warning: Hit effect image not found")

        # Setup heart sprites for lives
        self.heart_sprites = []
        try:
            for i in range(MAX_LIVES):
                heart = arcade.Sprite("images/Heart.png",
                                     center_x=30 + i * 55,
                                     center_y=SCREEN_HEIGHT - 30,
                                     scale=0.8)
                self.heart_sprites.append(heart)
        except FileNotFoundError:
            print("Warning: Heart image not found")

    def on_draw(self):
        """Render the screen"""
        self.clear()

        if self.game_state == GameState.START:
            self.draw_start_screen()
        elif self.game_state == GameState.INSTRUCTIONS:
            self.draw_instructions_screen()
        elif self.game_state == GameState.PLAYING:
            self.draw_game_screen()
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game_over_screen()

    def draw_start_screen(self):
        """Draw the start screen"""
        # Draw background
        try:
            start_bg = arcade.Sprite("images/StartScreenImage.png",
                                    center_x=SCREEN_WIDTH // 2,
                                    center_y=SCREEN_HEIGHT // 2)
            arcade.draw_sprite(start_bg)
        except Exception:
            pass

        # Draw start button
        if self.start_button:
            arcade.draw_sprite(self.start_button)
        else:
            # Fallback text
            arcade.draw_text("PINOY SKATER",
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                           arcade.color.WHITE, 54, anchor_x="center", bold=True)
            arcade.draw_text("Click to Start",
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                           arcade.color.WHITE, 32, anchor_x="center")

    def draw_instructions_screen(self):
        """Draw the instructions screen"""
        # Draw background
        try:
            inst_bg = arcade.Sprite("images/InstructionsImage.png",
                                   center_x=SCREEN_WIDTH // 2,
                                   center_y=SCREEN_HEIGHT // 2)
            arcade.draw_sprite(inst_bg)
        except:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                             arcade.color.DARK_BLUE)

        # Draw instructions text
        arcade.draw_text("HOW TO PLAY",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                        arcade.color.WHITE, 44, anchor_x="center", bold=True)

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
            arcade.draw_text(line, SCREEN_WIDTH // 2, y_pos,
                           arcade.color.WHITE, 24, anchor_x="center")
            y_pos -= 40

    def draw_game_screen(self):
        """Draw the game screen"""
        # Draw background
        if self.background:
            arcade.draw_sprite(self.background)

        # Draw parallax layers
        for layer in self.parallax_layers:
            layer.draw()

        # Draw obstacles
        performing_obstacles = 0
        for obstacle in self.obstacles:
            if obstacle.performing:
                performing_obstacles += 1
                obstacle.draw()

        # Draw items
        performing_items = 0
        for item in self.items:
            if item.performing:
                performing_items += 1
                item.draw()

        # Draw player
        if self.player:
            self.player.draw()

        # Draw hit effect
        if self.show_hit and self.hit_sprite:
            arcade.draw_sprite(self.hit_sprite)

        # Draw lives (hearts)
        for i, heart in enumerate(self.heart_sprites):
            if i < self.lives:
                arcade.draw_sprite(heart)

        # Draw score
        arcade.draw_text(f"Score: {self.score}",
                        10, SCREEN_HEIGHT - 70,
                        arcade.color.WHITE, 28, bold=True)

    def draw_game_over_screen(self):
        """Draw the game over screen"""
        # Draw background
        try:
            gameover_bg = arcade.Sprite("images/GameOverScreenImage.png",
                                       center_x=SCREEN_WIDTH // 2,
                                       center_y=SCREEN_HEIGHT // 2)
            arcade.draw_sprite(gameover_bg)
        except:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                             arcade.color.DARK_RED)

        # Draw semi-transparent overlay to make text more visible
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                         (0, 0, 0, 180))  # Black with 180/255 alpha (semi-transparent)

        # Draw game over text
        arcade.draw_text("GAME OVER",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                        arcade.color.WHITE, 54, anchor_x="center", bold=True)

        arcade.draw_text(f"Final Score: {self.score}",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                        arcade.color.WHITE, 32, anchor_x="center")

        arcade.draw_text("Click to Restart",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                        arcade.color.WHITE, 24, anchor_x="center")

    def on_update(self, delta_time: float):
        """Update game logic"""
        if self.game_state == GameState.PLAYING:
            self.update_game(delta_time)

    def update_game(self, delta_time: float):
        """Update game state"""
        # Update time
        self.time_elapsed += delta_time

        # Update speed multiplier every 30 seconds
        self.speed_multiplier = 1.0 + (int(self.time_elapsed / SPEED_INCREASE_INTERVAL) * 0.5)

        # Update parallax layers every 0.1 seconds (like original)
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

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.speed = INITIAL_OBJECT_SPEED * self.speed_multiplier
            obstacle.update(delta_time)

        # Update items
        for item in self.items:
            item.speed = INITIAL_OBJECT_SPEED * self.speed_multiplier
            item.update(delta_time)

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
                arcade.play_sound(self.game_over_sound)

    def spawn_obstacle(self):
        """Spawn a random obstacle"""
        # Find an inactive obstacle
        available = [obs for obs in self.obstacles if not obs.performing]
        if available:
            obstacle = random.choice(available)
            obstacle.performing = True
            # Reset position but keep performing as True
            obstacle.x = SCREEN_WIDTH
            obstacle.sprite.center_x = obstacle.x + obstacle.sprite.width / 2
            obstacle.sprite.center_y = obstacle.initial_y + obstacle.sprite.height / 2
            print(f"Spawned obstacle at x={obstacle.x}, y={obstacle.initial_y}, performing={obstacle.performing}")

    def spawn_item(self):
        """Spawn a random item"""
        # Find an inactive item
        available = [item for item in self.items if not item.performing]
        if available:
            item = random.choice(available)
            item.performing = True
            # Reset position but keep performing as True
            item.x = SCREEN_WIDTH
            item.sprite.center_x = item.x + item.sprite.width / 2
            item.sprite.center_y = item.initial_y + item.sprite.height / 2
            print(f"Spawned item at x={item.x}, y={item.initial_y}, performing={item.performing}")

    def check_collisions(self):
        """Check for collisions between player and objects"""
        if not self.player:
            return

        px, py, pw, ph = self.player.get_hitbox()
        player_x_range = range(int(px), int(px + pw))
        player_y_range = range(int(py), int(py + ph))

        # Check obstacle collisions
        for obstacle in self.obstacles:
            if obstacle.performing:
                # Get obstacle position (x is left edge, y is bottom edge)
                ox = obstacle.x
                oy = obstacle.initial_y

                # Check if obstacle x and y are within player's range
                hit_x = ox in player_x_range
                hit_y = oy in player_y_range

                if hit_x and hit_y:
                    # Collision detected
                    obstacle.reset()
                    obstacle.play_sound()
                    self.lives -= 1

                    # Show hit effect
                    self.show_hit = True
                    self.hit_timer = 0
                    if self.hit_sprite:
                        self.hit_sprite.center_x = self.player.x + obstacle.sprite.width
                        self.hit_sprite.center_y = obstacle.sprite.center_y

        # Check item collisions
        for item in self.items:
            if item.performing:
                # Get item position (x is left edge, y is bottom edge)
                ix = item.x
                iy = item.initial_y

                # Check if item x and y are within player's range
                hit_x = ix in player_x_range
                hit_y = iy in player_y_range

                if hit_x and hit_y:
                    # Collision detected
                    item.reset()
                    item.play_sound()
                    self.score += item.points

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Handle mouse clicks"""
        if self.game_state == GameState.START:
            # Check if start button clicked
            if self.start_button and self.start_button.collides_with_point((x, y)):
                if self.button_click_sound:
                    arcade.play_sound(self.button_click_sound)
                self.game_state = GameState.INSTRUCTIONS
            elif not self.start_button:
                # Fallback: click anywhere
                self.game_state = GameState.INSTRUCTIONS

        elif self.game_state == GameState.INSTRUCTIONS:
            # Click anywhere to start
            if self.button_click_sound:
                arcade.play_sound(self.button_click_sound)
            self.setup_game()
            self.game_state = GameState.PLAYING

        elif self.game_state == GameState.GAME_OVER:
            # Click to restart
            if self.button_click_sound:
                arcade.play_sound(self.button_click_sound)
            self.setup_game()
            self.game_state = GameState.PLAYING

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """Handle mouse motion"""
        if self.game_state == GameState.PLAYING and self.player:
            if y > 400:
                self.player.jump()
            elif y > 120 and y <= 300:
                self.player.stand_up()
            elif y <= 120:
                self.player.sit()

    def on_key_press(self, key: int, modifiers: int):
        """Handle key presses"""
        if self.game_state == GameState.PLAYING and self.player:
            if key == arcade.key.W or key == arcade.key.UP:
                self.player.jump()
            elif key == arcade.key.S or key == arcade.key.DOWN:
                self.player.sit()

    def on_key_release(self, key: int, modifiers: int):
        """Handle key releases"""
        if self.game_state == GameState.PLAYING and self.player:
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.player.stand_up()


def main():
    """Main function to run the game"""
    game = PinoySkaterGame()
    arcade.run()


if __name__ == "__main__":
    main()
