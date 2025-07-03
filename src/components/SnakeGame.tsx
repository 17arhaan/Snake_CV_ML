import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Play, Pause, RotateCcw, Camera, CameraOff, SkipBack, SkipForward } from 'lucide-react';
import { useOpenCVBackend } from '../hooks/useOpenCVBackend';
import OpenCVControls from './OpenCVControls';

interface Position {
  x: number;
  y: number;
}

type Direction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';
type GameState = 'MENU' | 'PLAYING' | 'PAUSED' | 'GAME_OVER' | 'DEATH_ANIMATION' | 'REPLAY';

interface GameFrame {
  snake: Position[];
  food: Position;
  score: number;
  direction: Direction;
  timestamp: number;
}

const GRID_SIZE = 20;
const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 400;
const INITIAL_SNAKE = [{ x: 10, y: 10 }];
const INITIAL_DIRECTION: Direction = 'RIGHT';

const SnakeGame: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const gameLoopRef = useRef<number>();
  const replayLoopRef = useRef<number>();
  const lastDirectionRef = useRef<Direction>(INITIAL_DIRECTION);

  const [gameState, setGameState] = useState<GameState>('MENU');
  const [snake, setSnake] = useState<Position[]>(INITIAL_SNAKE);
  const [direction, setDirection] = useState<Direction>(INITIAL_DIRECTION);
  const [food, setFood] = useState<Position>({ x: 15, y: 15 });
  const [score, setScore] = useState(0);
  const [highScore, setHighScore] = useState(() => {
    return parseInt(localStorage.getItem('snakeHighScore') || '0');
  });
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraStatus, setCameraStatus] = useState<'off' | 'starting' | 'ready' | 'error'>('off');
  
  // Death animation states
  const [deathAnimation, setDeathAnimation] = useState({
    frame: 0,
    maxFrames: 30,
    explosionParticles: [] as Array<{x: number, y: number, vx: number, vy: number, life: number}>
  });

  // Replay system states
  const [gameFrames, setGameFrames] = useState<GameFrame[]>([]);
  const [replayFrame, setReplayFrame] = useState(0);
  const [replaySpeed, setReplaySpeed] = useState(1);
  const [isRecording, setIsRecording] = useState(false);

  // OpenCV Backend Integration
  const {
    isBackendAvailable,
    isConnected,
    config: openCVConfig,
    error: openCVError,
    lastDetection,
    startProcessing,
    stopProcessing,
    setDetectionMode,
    setSensitivity,
    checkBackend
  } = useOpenCVBackend();

  // Generate random food position
  const generateFood = useCallback((snakeBody: Position[]): Position => {
    let newFood: Position;
    do {
      newFood = {
        x: Math.floor(Math.random() * (CANVAS_WIDTH / GRID_SIZE)),
        y: Math.floor(Math.random() * (CANVAS_HEIGHT / GRID_SIZE))
      };
    } while (snakeBody.some(segment => segment.x === newFood.x && segment.y === newFood.y));
    return newFood;
  }, []);

  // Camera setup with better error handling
  const setupCamera = useCallback(async () => {
    console.log('🔄 Setting up camera...');
    console.log('Current state:', { cameraEnabled, cameraStatus, stream: !!stream });
    setCameraStatus('starting');
    
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera not supported in this browser');
      }

      console.log('📡 Requesting camera access...');
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      });
      
      console.log('✅ Camera stream obtained:', mediaStream);
      console.log('Stream details:', {
        active: mediaStream.active,
        tracks: mediaStream.getVideoTracks().length,
        trackStates: mediaStream.getVideoTracks().map(t => t.readyState)
      });
      setStream(mediaStream);
      
      if (videoRef.current) {
        console.log('📹 Setting stream to video element...');
        videoRef.current.srcObject = mediaStream;
        
        const handleVideoReady = () => {
          console.log('✅ Video ready and playing');
          console.log('Video element state:', {
            videoWidth: videoRef.current?.videoWidth,
            videoHeight: videoRef.current?.videoHeight,
            readyState: videoRef.current?.readyState,
            paused: videoRef.current?.paused
          });
          setCameraStatus('ready');
          setCameraEnabled(true);
          
          // Start OpenCV processing if backend is available
          if (isBackendAvailable && videoRef.current) {
            console.log('🎯 Starting OpenCV processing with camera');
            startProcessing(videoRef.current);
          }
        };

        const handleVideoError = (error: any) => {
          console.error('❌ Video error:', error);
          setCameraStatus('error');
        };

        videoRef.current.addEventListener('loadeddata', handleVideoReady);
        videoRef.current.addEventListener('error', handleVideoError);
        videoRef.current.addEventListener('loadedmetadata', () => {
          console.log('📊 Video metadata loaded');
        });
        videoRef.current.addEventListener('canplay', () => {
          console.log('🎬 Video can play');
        });
        
        // Force video to play
        try {
          console.log('▶️ Starting video playback...');
          await videoRef.current.play();
          console.log('✅ Video is playing successfully');
        } catch (playError) {
          console.log('⚠️ Video play error (might be normal):', playError);
          // Sometimes autoplay is blocked, but the video will still work
          handleVideoReady(); // Call manually if autoplay fails
        }
      } else {
        console.error('❌ Video ref is not available');
        throw new Error('Video element not found');
      }
      
      return Promise.resolve();
      
    } catch (error) {
      console.error('❌ Camera setup error:', error);
      setCameraStatus('error');
      setCameraEnabled(false);
      
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
      return Promise.reject(error);
    }
  }, [stream, isBackendAvailable, startProcessing]);

  // Stop camera
  const stopCamera = useCallback(() => {
    console.log('Stopping camera...');
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.removeEventListener('loadeddata', () => {});
    }
    
    setCameraEnabled(false);
    setCameraStatus('off');
    
    // Stop OpenCV processing
    stopProcessing();
  }, [stream, stopProcessing]);

  // Toggle camera
  const toggleCamera = useCallback(() => {
    console.log('🎬 Toggle camera clicked!');
    console.log('Current state:', { 
      cameraEnabled, 
      cameraStatus, 
      hasStream: !!stream,
      hasVideoRef: !!videoRef.current,
      isBackendAvailable
    });
    
    if (cameraEnabled || cameraStatus === 'starting') {
      console.log('🛑 Stopping camera...');
      stopCamera();
    } else {
      console.log('▶️ Starting camera...');
      setupCamera().catch(error => {
        console.error('❌ Camera setup failed:', error);
      });
    }
  }, [cameraEnabled, cameraStatus, setupCamera, stopCamera, stream, isBackendAvailable]);

  // Handle OpenCV detection results
  useEffect(() => {
    if (!lastDetection || gameState !== 'PLAYING') return;

    const { direction: detectedDirection, gesture, blink } = lastDetection;

    // Handle blink for pause
    if (blink) {
      setGameState('PAUSED');
      return;
    }

    // Handle direction change
    if (detectedDirection && detectedDirection !== direction) {
      const newDirection = detectedDirection as Direction;
      
      // Prevent reverse direction
      const opposites: Record<Direction, Direction> = {
        'UP': 'DOWN',
        'DOWN': 'UP',
        'LEFT': 'RIGHT',
        'RIGHT': 'LEFT'
      };
      
      if (opposites[direction] !== newDirection) {
        setDirection(newDirection);
        lastDirectionRef.current = newDirection;
      }
    }

    // Handle gestures
    if (gesture === 'PAUSE') {
      setGameState('PAUSED');
    } else if (gesture === 'RESET') {
      resetGame();
    }
  }, [lastDetection, gameState, direction]);

  // Record game frame for replay
  const recordFrame = useCallback((snake: Position[], food: Position, score: number, direction: Direction) => {
    if (!isRecording) return;
    
    setGameFrames(prev => [...prev, {
      snake: [...snake],
      food: { ...food },
      score,
      direction,
      timestamp: Date.now()
    }]);
  }, [isRecording]);

  // Initialize death animation
  const initDeathAnimation = useCallback((snakeHead: Position) => {
    const particles = [];
    for (let i = 0; i < 15; i++) {
      particles.push({
        x: snakeHead.x * GRID_SIZE + GRID_SIZE / 2,
        y: snakeHead.y * GRID_SIZE + GRID_SIZE / 2,
        vx: (Math.random() - 0.5) * 8,
        vy: (Math.random() - 0.5) * 8,
        life: 1.0
      });
    }
    
    setDeathAnimation({
      frame: 0,
      maxFrames: 60,
      explosionParticles: particles
    });
  }, []);

  // Check if position is valid (not hitting walls or snake body)
  const isValidPosition = useCallback((pos: Position, snakeBody: Position[]): boolean => {
    if (pos.x < 0 || pos.x >= CANVAS_WIDTH / GRID_SIZE || 
        pos.y < 0 || pos.y >= CANVAS_HEIGHT / GRID_SIZE) {
      return false;
    }

    return !snakeBody.some(segment => segment.x === pos.x && segment.y === pos.y);
  }, []);

  // Game logic - move snake and handle collisions
  const moveSnake = useCallback((currentSnake: Position[], currentDirection: Direction) => {
    const head = { ...currentSnake[0] };
    
    switch (currentDirection) {
      case 'UP': head.y -= 1; break;
      case 'DOWN': head.y += 1; break;
      case 'LEFT': head.x -= 1; break;
      case 'RIGHT': head.x += 1; break;
    }

    if (!isValidPosition(head, currentSnake)) {
      initDeathAnimation(currentSnake[0]);
      setGameState('DEATH_ANIMATION');
      setIsRecording(false);
      return currentSnake;
    }

    const newSnake = [head, ...currentSnake];
    
    if (head.x === food.x && head.y === food.y) {
      setScore(prev => prev + 10);
      setFood(generateFood(newSnake));
      recordFrame(newSnake, food, score + 10, currentDirection);
      return newSnake;
    }
    
    const finalSnake = newSnake.slice(0, -1);
    recordFrame(finalSnake, food, score, currentDirection);
    return finalSnake;
  }, [food, generateFood, isValidPosition, initDeathAnimation, recordFrame, score]);

  // Render death animation
  const renderDeathAnimation = useCallback((ctx: CanvasRenderingContext2D) => {
    const { frame, maxFrames, explosionParticles } = deathAnimation;
    
    const shakeIntensity = Math.max(0, (maxFrames - frame) / maxFrames) * 5;
    const shakeX = (Math.random() - 0.5) * shakeIntensity;
    const shakeY = (Math.random() - 0.5) * shakeIntensity;
    
    ctx.save();
    ctx.translate(shakeX, shakeY);
    
    if (frame < 15) {
      ctx.fillStyle = `rgba(255, 0, 0, ${0.6 - frame * 0.04})`;
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    }
    
    explosionParticles.forEach(particle => {
      if (particle.life > 0) {
        const alpha = particle.life;
        const size = Math.max(1, 4 * alpha);
        ctx.fillStyle = `rgba(255, ${Math.floor(255 * alpha)}, 0, ${alpha})`;
        ctx.fillRect(particle.x - size/2, particle.y - size/2, size, size);
        
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life -= 0.025;
        particle.vx *= 0.98;
        particle.vy *= 0.98;
      }
    });
    
    ctx.restore();
  }, [deathAnimation]);

  // Render game
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.strokeStyle = '#001100';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= CANVAS_WIDTH; x += GRID_SIZE) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, CANVAS_HEIGHT);
      ctx.stroke();
    }
    for (let y = 0; y <= CANVAS_HEIGHT; y += GRID_SIZE) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(CANVAS_WIDTH, y);
      ctx.stroke();
    }

    const currentSnake = gameState === 'REPLAY' && gameFrames[replayFrame] 
      ? gameFrames[replayFrame].snake 
      : snake;
    const currentFood = gameState === 'REPLAY' && gameFrames[replayFrame] 
      ? gameFrames[replayFrame].food 
      : food;

    ctx.fillStyle = '#00ff41';
    currentSnake.forEach((segment, index) => {
      const x = segment.x * GRID_SIZE;
      const y = segment.y * GRID_SIZE;
      
      if (index === 0) {
        ctx.fillRect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2);
        ctx.fillStyle = '#00cc33';
        ctx.fillRect(x + 3, y + 3, GRID_SIZE - 6, GRID_SIZE - 6);
        ctx.fillStyle = '#00ff41';
      } else {
        ctx.fillRect(x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4);
      }
    });

    ctx.fillStyle = '#ffff00';
    ctx.fillRect(currentFood.x * GRID_SIZE + 3, currentFood.y * GRID_SIZE + 3, GRID_SIZE - 6, GRID_SIZE - 6);
    
    ctx.shadowColor = '#ffff00';
    ctx.shadowBlur = 10;
    ctx.fillRect(currentFood.x * GRID_SIZE + 3, currentFood.y * GRID_SIZE + 3, GRID_SIZE - 6, GRID_SIZE - 6);
    ctx.shadowBlur = 0;

    if (gameState === 'DEATH_ANIMATION') {
      renderDeathAnimation(ctx);
    }
  }, [snake, food, gameState, gameFrames, replayFrame, renderDeathAnimation]);

  // Death animation loop
  useEffect(() => {
    if (gameState === 'DEATH_ANIMATION') {
      const animationLoop = setInterval(() => {
        setDeathAnimation(prev => {
          if (prev.frame >= prev.maxFrames) {
            setGameState('GAME_OVER');
            if (score > highScore) {
              setHighScore(score);
              localStorage.setItem('snakeHighScore', score.toString());
            }
            return prev;
          }
          return { ...prev, frame: prev.frame + 1 };
        });
      }, 50);

      return () => clearInterval(animationLoop);
    }
  }, [gameState, score, highScore]);

  // Replay loop
  useEffect(() => {
    if (gameState === 'REPLAY' && gameFrames.length > 0) {
      replayLoopRef.current = window.setInterval(() => {
        setReplayFrame(prev => {
          if (prev >= gameFrames.length - 1) {
            return 0;
          }
          return prev + 1;
        });
      }, 150 / replaySpeed);
    } else {
      if (replayLoopRef.current) {
        clearInterval(replayLoopRef.current);
      }
    }

    return () => {
      if (replayLoopRef.current) {
        clearInterval(replayLoopRef.current);
      }
    };
  }, [gameState, gameFrames.length, replaySpeed]);

  // Game loop
  const gameLoop = useCallback(() => {
    if (gameState !== 'PLAYING') return;

    setSnake(currentSnake => {
      return moveSnake(currentSnake, direction);
    });
  }, [gameState, direction, moveSnake]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (gameState === 'REPLAY') {
        switch (e.key) {
          case 'ArrowLeft':
            setReplayFrame(prev => Math.max(0, prev - 1));
            break;
          case 'ArrowRight':
            setReplayFrame(prev => Math.min(gameFrames.length - 1, prev + 1));
            break;
          case 'Escape':
            setGameState('MENU');
            break;
        }
        return;
      }

      if (gameState !== 'PLAYING') return;

      switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
          if (direction !== 'DOWN') setDirection('UP');
          break;
        case 'ArrowDown':
        case 's':
        case 'S':
          if (direction !== 'UP') setDirection('DOWN');
          break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
          if (direction !== 'RIGHT') setDirection('LEFT');
          break;
        case 'ArrowRight':
        case 'd':
        case 'D':
          if (direction !== 'LEFT') setDirection('RIGHT');
          break;
        case ' ':
          e.preventDefault();
          setGameState('PAUSED');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [direction, gameState, gameFrames.length]);

  // Game loop timer
  useEffect(() => {
    if (gameState === 'PLAYING') {
      gameLoopRef.current = window.setInterval(gameLoop, 150);
    } else {
      if (gameLoopRef.current) {
        clearInterval(gameLoopRef.current);
      }
    }

    return () => {
      if (gameLoopRef.current) {
        clearInterval(gameLoopRef.current);
      }
    };
  }, [gameLoop, gameState]);

  // Render loop
  useEffect(() => {
    const renderLoop = () => {
      render();
      requestAnimationFrame(renderLoop);
    };
    renderLoop();
  }, [render]);

  // Cleanup camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  const startGame = () => {
    setGameState('PLAYING');
    setSnake(INITIAL_SNAKE);
    setDirection(INITIAL_DIRECTION);
    setFood(generateFood(INITIAL_SNAKE));
    setScore(0);
    setGameFrames([]);
    setReplayFrame(0);
    setIsRecording(true);
    lastDirectionRef.current = INITIAL_DIRECTION;
  };

  const resetGame = () => {
    setGameState('MENU');
    setSnake(INITIAL_SNAKE);
    setDirection(INITIAL_DIRECTION);
    setFood({ x: 15, y: 15 });
    setScore(0);
    setGameFrames([]);
    setReplayFrame(0);
    setIsRecording(false);
    lastDirectionRef.current = INITIAL_DIRECTION;
  };

  const togglePause = () => {
    setGameState(gameState === 'PLAYING' ? 'PAUSED' : 'PLAYING');
  };

  const startReplay = () => {
    if (gameFrames.length > 0) {
      setGameState('REPLAY');
      setReplayFrame(0);
    }
  };

  const exitReplay = () => {
    setGameState('GAME_OVER');
  };

  const toggleOpenCVProcessing = () => {
    if (openCVConfig.enabled) {
      stopProcessing();
    } else {
      // First enable camera if not already enabled
      if (!cameraEnabled && cameraStatus !== 'starting') {
        setupCamera().then(() => {
          // Camera setup will automatically start processing when ready
        });
      } else if (videoRef.current && cameraEnabled) {
        startProcessing(videoRef.current);
      }
    }
  };

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono flex flex-col items-center justify-center p-4">
      {/* Scanlines effect */}
      <div className="fixed inset-0 pointer-events-none opacity-20">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-green-400 to-transparent animate-pulse" 
             style={{ 
               backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #00ff41 2px, #00ff41 4px)',
               animation: 'scanlines 2s linear infinite'
             }} />
      </div>

      <div className="relative z-10 max-w-6xl w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Game Section */}
        <div className="lg:col-span-2">
          {/* Header */}
          <div className="text-center mb-6">
            <h1 className="text-4xl font-bold mb-2 text-green-400" style={{ textShadow: '0 0 10px #00ff41' }}>
              SNAKE CV / ML
            </h1>
            <div className="flex justify-between text-sm">
              <span>SCORE: {gameState === 'REPLAY' && gameFrames[replayFrame] ? gameFrames[replayFrame].score.toString().padStart(6, '0') : score.toString().padStart(6, '0')}</span>
              <span>HIGH: {highScore.toString().padStart(6, '0')}</span>
            </div>
            {gameState === 'REPLAY' && (
              <div className="text-xs text-green-300 mt-2">
                REPLAY: {replayFrame + 1} / {gameFrames.length} (Speed: {replaySpeed}x)
              </div>
            )}
          </div>

          {/* Game Canvas */}
          <div className="relative border-2 border-green-400 rounded-lg overflow-hidden mx-auto bg-black" 
               style={{ width: CANVAS_WIDTH + 4, height: CANVAS_HEIGHT + 4 }}>
            <canvas
              ref={canvasRef}
              width={CANVAS_WIDTH}
              height={CANVAS_HEIGHT}
              className="block"
              style={{ imageRendering: 'pixelated' }}
            />
            
            {/* Game state overlays */}
            {gameState === 'MENU' && (
              <div className="absolute inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center text-center">
                <div className="mb-6">
                  <div className="text-2xl mb-4">🐍</div>
                  <p className="text-sm mb-2">Use WASD or Arrow Keys</p>
                  <p className="text-xs text-green-300 mb-4">Or enable camera + OpenCV for AI control</p>
                </div>
                <button
                  onClick={startGame}
                  className="bg-green-700 hover:bg-green-600 px-6 py-2 rounded border border-green-400 transition-colors"
                >
                  START GAME
                </button>
              </div>
            )}

            {gameState === 'PAUSED' && (
              <div className="absolute inset-0 bg-black bg-opacity-90 flex items-center justify-center">
                <div className="text-center">
                  <Pause size={48} className="mx-auto mb-4" />
                  <p className="text-lg">PAUSED</p>
                  <p className="text-sm text-green-300">Press SPACE to continue</p>
                </div>
              </div>
            )}

            {gameState === 'GAME_OVER' && (
              <div className="absolute inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center text-center">
                <div className="mb-6">
                  <div className="text-4xl mb-4">💀</div>
                  <p className="text-xl mb-2 text-red-400">GAME OVER</p>
                  <p className="text-lg mb-2">Final Score: <span className="text-yellow-400">{score}</span></p>
                  <p className="text-sm mb-4">High Score: <span className="text-green-400">{highScore}</span></p>
                  {score === highScore && score > 0 && (
                    <p className="text-yellow-400 text-sm mb-4 animate-pulse">🏆 NEW HIGH SCORE! 🏆</p>
                  )}
                </div>
                <div className="space-y-3">
                  <button
                    onClick={startGame}
                    className="bg-green-700 hover:bg-green-600 px-6 py-2 rounded border border-green-400 transition-colors block w-full"
                  >
                    PLAY AGAIN
                  </button>
                  {gameFrames.length > 0 && (
                    <button
                      onClick={startReplay}
                      className="bg-blue-700 hover:bg-blue-600 px-6 py-2 rounded border border-green-400 transition-colors block w-full flex items-center justify-center gap-2"
                    >
                      <Play size={16} />
                      WATCH REPLAY
                    </button>
                  )}
                  <button
                    onClick={resetGame}
                    className="bg-gray-700 hover:bg-gray-600 px-6 py-2 rounded border border-green-400 transition-colors block w-full"
                  >
                    MAIN MENU
                  </button>
                </div>
              </div>
            )}

            {gameState === 'REPLAY' && (
              <div className="absolute bottom-2 left-2 right-2 bg-black bg-opacity-80 p-2 rounded text-xs">
                <div className="flex justify-between items-center mb-2">
                  <button
                    onClick={() => setReplayFrame(Math.max(0, replayFrame - 10))}
                    className="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded flex items-center gap-1"
                  >
                    <SkipBack size={12} />
                  </button>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setReplaySpeed(0.5)}
                      className={`px-2 py-1 rounded ${replaySpeed === 0.5 ? 'bg-green-700' : 'bg-gray-700 hover:bg-gray-600'}`}
                    >
                      0.5x
                    </button>
                    <button
                      onClick={() => setReplaySpeed(1)}
                      className={`px-2 py-1 rounded ${replaySpeed === 1 ? 'bg-green-700' : 'bg-gray-700 hover:bg-gray-600'}`}
                    >
                      1x
                    </button>
                    <button
                      onClick={() => setReplaySpeed(2)}
                      className={`px-2 py-1 rounded ${replaySpeed === 2 ? 'bg-green-700' : 'bg-gray-700 hover:bg-gray-600'}`}
                    >
                      2x
                    </button>
                  </div>
                  <button
                    onClick={() => setReplayFrame(Math.min(gameFrames.length - 1, replayFrame + 10))}
                    className="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded flex items-center gap-1"
                  >
                    <SkipForward size={12} />
                  </button>
                </div>
                <div className="flex justify-center">
                  <button
                    onClick={exitReplay}
                    className="bg-red-700 hover:bg-red-600 px-4 py-1 rounded text-xs"
                  >
                    EXIT REPLAY
                  </button>
                </div>
              </div>
            )}
          </div>



          {/* Game Controls */}
          <div className="mt-6 space-y-4">
            {gameState === 'PLAYING' && (
              <div className="flex justify-center space-x-4">
                <button
                  onClick={togglePause}
                  className="bg-yellow-700 hover:bg-yellow-600 px-4 py-2 rounded border border-green-400 transition-colors flex items-center gap-2"
                >
                  <Pause size={16} />
                  PAUSE
                </button>
                <button
                  onClick={resetGame}
                  className="bg-red-700 hover:bg-red-600 px-4 py-2 rounded border border-green-400 transition-colors flex items-center gap-2"
                >
                  <RotateCcw size={16} />
                  RESET
                </button>
              </div>
            )}
          </div>

          {/* Instructions */}
          <div className="mt-6 text-center text-xs text-green-300 space-y-1">
            {gameState === 'REPLAY' ? (
              <>
                <p>Arrow keys to navigate replay</p>
                <p>ESC to exit replay</p>
              </>
            ) : (
              <>
                <p>WASD or Arrow Keys to move</p>
                <p>SPACE to pause/resume</p>
                <p>Enable camera + OpenCV for AI controls</p>
              </>
            )}
          </div>
        </div>

        {/* Controls Panel */}
        <div className="lg:col-span-1 space-y-4">
          {/* Camera Preview Section */}
          <div className="bg-gray-900 border border-green-400 rounded-lg p-4">
            <h3 className="text-green-400 font-bold text-center mb-4">📹 Camera Control</h3>
            
            <div className="text-center">
              <button
                onClick={toggleCamera}
                className={`${
                  cameraEnabled || cameraStatus === 'starting' 
                    ? 'bg-red-700 hover:bg-red-600' 
                    : 'bg-blue-700 hover:bg-blue-600'
                } px-4 py-2 rounded border border-green-400 transition-colors flex items-center gap-2 mx-auto mb-4`}
                disabled={cameraStatus === 'starting'}
              >
                {cameraEnabled || cameraStatus === 'starting' ? <CameraOff size={16} /> : <Camera size={16} />}
                {cameraStatus === 'starting' ? 'STARTING...' : 
                 cameraEnabled ? 'STOP CAMERA' : 'START CAMERA'}
              </button>
              
              {/* Camera Preview Area */}
              <div className="relative border-2 border-green-400 rounded-lg bg-black mx-auto" style={{ width: '100%', maxWidth: '280px', height: '210px' }}>
                {(stream && videoRef.current) ? (
                  <video
                    ref={videoRef}
                    className="w-full h-full rounded-lg"
                    controls={false}
                    muted
                    playsInline
                    autoPlay
                    style={{ 
                      transform: 'scaleX(-1)',
                      objectFit: 'cover'
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                      <Camera size={40} className="mx-auto mb-2 opacity-50" />
                      <p className="text-xs">
                        {cameraStatus === 'starting' ? 'Starting camera...' :
                         cameraStatus === 'error' ? 'Camera error' :
                         'Click "START CAMERA" above'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Status Info */}
              <div className="mt-3 text-xs space-y-1">
                <p className="text-green-300">
                  Status: <span className="text-yellow-400">{cameraStatus}</span>
                </p>
                <p className="text-blue-300">
                  Stream: <span className="text-yellow-400">{stream ? 'Active' : 'None'}</span> | 
                  Backend: <span className="text-yellow-400">{isBackendAvailable ? 'Connected' : 'Offline'}</span>
                </p>
                {openCVConfig.enabled && (
                  <p className="text-green-400">
                    🎯 Finger Detection: <span className="text-white">Active</span>
                  </p>
                )}
                {lastDetection?.direction && (
                  <p className="text-green-400">
                    🎯 Detected: <span className="text-white font-bold">{lastDetection.direction}</span>
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* OpenCV Controls */}
          <OpenCVControls
            isBackendAvailable={isBackendAvailable}
            isConnected={isConnected}
            config={openCVConfig}
            error={openCVError}
            onModeChange={setDetectionMode}
            onSensitivityChange={setSensitivity}
            onToggleProcessing={toggleOpenCVProcessing}
            onCheckBackend={checkBackend}
          />
          
          {/* Detection Status */}
          {lastDetection && openCVConfig.enabled && (
            <div className="mt-4 bg-gray-900 border border-green-400 rounded-lg p-3">
              <h4 className="text-green-400 font-medium mb-2">🎯 Live Detection</h4>
              <div className="text-xs space-y-1">
                <p>Mode: <span className="text-yellow-400">{openCVConfig.mode}</span></p>
                {lastDetection.direction && (
                  <p>Direction: <span className="text-green-400">{lastDetection.direction}</span></p>
                )}
                {lastDetection.gesture && (
                  <p>Gesture: <span className="text-blue-400">{lastDetection.gesture}</span></p>
                )}
                {lastDetection.blink && (
                  <p>Blink: <span className="text-red-400">Detected</span></p>
                )}
                <p>Calibrated: <span className={lastDetection.calibrated ? 'text-green-400' : 'text-yellow-400'}>
                  {lastDetection.calibrated ? 'Yes' : 'Calibrating...'}
                </span></p>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes scanlines {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }
      `}</style>
    </div>
  );
};

export default SnakeGame;