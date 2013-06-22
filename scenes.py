import cocos

"""
  name: MainScene
  desc: The main screen to be shown when the game is loaded.
"""
class MainScene(cocos.scene.Scene):
  BG_IMG_FILENAME = "images/scrollingbg.png"
  def __init__(self):
    super(MainScene, self).__init__()

    # Create an instance of the background layer
    self.background = cocos.layer.Layer()

    # Call the method to set the background of the scene
    self.set_background(MainScene.BG_IMG_FILENAME)

    self.add(self.background)

  """
    name: set background
    desc: Sets the background image to the background layer of the scene
  """
  def set_background(self, image_name):

    # Create the background image
    background_image = cocos.sprite.Sprite(image_name, anchor=(0,0))

    # Add the background image sprite to the layer
    self.background.add(background_image)
