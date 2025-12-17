const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Enable CORS for communication with Docusaurus frontend and Python backend
app.use(cors({
  origin: [
    'http://localhost:3000',  // Docusaurus frontend
    'http://localhost:8000',  // Python backend
    'http://localhost:3001',  // Alternative Docusaurus port
    'http://localhost:8001',   // Alternative Python backend port
    'http://localhost:3003',   // Self-origin for auth requests
    'http://localhost:3002'    // Additional common Docusaurus port
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin']
}));

// Apply middleware for debugging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Parse JSON bodies
app.use(express.json());

// Mock auth endpoints for testing without database
let mockUsers = new Map(); // In-memory storage for mock users
let currentSession = null; // Simple session tracking

// Mock sign up endpoint
app.post('/api/auth/sign-up', (req, res) => {
  const { email, password, firstName, lastName, ...additionalData } = req.body;
  
  if (!email || !password || !firstName || !lastName) {
    return res.status(400).json({ 
      error: 'Missing required fields: email, password, firstName, lastName' 
    });
  }
  
  // Check if user already exists
  if (mockUsers.has(email)) {
    return res.status(409).json({ 
      error: 'A user with this email already exists' 
    });
  }
  
  // Create new user
  const userId = 'user_' + Date.now();
  const newUser = {
    id: userId,
    email,
    firstName,
    lastName,
    ...additionalData
  };
  
  mockUsers.set(email, newUser);
  
  // Create mock session
  currentSession = {
    user: newUser,
    token: 'mock-session-token-' + userId,
    createdAt: new Date().toISOString()
  };
  
  console.log('New user registered:', email);
  
  // Simulate processing time
  setTimeout(() => {
    res.json({
      user: newUser,
      session: currentSession
    });
  }, 500);
});

// Mock sign in endpoint
app.post('/api/auth/sign-in', (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({ 
      error: 'Missing email or password' 
    });
  }
  
  // Find user (in a real scenario, you would verify the password)
  const user = mockUsers.get(email);
  
  if (!user) {
    return res.status(401).json({ 
      error: 'Invalid email or password' 
    });
  }
  
  // Create mock session
  currentSession = {
    user: user,
    token: 'mock-session-token-' + user.id,
    createdAt: new Date().toISOString()
  };
  
  console.log('User signed in:', email);
  
  // Simulate processing time
  setTimeout(() => {
    res.json({
      user: user,
      session: currentSession
    });
  }, 500);
});

// Get current session
app.get('/api/auth/session', (req, res) => {
  if (currentSession) {
    res.json({
      user: currentSession.user,
      session: currentSession
    });
  } else {
    res.json({}); // No active session
  }
});

// Sign out
app.post('/api/auth/sign-out', (req, res) => {
  currentSession = null;
  res.json({ success: true });
});

// Additional API route to sync user data with Python backend
app.post('/api/sync-user', async (req, res) => {
  try {
    const { betterAuthId, email } = req.body;

    if (!betterAuthId || !email) {
      return res.status(400).json({ error: 'betterAuthId and email required' });
    }

    // In a real implementation, you would forward to the Python backend
    // For now, return a success response
    res.json({ 
      success: true, 
      data: { message: 'Sync successful', betterAuthId, email }
    });
  } catch (error) {
    console.error('User sync error:', error);
    res.status(500).json({ error: 'User sync failed' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'Mock Auth Server (no database required)',
    usersCount: mockUsers.size
  });
});

// Add a simple root route
app.get('/', (req, res) => {
  res.json({ 
    message: 'Mock Auth Server is running', 
    status: 'ok',
    endpoints: [
      'POST /api/auth/sign-up',
      'POST /api/auth/sign-in', 
      'GET /api/auth/session',
      'POST /api/auth/sign-out'
    ]
  });
});

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => {
  console.log(`Mock Auth server running on port ${PORT}`);
  console.log(`Base URL: http://localhost:${PORT}`);
  console.log('Routes (mocked):');
  console.log('- POST /api/auth/sign-up (mock)');
  console.log('- POST /api/auth/sign-in (mock)');
  console.log('- GET /api/auth/session (mock)');
  console.log('- POST /api/auth/sign-out (mock)');
  console.log('- POST /api/sync-user');
  console.log('- GET /health');
  console.log('- GET / (info)');
});