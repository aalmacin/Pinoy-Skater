import cocos
from scenes import *

# Start the game
def main():
  # Initialize the director
  cocos.director.director.init(width=1200, height=700)

  # Create the main Scene
  main_scene = StartScene()

  # Run the scene
  cocos.director.director.run(main_scene)

if __name__ == "__main__": main()
