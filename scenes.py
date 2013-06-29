import cocos
from cocos.actions.interval_actions import *
from cocos.actions.instant_actions import *
from cocos.sprite import *
from cocos.cocosnode import CocosNode
from cocos.scene import Scene
from cocos.layer.base_layers import *
from pyglet.window import key as keyboard_key
from random import choice

class GameScene(Scene):
  WIDTH = 1200
  def __init__(self):
    super(GameScene, self).__init__()

    moving_bg = MovingBackground()
    game_action_layer = GameAction()

    self.add(moving_bg, z=0)
    self.add(game_action_layer, z=1)

class MovingBackground(Layer):
  def __init__(self):
    super(MovingBackground, self).__init__()
    self.non_moving_bg = Sprite("images/NonMovingBG.png", anchor=(0,0))

    self.clouds = [
        Sprite("images/clouds_01.png", anchor=(0,0)),
        Sprite("images/clouds_02.png", anchor=(0,0))
    ]

    self.mountains = [
        Sprite("images/Mountains_01.png", anchor=(0,0)),
        Sprite("images/Mountains_02.png", anchor=(0,0))
    ]

    self.road = [
        Sprite("images/Road_01.png", anchor=(0,0)),
        Sprite("images/Road_02.png", anchor=(0,0))
    ]

    self.parallax_bgs = [self.clouds, self.mountains, self.road]
    self.parallax_speed = [1, 5, 100]

    self.positions = [0, GameScene.WIDTH]

    self.add(self.non_moving_bg)

    for bg in self.parallax_bgs:
      for i in range(0, len(bg)):
        bg_img = bg[i]
        bg_img.x = self.positions[i]
        self.add(bg_img)

    self.interval = 0.1

    self.schedule_interval(self.move, self.interval)

  def move(self, *args, **kwargs):
    for i in range(0, len(self.parallax_speed)):
      for obj in self.parallax_bgs[i]:
        obj.x -= self.parallax_speed[i]
        if obj.x == -GameScene.WIDTH:
          obj.x = GameScene.WIDTH


class GameAction(Layer):
  is_event_handler = True
  def __init__(self):
    super(GameAction, self).__init__()

    self.objects_speed = 10
    self.obstacles_interval = 3
    self.items_interval = 1
    self.half_minute_count = 1
    self.seconds_played = 1

    self.main_char = Skater()

    self.score = 0
    self.life = 3

    self.add(self.main_char)
    self.obstacles = []
    self.setup_obstacles()

    self.schedule_interval(self.count_time_played, 1)
    self.schedule_interval(self.throw_objects, 1)
    self.schedule(self.check_collisions)

  def throw_objects(self, *args, **kwargs):
    if self.seconds_played % self.obstacles_interval == 0:
      obj_selected = False
      while not obj_selected:
        obj = choice(self.obstacles)
        if obj.performing == False:
          obj_selected = True
          obj.performing = True
          obj.speed = self.objects_speed

  def count_time_played(self, *args, **kwargs):
    self.seconds_played += 1
    if self.seconds_played % 30 == 0:
      self.half_minute_count += 1

  def setup_obstacles(self):
    rock_count = 3
    bird_count = 3

    for i in range(0, rock_count):
      self.obstacles.append(Obstacle("images/Rock.png", HittableObj.BOTTOM))

    for i in range(0, bird_count):
      self.obstacles.append(Obstacle("images/Bird.png", HittableObj.TOP))

    for obs in self.obstacles:
      self.add(obs)

  def on_key_press(self, key, modifiers):
    if key == keyboard_key.W:
      self.main_char.jump()
    elif key == keyboard_key.S:
      self.main_char.sit()

  def on_key_release(self, key, modifiers):
    if key == keyboard_key.S:
      self.main_char.performing = False

  def check_collisions(self, *args, **kwargs):
    for x in self.main_char.get_children():
      main_obj = x.get_children()[0]

    for obstacle in self.obstacles:
      if obstacle.sprite.x in range(main_obj.x, main_obj.width - 50):
        obstacle.reset()
        self.life -= 1

class Skater(MultiplexLayer):
  IMG_FILENAMES = ["images/Skater.png", "images/SkaterJump.png", "images/SkaterSitting.png"]
  X = 100
  Y = 130
  MAIN = 0
  JUMP = 1
  SIT = 2

  def __init__(self):
    layers = []
    for file_name in Skater.IMG_FILENAMES:
      self.temp_layer = Layer()
      self.temp_layer.add(Sprite(file_name, anchor=(0,0)))
      layers.append(self.temp_layer)

    super(Skater, self).__init__(*layers)

    self.y = Skater.Y
    self.performing = False

    self.schedule(self.show_correct_img)

  def jump(self):
    if not self.performing and self.y == Skater.Y:
      self.switch_to(Skater.JUMP)
      self.performing = True
      jump_height = Skater.Y + 200
      jump_action = Jump(x=0, y=jump_height, duration=1)
      jump_protection = Lerp("performing", True, False, 1)
      self.do(jump_action | jump_protection)

  def sit(self):
    if not self.performing and self.y == Skater.Y:
      self.performing = True
      self.switch_to(Skater.SIT)

  def to_normal(self):
    self.switch_to(Skater.MAIN)

  def show_correct_img(self, *args, **kwargs):
    if not self.performing and self.y == Skater.Y:
      self.to_normal()

class HittableObj(CocosNode):
  BOTTOM = (1200, 100)
  TOP = (1200, 300)
  def __init__(self, image_name, pos):
    super(HittableObj, self).__init__()
    self.sprite = Sprite(image_name, anchor=(0,0))
    self.sprite.position = pos
    self.add(self.sprite)
    self.performing = False
    self.speed = 0
    self.schedule(self.move)

  def move(self, *args, **kwargs):
    if self.performing:
      self.sprite.x -= self.speed
    if self.sprite.x == 0:
      self.reset()

  def reset(self):
    self.sprite.x = 1200
    self.performing = False


class Obstacle(HittableObj):
  def __init__(self, image_name, pos):
    super(Obstacle, self).__init__(image_name, pos)

class Item(HittableObj):
  def __init__(self, image_name):
    super(Item, self).__init__(image_name, pos)
