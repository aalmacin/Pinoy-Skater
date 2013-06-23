import cocos
from scenes import MainScene

# Start the game
def main():
  # Initialize the director
  cocos.director.director.init(width=1024, height=500)

  # Create the main Scene
  main_scene = MainScene()

  # Run the scene
  cocos.director.director.run(main_scene)

if __name__ == "__main__": main()
