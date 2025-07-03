import React from 'react';
import { Camera, CameraOff, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Hand, Settings, Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';

interface OpenCVControlsProps {
  isBackendAvailable: boolean;
  isConnected: boolean;
  config: {
    mode: 'motion' | 'gesture' | 'head';
    sensitivity: number;
    enabled: boolean;
  };
  error: string | null;
  onModeChange: (mode: 'motion' | 'gesture' | 'head') => void;
  onSensitivityChange: (sensitivity: number) => void;
  onToggleProcessing: () => void;
  onCheckBackend: () => void;
}

const OpenCVControls: React.FC<OpenCVControlsProps> = ({
  isBackendAvailable,
  isConnected,
  config,
  error,
  onModeChange,
  onSensitivityChange,
  onToggleProcessing,
  onCheckBackend
}) => {
  return (
    <div className="bg-gray-900 border border-green-400 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-green-400 font-bold text-lg flex items-center gap-2">
          <Hand size={20} />
          Finger Control
        </h3>
        
        <div className="flex items-center gap-2">
          {/* Backend Status */}
          <div className="flex items-center gap-1">
            {isBackendAvailable ? (
              <CheckCircle size={16} className="text-green-400" />
            ) : (
              <AlertCircle size={16} className="text-red-400" />
            )}
            <span className="text-xs">
              {isBackendAvailable ? 'Backend Online' : 'Backend Offline'}
            </span>
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center gap-1">
            {isConnected ? (
              <Wifi size={16} className="text-green-400" />
            ) : (
              <WifiOff size={16} className="text-gray-400" />
            )}
            <span className="text-xs">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900 border border-red-400 rounded p-2">
          <p className="text-red-400 text-xs">{error}</p>
        </div>
      )}

      {/* Camera Control */}
      <div className="space-y-3">
        <button
          onClick={onToggleProcessing}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
            config.enabled
              ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg'
              : 'bg-green-600 hover:bg-green-600 text-white shadow-lg'
          } ${!isBackendAvailable ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={!isBackendAvailable}
        >
          {config.enabled ? (
            <>
              <CameraOff size={18} />
              Stop Camera
            </>
          ) : (
            <>
              <Camera size={18} />
              Start Camera
            </>
          )}
        </button>

        {config.enabled && isBackendAvailable && (
          <>
            {/* Directional Control Grid */}
            <div className="bg-black rounded-lg p-4 border border-green-400">
              <h4 className="text-green-400 text-sm font-medium mb-3 text-center">
                Point your finger at a direction
              </h4>
              
              <div className="grid grid-cols-3 grid-rows-3 gap-2 max-w-xs mx-auto">
                {/* Top row */}
                <div></div>
                <div 
                  className="aspect-square bg-blue-900 border-2 border-blue-400 rounded-lg flex items-center justify-center hover:bg-blue-800 transition-colors cursor-pointer active:bg-blue-700"
                  data-direction="UP"
                >
                  <ArrowUp size={24} className="text-blue-400" />
                </div>
                <div></div>
                
                {/* Middle row */}
                <div 
                  className="aspect-square bg-blue-900 border-2 border-blue-400 rounded-lg flex items-center justify-center hover:bg-blue-800 transition-colors cursor-pointer active:bg-blue-700"
                  data-direction="LEFT"
                >
                  <ArrowLeft size={24} className="text-blue-400" />
                </div>
                <div className="aspect-square bg-gray-800 border-2 border-gray-600 rounded-lg flex items-center justify-center">
                  <Hand size={20} className="text-gray-400" />
                </div>
                <div 
                  className="aspect-square bg-blue-900 border-2 border-blue-400 rounded-lg flex items-center justify-center hover:bg-blue-800 transition-colors cursor-pointer active:bg-blue-700"
                  data-direction="RIGHT"
                >
                  <ArrowRight size={24} className="text-blue-400" />
                </div>
                
                {/* Bottom row */}
                <div></div>
                <div 
                  className="aspect-square bg-blue-900 border-2 border-blue-400 rounded-lg flex items-center justify-center hover:bg-blue-800 transition-colors cursor-pointer active:bg-blue-700"
                  data-direction="DOWN"
                >
                  <ArrowDown size={24} className="text-blue-400" />
                </div>
                <div></div>
              </div>
              
              <p className="text-center text-xs text-gray-400 mt-3">
                Point your finger toward any blue arrow to move the snake
              </p>
            </div>

            {/* Sensitivity Control */}
            <div className="bg-gray-800 rounded-lg p-3">
              <label className="block text-green-300 text-sm mb-2">
                Detection Sensitivity: {config.sensitivity}%
              </label>
              <input
                type="range"
                min="10"
                max="100"
                value={config.sensitivity}
                onChange={(e) => onSensitivityChange(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Less Sensitive</span>
                <span>More Sensitive</span>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-green-900 border border-green-400 rounded-lg p-3">
              <h4 className="text-green-400 text-sm font-medium mb-2">How to Play</h4>
              <div className="text-xs text-green-300 space-y-1">
                <p>1. Allow camera access when prompted</p>
                <p>2. Point your finger at the blue arrows</p>
                <p>3. Snake will move in that direction</p>
                <p>4. Adjust sensitivity if needed</p>
              </div>
            </div>
          </>
        )}

        {/* Offline State */}
        {!isBackendAvailable && (
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-3 text-center">
            <p className="text-gray-400 text-sm mb-2">Camera controls are currently offline</p>
            <button
              onClick={onCheckBackend}
              className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-xs transition-colors"
            >
              Retry Connection
            </button>
          </div>
        )}
      </div>



      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #00ff41;
          cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #00ff41;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
};

export default OpenCVControls;