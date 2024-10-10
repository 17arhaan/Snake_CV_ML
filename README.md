# Snake Game with Gesture Control

## Overview
This project is a modern take on the classic Snake game, developed in Python using `pygame` and integrated with `OpenCV` for gesture control. It allows players to choose between manual, AI, and gesture-controlled gameplay modes. The game features an interactive menu, live webcam feed for gesture recognition, a countdown before starting, a replay feature, and a leaderboard to keep track of high scores.

## Features
- **Manual Mode**: Control the snake using keyboard arrow keys.
- **AI Mode**: Watch an AI agent play the game using pre-trained Q-learning data.
- **Gesture Control Mode**: Use hand gestures via a webcam to control the snake.
- **Interactive Menu**: Select between different game modes, view the leaderboard, or quit the game.
- **Live Webcam Feed**: Visualize gestures and see which direction is detected.
- **Leaderboard**: Keeps track of top scores for different players.
- **Replay Feature**: Watch a replay of your game after it ends.

## Game Controls
- **Manual Mode**: Use the following keys:
  - Arrow keys to move (`UP`, `DOWN`, `LEFT`, `RIGHT`)
- **Gesture Control**:
  - Move your hand to the left, right, up, or down to control the snake.
  - The webcam feed shows the detected gesture.
  - Press `q` to quit gesture mode.

## Installation
### Prerequisites
- Python 3.6+
- Install the required Python packages:
  ```sh
  pip install pygame opencv-python numpy
  ```

### Running the Game
1. Clone this repository or download the game script.
   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Run the Python script:
   ```sh
   python snake_game.py
   ```

### Optional Bash Commands
- Create a virtual environment to manage dependencies:
  ```sh
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
- Install the dependencies inside the virtual environment:
  ```sh
  pip install -r requirements.txt
  ```
- Deactivate the virtual environment after use:
  ```sh
  deactivate
  ```

## How to Play
1. **Launch the Game**: Start the game by running the script.
2. **Menu Options**: Choose from the following:
   - **Manual Mode**: Play the game using your keyboard.
   - **AI Mode**: Watch the AI play the game autonomously.
   - **Gesture Mode**: Play the game using hand gestures via a webcam.
   - **Leaderboard**: View the top scores.
   - **Quit**: Exit the game.
3. **Countdown**: After selecting a game mode, a 10-second countdown will begin before the game starts.
4. **Collect Food**: Direct the snake to collect red blocks (food) and grow longer while avoiding collisions with itself and the game boundaries.

## Gesture Control
In gesture mode, the game uses the computer's webcam to track hand movements:
- The webcam feed is displayed in a smaller window for better visibility.
- The following gestures are used for controlling the snake:
  - **Move Left**: Move your hand to the left of the screen.
  - **Move Right**: Move your hand to the right of the screen.
  - **Move Up**: Move your hand to the top of the screen.
  - **Move Down**: Move your hand to the bottom of the screen.

## Leaderboard
- After each game, your score is recorded on the leaderboard.
- The leaderboard keeps track of the top 10 scores.

## Replay Feature
- After the game ends, you will have the option to watch a replay of your game.
- The replay allows you to review your moves and see where you went wrong.

## Code Structure
- **SnakeGame Class**: The main class that handles all game logic, graphics, and player input.
- **Gesture Control**: The game uses `OpenCV` to capture and recognize gestures.
- **AI Mode**: Uses Q-learning to control the snake based on pre-trained data.

## Customization
You can modify the game's behavior by changing certain parameters in the code:
- **Game Speed**: Adjust the `self.spd` value to make the game faster or slower.
- **Grid Size**: Modify `self.sn_size` to change the size of each snake segment.
- **AI Training**: Replace the Q-table with your own training data to improve the AI's performance.

## Known Issues
- The gesture detection may vary depending on lighting conditions and the quality of the webcam.
- Pressing `q` while in gesture mode will quit the game.

## License
This project is open-source and available under the MIT License.

## Contributions
Feel free to submit issues, fork the repository, and send pull requests to contribute to the project.

## Credits
- Developed by **Arhaan** using **Python**, **pygame**, and **OpenCV**.
- Inspired by the classic Snake game.
