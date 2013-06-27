import cocos
from cocos.actions.interval_actions import *
from cocos.sprite import *
from cocos.cocosnode import CocosNode
from cocos.scene import Scene
from cocos.layer.base_layers import Layer

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
  def __init__(self):
    super(GameAction, self).__init__()

    self.main_char = Skater()

    self.add(self.main_char)

class Skater(CocosNode):
  IMG_FILENAME = "images/Skater.png"
  X = 100
  Y = 250
  def __init__(self):
    super(Skater, self).__init__()

    self.skater_main = Sprite(Skater.IMG_FILENAME)

    self.add(self.skater_main)
    self.skater_main.position = (Skater.X, Skater.Y)

