#!/usr/bin/env python3
"""
Minimal test backend for Snake CV
"""

from flask import Flask, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Test backend is running",
        "timestamp": time.time(),
        "camera_support": "basic"
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        "message": "Backend is working!",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    print("🧪 Starting Test Backend")
    print("🌐 Available at: http://localhost:5001")
    print("🔧 Health check: http://localhost:5001/health")
    print("🔧 Test endpoint: http://localhost:5001/test")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 