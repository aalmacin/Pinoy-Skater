import cocos
from cocos.actions.interval_actions import *
from cocos.actions.instant_actions import *
from cocos.sprite import *
from cocos.cocosnode import CocosNode
from cocos.menu import *
from cocos.scene import Scene
from cocos.layer.base_layers import *
from pyglet.window import key as keyboard_key
from random import choice
from cocos.text import *
import cocos.audio.pygame.music as game_music
import cocos.audio.pygame.mixer as game_mixer

#Initialize the pygame mixer
cocos.audio.pygame.mixer.init()

#Make the click button sound available globally
clicked_button = game_mixer.Sound("sounds/clicked_button.ogg")

"""
  Class: All Scenes
  Description: Holds all the scenes to be used by the game. Start, Instructions, Game, and Game Over scene.
"""
class AllScenes():
  def __init__(self):
    # Initialize the director
    cocos.director.director.init(width=1200, height=700)
    cocos.director.director.window.set_caption("Pinoy Skater")

    # Create all the scenes
    self.start_scene = StartScene(self)
    self.instructions_scene = InstructionsScene(self)
    self.game_scene = GameScene(self)
    self.game_over_scene = GameOverScene(self)

    # Play the game's soundtract
    game_music.load("sounds/bg.mp3")
    game_music.play(-1)

    # Run the start scene
    cocos.director.director.run(self.start_scene)

"""
  Class: Game Scene
  Description: Contains the moving background and game action. This is the main game content.
"""
class GameScene(Scene):
  WIDTH = 1200
  def __init__(self, controller):
    super(GameScene, self).__init__()

    # Create the moving parallax bg and the game layer
    self.moving_bg = MovingBackground()
    self.game_action_layer = GameAction()

    # Add the bg and game layer with the bg at the back
    self.add(self.moving_bg, z=0)
    self.add(self.game_action_layer, z=1)

    # Have a scheduled method check if the game is over
    self.schedule(self.check_if_game_over)
    self.controller = controller

    # Initialize sounds
    self.game_over_snd = game_mixer.Sound("sounds/gameover.ogg")

  """
    Method: Check if game over
    Description: A scheduled method that checks if the game is over (The player run out of life).
  """
  def check_if_game_over(self, *args, **kwargs):
    # If game over
    if self.game_action_layer.game_over == True:
      # Replace the scene to the game over scene
      cocos.director.director.replace(self.controller.game_over_scene)
      # Set the final score in the game over scene to the current score in the scorer.
      self.controller.game_over_scene.final_score = self.game_action_layer.scorer.score
      # Update the text (Holds the score) in the game over scene.
      self.controller.game_over_scene.update_text()
      # Reset the game scene to make sure that it become reusable
      self.reset()
      # Reset game over.
      self.game_action_layer.game_over = False
      # Play the game over sound
      self.game_over_snd.play()

  """
    Method: Reset
    Description: Reset the moving background and the game action layer
  """
  def reset(self):
    self.moving_bg.reset()
    self.game_action_layer.reset()

