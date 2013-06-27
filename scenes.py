import cocos
from cocos.actions.interval_actions import *
from cocos.sprite import *
from cocos.scene import Scene
from cocos.layer.base_layers import Layer

class GameScene(Scene):
  WIDTH = 1200
  def __init__(self):
    super(GameScene, self).__init__()

    moving_bg = MovingBackground()
    self.add(moving_bg)

class MovingBackground(Layer):
  BG_IMGS = [
              "images/NonMovingBG.png",
              "images/Ulap.png",
              "images/Mountains.png",
              "images/FastMovingBG.png"
            ]
  def __init__(self):
    super(MovingBackground, self).__init__()
    self.non_moving_bg = Sprite("images/NonMovingBG.png", anchor=(0,0))
    self.clouds = Sprite("images/Ulap.png", anchor=(0,0))

    self.mountains = [
        Sprite("images/Mountains_01.png", anchor=(0,0)),
        Sprite("images/Mountains_02.png", anchor=(0,0))
    ]

    self.positions = [0, GameScene.WIDTH]
    self.fast_moving_bg = Sprite("images/FastMovingBG.png", anchor=(0,0))

    self.add(self.non_moving_bg)
    self.add(self.clouds)

    for i in range(0, len(self.mountains)):
      mountain = self.mountains[i]
      mountain.x = self.positions[i]
      self.add(mountain)


    self.add(self.fast_moving_bg)

    self.interval = 0.1

    self.schedule_interval(self.move, self.interval)

  def move(self, *args, **kwargs):
    #self.clouds.x -= 5

    for mountain in self.mountains:
      mountain.x -= 10
      if mountain.x == -GameScene.WIDTH:
        mountain.x = GameScene.WIDTH
    #self.fast_moving_bg.x -= 15
