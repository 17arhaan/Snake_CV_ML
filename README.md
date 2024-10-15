Snake Game with Gesture Control (Python + React)
Overview
This project is a modern take on the classic Snake game, developed in Python using pygame and integrated with OpenCV for gesture control. Additionally, it includes a React version for web-based gameplay. Both versions of the game allow players to choose between manual, AI, and gesture-controlled gameplay modes. The Python version offers an interactive menu, live webcam feed for gesture recognition, a countdown before starting, a replay feature, and a leaderboard to keep track of high scores. The React version extends the game to the web with an intuitive user interface.

Features
Manual Mode: Control the snake using keyboard arrow keys.
AI Mode: Watch an AI agent play the game using pre-trained Q-learning data.
Gesture Control Mode: Use hand gestures via a webcam to control the snake (Python version only).
Interactive Menu: Select between different game modes, view the leaderboard, or quit the game (Python).
Live Webcam Feed: Visualize gestures and see which direction is detected (Python version).
React Web Version: A browser-based version of the game with a user-friendly interface.
Leaderboard: Keeps track of top scores for different players.
Replay Feature: Watch a replay of your game after it ends.
Game Controls
Manual Mode:
Arrow keys to move (UP, DOWN, LEFT, RIGHT)
React version uses standard keyboard controls.
Gesture Control (Python version only):
Move your hand to the left, right, up, or down to control the snake.
The webcam feed shows the detected gesture.
Press q to quit gesture mode.
Installation
Python Version
Prerequisites
Python 3.6+
Install the required Python packages:
sh
Copy code
pip install pygame opencv-python numpy
Running the Game
Clone the repository or download the game script:
sh
Copy code
git clone <repository-url>
cd <repository-folder>
Run the Python script:
sh
Copy code
python snake_game.py
Optional Bash Commands
Create a virtual environment to manage dependencies:
sh
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the dependencies inside the virtual environment:
sh
Copy code
pip install -r requirements.txt
Deactivate the virtual environment after use:
sh
Copy code
deactivate
React Version
Prerequisites
Node.js (v14+)
Install the required dependencies:
sh
Copy code
npm install
Running the React Game
Navigate to the React folder of the project:
sh
Copy code
cd react-snake-game
Install dependencies:
sh
Copy code
npm install
Start the development server:
sh
Copy code
npm start
Access the game at http://localhost:3000.
How to Play (Both Versions)
Launch the Game: Start the Python or React version.
Menu Options (Python version): Choose from the following:
Manual Mode: Play the game using your keyboard.
AI Mode: Watch the AI play the game autonomously.
Gesture Mode: Play the game using hand gestures via a webcam.
Leaderboard: View the top scores.
Quit: Exit the game.
Gameplay: Use arrow keys or gestures to control the snake, collect food, and grow longer while avoiding collisions with the snake's body or game boundaries.
Gesture Control (Python version)
In gesture mode, the game uses the computer's webcam to track hand movements:

The webcam feed is displayed in a smaller window for better visibility.
The following gestures are used for controlling the snake:
Move Left: Move your hand to the left of the screen.
Move Right: Move your hand to the right of the screen.
Move Up: Move your hand to the top of the screen.
Move Down: Move your hand to the bottom of the screen.
Leaderboard
After each game, your score is recorded on the leaderboard (Python).
The leaderboard keeps track of the top 10 scores.
Replay Feature (Python version)
After the game ends, you will have the option to watch a replay of your game.
The replay allows you to review your moves and see where you went wrong.
Code Structure
SnakeGame Class (Python): The main class that handles all game logic, graphics, and player input.
Gesture Control (Python): The game uses OpenCV to capture and recognize gestures via webcam.
React Version: The React app contains the web-based game logic and UI.
AI Mode (Python): Uses Q-learning to control the snake based on pre-trained data.
Customization
You can modify the game's behavior by changing certain parameters in the code:

Game Speed: Adjust the self.spd value in Python or React to make the game faster or slower.
Grid Size: Modify self.sn_size to change the size of each snake segment.
AI Training (Python): Replace the Q-table with your own training data to improve the AI's performance.
Known Issues
The gesture detection may vary depending on lighting conditions and the quality of the webcam (Python version).
Pressing q while in gesture mode will quit the game (Python version).
The React version currently does not support gesture control but offers manual gameplay.
License
This project is open-source and available under the MIT License.

Contributions
Feel free to submit issues, fork the repository, and send pull requests to contribute to the project.

Credits
Developed by Arhaan using Python, pygame, OpenCV, and React.
Inspired by the classic Snake game.
