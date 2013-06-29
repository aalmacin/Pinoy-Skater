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

    self.moving_bg = MovingBackground()
    self.game_action_layer = GameAction()

    self.add(self.moving_bg, z=0)
    self.add(self.game_action_layer, z=1)

    self.schedule(self.check_if_game_over)

  def check_if_game_over(self, *args, **kwargs):
    if self.game_action_layer.game_over == True:
      self.end()

  def on_exit(self):
    cocos.director.director.replace(GameOverScene())

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
    self.game_over = False

    self.score = 0
    self.life_holder = LifeHolder()
    self.add(self.life_holder)

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
          obj.speed = self.objects_speed + (self.half_minute_count * 5)

  def count_time_played(self, *args, **kwargs):
    self.seconds_played += 1
    # Increase speed every 30 seconds
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
    for obstacle in self.obstacles:
      main_obj = self.main_char.get_children()[0].get_children()[0]
      hit_x = obstacle.sprite.x in range(int(self.main_char.x), main_obj.width - 50)
      hit_y = obstacle.sprite.y in range(int(self.main_char.y), int(self.main_char.y) + main_obj.height)
      if hit_x and hit_y:
        obstacle.reset()
        self.life_holder.lives -= 1
        self.life_holder.update_image()
        if self.life_holder.lives == 0:
          self.game_over = True

  def reset(self):
    print "RESET"

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
      temp_layer = Layer()
      temp_layer.add(Sprite(file_name, anchor=(0,0)))
      layers.append(temp_layer)

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
  BOTTOM = (1200, 130)
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
    if self.sprite.x == -self.sprite.width:
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

class LifeHolder(Layer):
  IMAGE_NAME = "images/Heart.png"
  def __init__(self):
    super(Layer, self).__init__()
    self.lives = 3
    self.x_pos = [10, 65, 120]
    for i in range(0, self.lives):
      temp_sprite = Sprite(LifeHolder.IMAGE_NAME, anchor=(0,0))
      temp_sprite.x = self.x_pos[i]
      temp_sprite.y = 20
      self.add(temp_sprite, name=str(i))

  def update_image(self):
    if self.lives < 3:
      self.remove(self.get(str(self.lives)))

class StartScene(Scene):
  def __init__(self):
    super(StartScene, self).__init__()

class GameOverScene(Scene):
  def __init__(self):
    super(GameOverScene, self).__init__()
