import { useState, useEffect, useCallback, useRef } from 'react';

interface DetectionResult {
  direction: string | null;
  gesture: string | null;
  blink: boolean;
  calibrated: boolean;
  timestamp: number;
}

interface BackendConfig {
  mode: 'motion' | 'gesture' | 'head';
  sensitivity: number;
  enabled: boolean;
}

export const useOpenCVBackend = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isBackendAvailable, setIsBackendAvailable] = useState(false);
  const [config, setConfig] = useState<BackendConfig>({
    mode: 'motion',
    sensitivity: 50,
    enabled: false
  });
  const [lastDetection, setLastDetection] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const socketRef = useRef<any>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Check if backend is available
  const checkBackend = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5001/health');
      if (response.ok) {
        setIsBackendAvailable(true);
        setError(null);
        return true;
      }
    } catch (err) {
      setIsBackendAvailable(false);
      setError('Backend not available. Please start the Python backend.');
    }
    return false;
  }, []);

  // Initialize WebSocket connection
  const connectWebSocket = useCallback(async () => {
    if (!isBackendAvailable) return;

    try {
      // Dynamic import of socket.io-client
      const { io } = await import('socket.io-client');
      
      socketRef.current = io('http://localhost:5001', {
        transports: ['websocket', 'polling']
      });

      socketRef.current.on('connect', () => {
        console.log('Connected to OpenCV backend');
        setIsConnected(true);
        setError(null);
      });

      socketRef.current.on('disconnect', () => {
        console.log('Disconnected from OpenCV backend');
        setIsConnected(false);
      });

      socketRef.current.on('detection_result', (data: DetectionResult) => {
        setLastDetection(data);
      });

      socketRef.current.on('error', (err: any) => {
        console.error('WebSocket error:', err);
        setError(err.message || 'WebSocket connection error');
      });

    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
      setError('Failed to establish WebSocket connection');
    }
  }, [isBackendAvailable]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // Process frame via HTTP API
  const processFrame = useCallback(async (frameData: string): Promise<DetectionResult | null> => {
    if (!isBackendAvailable) return null;

    try {
      const response = await fetch('http://localhost:5001/process_frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          frame: frameData,
          mode: config.mode
        })
      });

      if (response.ok) {
        const result = await response.json();
        setLastDetection(result);
        return result;
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      console.error('Frame processing error:', err);
      setError(err instanceof Error ? err.message : 'Frame processing failed');
      return null;
    }
  }, [isBackendAvailable, config.mode]);

  // Send frame via WebSocket
  const sendFrameWebSocket = useCallback((frameData: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('frame_data', {
        frame: frameData,
        mode: config.mode
      });
    }
  }, [isConnected, config.mode]);

  // Capture frame from video element
  const captureFrame = useCallback((video: HTMLVideoElement): string | null => {
    if (!video || video.readyState < 2) return null;

    try {
      if (!canvasRef.current) {
        canvasRef.current = document.createElement('canvas');
      }

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      ctx.drawImage(video, 0, 0);
      return canvas.toDataURL('image/jpeg', 0.8);
    } catch (err) {
      console.error('Frame capture error:', err);
      return null;
    }
  }, []);

  // Start processing frames from video
  const startProcessing = useCallback((video: HTMLVideoElement) => {
    if (!isBackendAvailable || !video) return;

    videoRef.current = video;

    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Start frame processing loop
    intervalRef.current = setInterval(() => {
      const frameData = captureFrame(video);
      if (frameData) {
        if (isConnected) {
          sendFrameWebSocket(frameData);
        } else {
          processFrame(frameData);
        }
      }
    }, 150); // Process every 150ms

    setConfig(prev => ({ ...prev, enabled: true }));
  }, [isBackendAvailable, isConnected, captureFrame, sendFrameWebSocket, processFrame]);

  // Stop processing
  const stopProcessing = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setConfig(prev => ({ ...prev, enabled: false }));
    setLastDetection(null);
  }, []);

  // Update detection mode
  const setDetectionMode = useCallback(async (mode: 'motion' | 'gesture' | 'head') => {
    try {
      await fetch('http://localhost:5001/set_detection_mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode })
      });

      setConfig(prev => ({ ...prev, mode }));
    } catch (err) {
      console.error('Failed to set detection mode:', err);
    }
  }, []);

  // Update sensitivity
  const setSensitivity = useCallback(async (sensitivity: number) => {
    try {
      await fetch('http://localhost:5001/set_sensitivity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sensitivity })
      });

      setConfig(prev => ({ ...prev, sensitivity }));
    } catch (err) {
      console.error('Failed to set sensitivity:', err);
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    checkBackend().then(available => {
      if (available) {
        connectWebSocket();
      }
    });

    return () => {
      stopProcessing();
      disconnectWebSocket();
    };
  }, [checkBackend, connectWebSocket, stopProcessing, disconnectWebSocket]);

  return {
    // Status
    isBackendAvailable,
    isConnected,
    error,
    
    // Configuration
    config,
    setDetectionMode,
    setSensitivity,
    
    // Processing
    startProcessing,
    stopProcessing,
    processFrame,
    
    // Results
    lastDetection,
    
    // Utilities
    checkBackend,
    connectWebSocket,
    disconnectWebSocket
  };
};