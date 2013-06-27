import cocos
from cocos.actions.interval_actions import *
from cocos.sprite import *
import time

"""
  name: GameScene
  desc: The main screen to be shown when the game is loaded.
"""
class GameScene(cocos.scene.Scene):
  BG_IMGS = [
              "images/NonMovingBG.png",
              "images/Ulap.png",
              "images/Mountains.png",
              "images/FastMovingBG.png"
            ]
  WIDTH = 2400
  HEIGHT = 700
  def __init__(self, director_window):
    super(GameScene, self).__init__()

    # Create an instance of the scroller
    self.background_scroller = ParallaxScroller(director_window)

    # Call the method to set the background of the scene
    self.set_parallax_background()

    self.game_layer = GameLayer()

    self.add(self.background_scroller, z=1)
    self.add(self.game_layer, z=2)

  """
    name: set background
    desc: Sets the background image to the background layer of the scene
  """
  def set_parallax_background(self):
    # Create the background image
    scrollable_layers = []
    for i in range(0, len(GameScene.BG_IMGS)):
      scrollable_sprite = Sprite(GameScene.BG_IMGS[i], anchor=(0,0))
      scrollable_layer = cocos.layer.scrolling.ScrollableLayer(parallax=i)
      scrollable_layer.px_width = GameScene.WIDTH
      scrollable_layer.px_height = GameScene.HEIGHT
      scrollable_layer.add(scrollable_sprite)
      scrollable_layers.append(scrollable_layer)

    self.background_scroller.add_children(scrollable_layers)

class ParallaxScroller(cocos.layer.scrolling.ScrollingManager):
  PARALLAX_SPEED = 10
  PARALLAX_INTERVAL = 0.1
  def __init__(self, viewport=None):
    super(ParallaxScroller, self).__init__(viewport)
    self.schedule_interval(self.start_moving, ParallaxScroller.PARALLAX_INTERVAL)
    self.current_x = self.viewport.width / 2

  def start_moving(self, *args, **kwargs):
    for layer in self.get_children():
      if layer.x <= -GameScene.WIDTH:
        layer.set_view(0, layer.y, GameScene.WIDTH / 2, GameScene.HEIGHT)

    if self.current_x + ParallaxScroller.PARALLAX_SPEED <= GameScene.WIDTH - (self.viewport.width / 2):
      self.current_x += ParallaxScroller.PARALLAX_SPEED
    else:
      self.current_x = self.viewport.width / 2
    self.set_focus(self.current_x, 0)

  def add_children(self, layers):
    for layer in layers:
      self.add(layer)

class GameLayer(cocos.layer.base_layers.Layer):
  UP = 119
  DOWN = 115
  is_event_handler = True
  HEIGHT = 200
  def __init__(self):
    super(GameLayer, self).__init__()
    self.size = (GameScene.WIDTH / 2, GameLayer.HEIGHT)
    self.hero = Hero()
    self.add(self.hero)

  def on_key_press(self, key, modifiers):
    if GameLayer.UP == key:
      self.hero.hero_action(Hero.JUMPING)
    elif GameLayer.DOWN == key:
      self.hero.hero_action(Hero.SLIDING)

class Hero(cocos.cocosnode.CocosNode):
  IMAGE_RUN = "images/Skater.png"
  SLIDE_NAME = "images/katipunero_slide.png"
  JUMP_NAME = "images/katipunero_jump.png"
  JUMPING = "Jumping"
  SLIDING = "Sliding"
  X = 100
  Y = 250
  RUNNING_CHANGE = 0.4
  ACTION_DURATION = 0.4

  def __init__(self):
    super(Hero, self).__init__()
    self.hero_running = Sprite(Hero.IMAGE_RUN)
    self.hero_slide = Sprite(Hero.SLIDE_NAME)
    self.hero_jump = Sprite(Hero.JUMP_NAME)

    self.add(self.hero_slide)
    self.add(self.hero_running)
    self.add(self.hero_jump)

    self.hero_slide.visible = False
    self.hero_jump.visible = False
    self.acting = False
    self.position = (Hero.X, Hero.Y)

  def hero_action(self, action_type):
    if not self.acting:
      self.hero_running.visible = False

      delay = Delay(Hero.ACTION_DURATION)

      hide_and_show = Lerp("visible", False, True, Hero.ACTION_DURATION)
      show_and_hide = Lerp("visible", True, False, Hero.ACTION_DURATION)

      self.acting = True
      if action_type == Hero.JUMPING:
        jump_height = Hero.Y + 100
        jump = Jump(x=0, y=jump_height, duration=Hero.ACTION_DURATION)
        self.do(jump)
        self.hero_jump.do(show_and_hide)
      elif action_type == Hero.SLIDING:
        self.hero_slide.do(show_and_hide)

      state_change = Lerp("acting", True, False, Hero.ACTION_DURATION)
      self.do(delay + state_change)
      self.hero_running.do(delay + hide_and_show)

