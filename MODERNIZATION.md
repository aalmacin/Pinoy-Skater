# Pinoy Skater - Modern Version Guide

## Overview

This project now includes **two versions** of the Pinoy Skater game:

1. **Original Version** (`pinoy-skater_3.py`) - Uses legacy Cocos2d library (Python 3.10 or older)
2. **Modern Version** (`pinoy-skater_4.py`) - Uses Python Arcade library (Python 3.13.5+)

## Why a Modern Version?

The original version uses `cocos2d==0.6.9`, which is incompatible with Python 3.11+ due to deprecated features (specifically the `'rU'` file mode). The modern version has been completely rewritten using the **Arcade** library, a modern, actively maintained Python game framework.

## What Changed?

### Technical Improvements

- **Modern Library**: Migrated from Cocos2d to Arcade 3.3+
- **Python 3.13.5 Compatible**: Works with the latest Python versions
- **Better Performance**: Arcade is built on OpenGL for better rendering
- **Cleaner Code**: Modernized with type hints and better structure
- **Active Maintenance**: Arcade is actively developed and supported

### Game Features (Preserved)

All original gameplay features are maintained:
- ✅ Side-scrolling parallax backgrounds
- ✅ Player character with jump/duck mechanics
- ✅ Mouse and keyboard controls
- ✅ Obstacles (rocks and birds)
- ✅ Collectible items (coins and candy)
- ✅ Lives system (3 hearts)
- ✅ Score tracking
- ✅ Multiple game states (Start, Instructions, Playing, Game Over)
- ✅ Sound effects and background music support
- ✅ Progressive difficulty (speeds up over time)

## Installation & Setup

### For Modern Version (Python 3.13.5+)

```bash
# Install dependencies
pip install -r requirements-modern.txt

# Run the game
python pinoy-skater_4.py
```

### For Original Version (Python 3.10 or older)

If you need to run the original version, you'll need to downgrade Python:

```bash
# Using asdf (recommended)
asdf install python 3.10.14
asdf local python 3.10.14

# Install dependencies
pip install -r requirements.txt

# Run the original game
python pinoy-skater_3.py
```

## How to Play

### Controls

**Mouse Control:**
- Move mouse to **top of screen** → Jump
- Move mouse to **middle of screen** → Normal
- Move mouse to **bottom of screen** → Duck

**Keyboard Control:**
- Press **W** or **↑** → Jump
- Press **S** or **↓** → Duck
- Release **S** or **↓** → Stand up

### Objective

- **Avoid obstacles** (rocks on the ground, birds in the air)
- **Collect items** for points:
  - Coins (bottom) = 100 points
  - Candy (top) = 200 points
- Survive as long as possible
- Game gets progressively faster every 30 seconds

### Lives

- You start with 3 lives (hearts)
- Hitting an obstacle costs 1 life
- Game ends when all lives are lost

## Key Code Improvements

### Architecture

The modern version uses a cleaner, more maintainable architecture:

```python
# Original (Cocos2d)
class GameScene(Scene):
    def __init__(self):
        super(GameScene, self).__init__()
        self.moving_bg = MovingBackground()
        # ...

# Modern (Arcade)
class PinoySkaterGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        # Cleaner window management
```

### Type Hints

Modern version includes proper type annotations:

```python
def update(self, delta_time: float):
    """Update game logic"""
    # ...

def check_collisions(self) -> None:
    """Check for collisions between player and objects"""
    # ...
```

### Enums for State Management

```python
class GameState(Enum):
    START = 1
    INSTRUCTIONS = 2
    PLAYING = 3
    GAME_OVER = 4

class PlayerState(Enum):
    NORMAL = 0
    JUMPING = 1
    SITTING = 2
```

### Important API Differences

**Sprite Drawing in Arcade 3.x:**

In Arcade 3.x, individual sprites don't have a `.draw()` method. Instead, use the `arcade.draw_sprite()` function:

```python
# OLD (Arcade 2.x / Cocos2d)
sprite.draw()

# NEW (Arcade 3.x)
arcade.draw_sprite(sprite)

# OR use SpriteList (recommended for performance)
sprite_list = arcade.SpriteList()
sprite_list.append(sprite)
sprite_list.draw()
```

This is a **breaking change** from Arcade 2.x and is important to know if you're updating existing Arcade code.

## Dependencies Comparison

### Original Version
```
cocos2d==0.6.9      # Unmaintained, Python ≤3.10 only
pygame==2.1.0        # Used by cocos2d for audio
pyglet==1.5.27       # Used by cocos2d for graphics
```

### Modern Version
```
arcade>=3.0.0        # Modern, actively maintained
├── pyglet~=2.1.11   # Latest version (auto-installed)
├── pillow~=11.3.0   # Image processing (auto-installed)
└── pymunk~=6.9.0    # Physics engine (auto-installed)
```

## Troubleshooting

### "Module not found: arcade"
```bash
pip install arcade
```

### "FileNotFoundError: images/..."
Make sure all game assets (images and sounds) are in the correct directories:
- `images/` - All sprite images
- `sounds/` - All sound effects and music

The modern version includes fallbacks if assets are missing, but the game will look/sound better with proper assets.

### Performance Issues
The modern version uses hardware acceleration via OpenGL. If you experience issues:
1. Update your graphics drivers
2. Try running on a different machine
3. Check that your system supports OpenGL 3.3+

## Building Executables

### Modern Version
```bash
pip install pyinstaller
pyinstaller --name="PinoySkater" --windowed --onefile pinoy-skater_4.py
```

### Original Version
Use the existing `build.sh` script (requires Python 3.10).

## Future Enhancements

The modern architecture makes it easier to add:
- 🎮 Gamepad support
- 🌐 Online leaderboards
- 🎨 New themes and skins
- 📱 Mobile support (via Kivy)
- 🔊 Better audio management
- ⚡ Particle effects
- 🏆 Achievement system

## Contributing

When contributing, please target the modern version (`pinoy-skater_4.py`) as the original version is maintained for legacy compatibility only.

## License

Same as original Pinoy Skater project.

---

**Recommendation:** Use the modern version (`pinoy-skater_4.py`) for all new development and gameplay. The original version is kept for historical purposes and compatibility with existing builds.
