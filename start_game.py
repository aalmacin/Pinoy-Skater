import cocos
from scenes import MainScene

# Start the game
def main():
  # Initialize the director
  cocos.director.director.init(width=600, height=500)

  # Create the main Scene
  main_scene = MainScene(cocos.director.director.window)

  # Run the scene
  cocos.director.director.run(main_scene)

if __name__ == "__main__": main()
