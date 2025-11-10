// Custom start script to handle paths with exclamation marks
const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

// Set environment variables to use temp directories for cache
process.env.WEBPACK_CACHE_DIR = path.join(os.tmpdir(), 'react-app-webpack-cache');
process.env.NODE_ENV = process.env.NODE_ENV || 'development';

// Spawn react-app-rewired start
const child = spawn('npx', ['react-app-rewired', 'start'], {
  stdio: 'inherit',
  shell: true,
  env: process.env
});

child.on('error', (error) => {
  console.error('Failed to start:', error);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code);
});