"""
  Class: Moving Background
  Description: The parallax background at the back of the main game action layer.
"""
class MovingBackground(Layer):
  def __init__(self):
    super(MovingBackground, self).__init__()
    #Set all the sprites in the moving bg
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

    # Set the parallax backgrounds (bgs that move).
    self.parallax_bgs = [self.clouds, self.mountains, self.road]
    # Set the speed of movement of the clouds, mountains, and road
    self.parallax_speed = [1, 5, 100]

    # Set the x positions of the backgrounds to make sure that two bg are connected.
    self.positions = [0, GameScene.WIDTH]

    # Add the non moving background
    self.add(self.non_moving_bg)

    # Add each background to the screen and position them with the positions var.
    for bg in self.parallax_bgs:
      for i in range(0, len(bg)):
        bg_img = bg[i]
        bg_img.x = self.positions[i]
        self.add(bg_img)

    # Move the images every .1 second
    self.schedule_interval(self.move, 0.1)

  """
    Method: Move
    Description: Moves and adjusts the backgrounds.
  """
  def move(self, *args, **kwargs):
    # Moves the backgrounds base on the speed of each bg
    # and reset the background when reached the end of the image.
    for i in range(0, len(self.parallax_speed)):
      for obj in self.parallax_bgs[i]:
        obj.x -= self.parallax_speed[i]
        if obj.x == -GameScene.WIDTH:
          obj.x = GameScene.WIDTH

  """
    Method: Reset
    Description: Reset the parallax bgs to their initial state.
  """
  def reset(self):
    for bg in self.parallax_bgs:
      for i in range(0, len(bg)):
        bg_img = bg[i]
        bg_img.x = self.positions[i]

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
    self.main_char.x = 100
    self.game_over = False

    self.score_given = 100
    self.life_holder = LifeHolder()
    self.add(self.life_holder)

    self.add(self.main_char)
    self.obstacles = []
    self.setup_obstacles()

    self.items = []
    self.setup_items()

    self.schedule_interval(self.count_time_played, 1)
    self.schedule_interval(self.throw_objects, 1)
    self.schedule(self.check_collisions)

    self.scorer = Scorer()
    self.add(self.scorer)

    self.hit_graphic = Sprite("images/Hit.png", anchor=(0,0))
    self.add(self.hit_graphic, z=10)
    self.hit_graphic.visible = False

  def throw_objects(self, *args, **kwargs):
    if self.seconds_played % self.obstacles_interval == 0:
      obj_selected = False
      while not obj_selected:
        obj = choice(self.obstacles)
        if obj.performing == False:
          obj.performing = True
          obj.speed = self.objects_speed + (self.half_minute_count * 5)
          obj_selected = True
    elif self.seconds_played % self.items_interval == 0:
      item_selected = False
      while not item_selected:
        item = choice(self.items)
        if item.performing == False:
          item.performing = True
          item.speed = self.objects_speed + (self.half_minute_count * 5)
          item_selected = True

  def count_time_played(self, *args, **kwargs):
    self.seconds_played += 1
    # Increase speed every 30 seconds
    if self.seconds_played % 30 == 0:
      self.half_minute_count += 1

  def setup_obstacles(self):
    rock_count = 5
    bird_count = 5

    for i in range(0, rock_count):
      self.obstacles.append(HittableObj("images/Rock.png", HittableObj.BOTTOM, game_mixer.Sound("sounds/ouch.ogg")))

    for i in range(0, bird_count):
      self.obstacles.append(HittableObj("images/Bird.png", HittableObj.TOP, game_mixer.Sound("sounds/ouch.ogg")))

    for obs in self.obstacles:
      self.add(obs)

  def setup_items(self):
    coin_count_top = 5
    coin_count_bottom = 10

    for i in range(0, coin_count_top):
      self.items.append(Item("images/Candy.png", HittableObj.CANDY_TOP, 200, game_mixer.Sound("sounds/candy.ogg")))

    for i in range(0, coin_count_bottom):
      self.items.append(Item("images/Coin.png", HittableObj.BOTTOM, 100, game_mixer.Sound("sounds/coin_pickup.ogg")))

    for item in self.items:
      self.add(item)

  # Mouse or keyboard for controls
  def on_mouse_motion(self, x, y, dx, dy):
    if y > 400:
      self.main_char.jump()
    elif y > 120 and y <= 300:
      self.main_char.performing = False
    elif y <= 120:
      self.main_char.sit()

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
      hit_x = obstacle.sprite.x in range(int(self.main_char.x), int(self.main_char.x) + main_obj.width - 50)
      hit_y = obstacle.sprite.y in range(int(self.main_char.y), int(self.main_char.y) + main_obj.height)
      if hit_x and hit_y:
        self.hit_graphic.position = (self.main_char.x + obstacle.sprite.width, obstacle.sprite.y)
        self.hit_graphic.do(Lerp("visible", True, False, 0.5))
        obstacle.reset()
        obstacle.play_sound()
        self.life_holder.lives -= 1
        self.life_holder.update_image()
        if self.life_holder.lives == 0:
          self.game_over = True

    for item in self.items:
      main_obj = self.main_char.get_children()[0].get_children()[0]
      hit_x = item.sprite.x in range(int(self.main_char.x), int(self.main_char.x) + main_obj.width - 50)
      hit_y = item.sprite.y in range(int(self.main_char.y), int(self.main_char.y) + main_obj.height)
      if hit_x and hit_y:
        item.reset()
        item.play_sound()
        self.scorer.score += item.points
        self.scorer.update_text()

  def reset(self):
    self.life_holder.reset()
    self.game_over = False
    self.objects_speed = 10
    self.obstacles_interval = 3
    self.items_interval = 1
    self.half_minute_count = 1
    self.seconds_played = 1
    self.score = 0
    self.scorer.score = 0
    self.scorer.update_text()
    self.hit_graphic.visible = False
    for obs in self.obstacles:
      obs.reset()

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
      jump_height = Skater.Y + 30
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
  CANDY_TOP = (1200, 400)
  def __init__(self, image_name, pos, sound):
    super(HittableObj, self).__init__()
    self.sprite = Sprite(image_name, anchor=(0,0))
    self.sprite.position = pos
    self.add(self.sprite)
    self.performing = False
    self.speed = 0
    self.schedule(self.move)
    self.sound = sound

  def move(self, *args, **kwargs):
    if self.performing:
      self.sprite.x -= self.speed

    if self.sprite.x <= -self.sprite.width:
      self.reset()

  def reset(self):
    self.sprite.x = 1200
    self.performing = False

  def play_sound(self):
    self.sound.play()

