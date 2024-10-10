import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const SNAKE_SIZE = 20;
const WIDTH = 600;
const HEIGHT = 400;
const GRID_SIZE = 20;
const DIRECTIONS = {
  37: { x: -SNAKE_SIZE, y: 0 },
  38: { x: 0, y: -SNAKE_SIZE },
  39: { x: SNAKE_SIZE, y: 0 },
  40: { x: 0, y: SNAKE_SIZE }
};

function App() {
  const videoRef = useRef(null);
  const getRandomFoodPosition = () => {
    const x = Math.floor(Math.random() * (WIDTH / GRID_SIZE)) * GRID_SIZE;
    const y = Math.floor(Math.random() * (HEIGHT / GRID_SIZE)) * GRID_SIZE;
    return { x, y };
  };
  const [snake, setSnake] = useState([{ x: WIDTH / 2, y: HEIGHT / 2 }]);
  const [direction, setDirection] = useState(DIRECTIONS[39]);
  const [food, setFood] = useState(getRandomFoodPosition());
  const [speed, setSpeed] = useState(200);
  const [isGameOver, setIsGameOver] = useState(false);
  const [score, setScore] = useState(0);
  const [isGameStarted, setIsGameStarted] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (DIRECTIONS[e.keyCode] && !isPaused) {
        setDirection(DIRECTIONS[e.keyCode]);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isPaused]);
  useEffect(() => {
    if (isGameOver || isPaused) return;
    const interval = setInterval(() => {
      moveSnake();
    }, speed);
    return () => clearInterval(interval);
  }, [snake, direction, isGameOver, isPaused, speed]);
  const moveSnake = () => {
    const newSnake = [...snake];
    const head = {
      x: newSnake[0].x + direction.x,
      y: newSnake[0].y + direction.y
    };
    if (
      head.x >= WIDTH || head.x < 0 || 
      head.y >= HEIGHT || head.y < 0 || 
      isCollision(newSnake, head)
    ) {
      setIsGameOver(true);
      return;
    }
    newSnake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      setFood(getRandomFoodPosition());
      setSpeed(speed => Math.max(200, speed + 10));
      setScore(score + 10);
    } else {
      newSnake.pop();
    }
    setSnake(newSnake);
  };
  const isCollision = (snake, head) => {
    for (let i = 1; i < snake.length; i++) {
      if (snake[i].x === head.x && snake[i].y === head.y) {
        return true;
      }
    }
    return false;
  };
  const resetGame = () => {
    setSnake([{ x: WIDTH / 2, y: HEIGHT / 2 }]);
    setDirection(DIRECTIONS[39]);
    setFood(getRandomFoodPosition());
    setSpeed(300);
    setIsGameOver(false);
    setScore(0);
  };
  const handleStartGame = () => {
    setIsGameStarted(true);
  };
  const handlePause = () => {
    setIsPaused(!isPaused);
  };

  return (
    <div className="app-container">
      {isGameStarted ? (
        <>
          <div className="title-score-container">
            <h1 className="title">Snake with CV</h1>
            <div className="score-container">
              <div className="score">Score: {score}</div>
              <button className="pause-button" onClick={handlePause}>
                {isPaused ? 'Resume' : 'Pause'}
              </button>
            </div>
          </div>
          <div className="container">
            <div className="game-container">
              <div className="game-area">
                {snake.map((segment, index) => (
                  <div
                    key={index}
                    className="snake-segment"
                    style={{ top: segment.y, left: segment.x }}
                  ></div>
                ))}
                <div
                  className="food"
                  style={{ top: food.y, left: food.x }}
                ></div>
                {isGameOver && (
                  <div className="game-over">
                    <h2>Game Over</h2>
                    <button onClick={resetGame}>Play Again</button>
                  </div>
                )}
              </div>
            </div>
            <div className="video-container">
              <h1>Live Video Feed</h1>
              <img
                ref={videoRef}
                src="http://localhost:5000/video_feed"
                alt="Live Processed Video"
                width="600"
                height="400"
              />
            </div>
          </div>
        </>
      ) : (
        <div className="frontpage">
          <h1 className="typewriter">Snake Game</h1>
          <button onClick={handleStartGame}>Start Game</button>
        </div>
      )}
    </div>
  );
}

export default App;