class Item(HittableObj):
  def __init__(self, image_name, pos, points, sound):
    super(Item, self).__init__(image_name, pos, sound)
    self.points = points

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
      self.get(str(self.lives)).visible = False

  def reset(self):
    self.lives = 3
    for i in range(0, 3):
      self.get(str(i)).visible = True

class StartScene(Scene):
  def __init__(self, controller):
    super(StartScene, self).__init__()

    self.menu = Menu()
    start_button = ImageMenuItem("images/StartButton.png", self.switch_to_instructions_screen)
    start_button.scale = 2
    start_button.y = -200
    menu_items = [start_button]

    self.menu.create_menu(menu_items)
    self.add(Sprite("images/StartScreenImage.png", anchor=(0,0)), z=0)
    self.add(self.menu, z=1)
    self.controller = controller

  def switch_to_instructions_screen(self):
    cocos.director.director.replace(self.controller.instructions_scene)
    clicked_button.play()

class InstructionsScene(Scene):
  def __init__(self, controller):
    super(InstructionsScene, self).__init__()

    self.instructions_image = Sprite("images/InstructionsImage.png", anchor=(0,0))
    self.instructions_content_image = Sprite("images/Instructions.png", anchor=(0,1800))
    self.instructions_image_mask_top = Sprite("images/InstructionsMaskTop.png", anchor=(0,0))
    self.instructions_image_mask = Sprite("images/InstructionsMask.png", anchor=(0,0))
    self.instructions_content = MoveByMouseLayer(self.instructions_content_image)

    self.instructions_content.x = 73
    self.instructions_content.y = 50

    self.instructions_image_mask_top.y = 650

    self.menu = Menu()
    play_button = ImageMenuItem("images/InstructionsButton.png", self.switch_to_game_screen)
    play_button.y = -300
    play_button.scale = 1.5

    menu_items = [play_button]
    self.menu.create_menu(menu_items)

    self.add(self.instructions_image, z=0)
    self.add(self.instructions_content, z=1)
    self.add(self.instructions_image_mask_top, z=2)
    self.add(self.instructions_image_mask, z=3)
    self.add(self.menu, z=4)
    self.controller = controller

  def switch_to_game_screen(self):
    cocos.director.director.replace(self.controller.game_scene)
    clicked_button.play()

class MoveByMouseLayer(Layer):
  is_event_handler = True
  def __init__(self, content_image):
    super(MoveByMouseLayer, self).__init__()
    self.content_image = content_image
    self.add(self.content_image)

  def on_mouse_motion(self, x, y, dx, dy):
    if y >= cocos.director.director.window.height/2 and self.content_image.y >= 0:
      self.content_image.y -= 10
    elif y < cocos.director.director.window.height/2 and self.content_image.y < 1900:
      self.content_image.y += 10

class GameOverScene(Scene):
  def __init__(self, controller):
    super(GameOverScene, self).__init__()
    self.text_pos = (cocos.director.director.window.width/2,cocos.director.director.window.height/2)

    self.menu = Menu()
    restart_button = ImageMenuItem("images/RestartButton.png", self.switch_to_game_screen)
    menu_items = [restart_button]
    restart_button.scale = 2
    restart_button.y = -200

    self.menu.create_menu(menu_items)
    self.add(Sprite("images/GameOverScreenImage.png", anchor=(0,0)), z=0)
    self.add(self.menu, z=1)
    self.controller = controller

    self.score_layer = Layer()
    self.final_score = 0
    self.final_score_label = Label(text="Final Score: 0", font_size=32, position=self.text_pos, anchor_x="center", anchor_y="center", color=(255, 30, 30, 200))
    self.score_layer.add(self.final_score_label)
    self.add(self.score_layer, z=2)

  def switch_to_game_screen(self):
    cocos.director.director.replace(self.controller.game_scene)
    clicked_button.play()

  def update_text(self):
    self.final_score_label.element.text = "Final Score: " + str(self.final_score)

class Scorer(CocosNode):
  TEXT_POS = (10, 650)
  def __init__(self):
    super(Scorer, self).__init__()
    self.score = 0
    self.scorer = Label(text="Score: 0", font_size=32, position=Scorer.TEXT_POS)
    self.add(self.scorer)

  def update_text(self):
    self.scorer.element.text = "Score: " + str(self.score)
