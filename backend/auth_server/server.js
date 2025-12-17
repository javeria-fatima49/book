const express = require('express');
const cors = require('cors');
const { betterAuth } = require('better-auth');
const { toNodeHandler } = require('better-auth/node');
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

// Also handle preflight requests specifically for auth
app.options('/api/auth/*', cors());

// Initialize Better Auth with SQLite database - wrap in async function to handle errors
let auth;
async function initializeAuth() {
  try {
    auth = betterAuth({
      secret: process.env.BETTER_AUTH_SECRET || "fallback-secret-for-development",
      baseURL: process.env.BETTER_AUTH_BASE_URL || "http://localhost:3003",
      database: {
        provider: "libsql",
        url: "file:./local_auth.db" // Use libSQL with local file
      },
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
        sendEmailVerification: false, // Disable email verification for development
      },
      session: {
        expiresIn: 7 * 24 * 60 * 60 * 1000, // 7 days
        updateAge: 24 * 60 * 60 * 1000,      // 24 hours
      },
      user: {
        // Custom fields for user background information
        additionalFields: {
          developerLevel: {
            type: "string",
            required: false,
          },
          roboticsInterests: {
            type: "string",
            required: false,
          },
          preferredAiModel: {
            type: "string",
            required: false,
          },
          learningGoals: {
            type: "string",
            required: false,
          },
          programmingLanguages: {
            type: "string",
            required: false,
          },
          yearsExperience: {
            type: "number",
            required: false,
          },
        },
      },
      // Add proper error handling configuration
      socialProviders: {}, // Disable social providers for now
      account: {
        // Configure account-related settings
        accountModel: {
          // Use defaults
        }
      },
      // Add hooks for additional processing if needed
      hooks: {
        signIn: {
          after: [
            // Add any post-signin processing here if needed
            async (ctx) => {
              console.log(`User signed in: ${ctx.user.email}`);
              // Add any additional processing here
            }
          ]
        },
        signUp: {
          after: [
            // Add any post-signup processing here if needed
            async (ctx) => {
              console.log(`New user registered: ${ctx.user.email}`);
              // Add any additional processing here
            }
          ]
        }
      },
      // Make sure all required endpoints are enabled
      account: {
        accountModel: {}
      }
    });

    // Apply middleware for debugging
    app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });

    // Apply Better Auth handler first
    app.all('/api/auth/*', toNodeHandler(auth));

    // Apply express.json() AFTER the Better Auth handler for other routes
    app.use(express.json());

    // Add a simple root route to avoid 404
    app.get('/', (req, res) => {
      res.json({ message: 'Better Auth Server is running', status: 'ok' });
    });

    // Additional API route to sync user data with Python backend
    app.post('/api/sync-user', async (req, res) => {
      try {
        // Note: With current Better Auth API, session validation works differently
        // In a real implementation, you'd use the proper session validation method
        // For now, this is a placeholder for user data sync

        // Since we can't easily validate the session directly without the client token,
        // we'll implement a different approach where the frontend sends user data after auth
        const { betterAuthId, email } = req.body;

        if (!betterAuthId || !email) {
          return res.status(400).json({ error: 'betterAuthId and email required' });
        }

        // Forward user data to Python backend
        const pythonResponse = await fetch(`${process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'}/api/v1/users/link-better-auth`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            better_auth_id: betterAuthId,
            email: email
          })
        });

        if (!pythonResponse.ok) {
          throw new Error(`Python backend sync failed: ${pythonResponse.statusText}`);
        }

        const result = await pythonResponse.json();
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('User sync error:', error);
        res.status(500).json({ error: 'User sync failed' });
      }
    });

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({ status: 'healthy', service: 'Better Auth Server' });
    });

    // Start server
    const PORT = process.env.PORT || 3003;
    app.listen(PORT, () => {
      console.log(`Better Auth server running on port ${PORT}`);
      console.log(`Base URL: http://localhost:${PORT}`);
      console.log('Routes:');
      console.log('- POST /api/auth/sign-in (email)');
      console.log('- POST /api/auth/sign-up (email)');
      console.log('- GET /api/auth/session');
      console.log('- POST /api/auth/sign-out');
      console.log('- POST /api/sync-user (custom route for Python backend)');
    });
  } catch (error) {
    console.error('Failed to initialize Better Auth:', error);
    console.error('This is likely due to a database configuration issue.');
    console.error('Please ensure better-sqlite3 is properly installed for your system.');

    // Still start the server but without auth functionality
    const PORT = process.env.PORT || 3003;
    app.use(express.json());

    // Return error for auth routes since auth isn't initialized
    app.all('/api/auth/*', (req, res) => {
      res.status(500).json({ error: 'Authentication service not available due to database configuration error' });
    });

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({ status: 'partially healthy', service: 'Better Auth Server - DB issue', error: error.message });
    });

    // Additional API route to sync user data with Python backend
    app.post('/api/sync-user', async (req, res) => {
      res.status(500).json({ error: 'Service unavailable due to database configuration error' });
    });

    app.listen(PORT, () => {
      console.log(`Better Auth server running on port ${PORT} (with auth unavailable due to database error)`);
      console.log('Routes:');
      console.log('- All /api/auth/* routes: UNAVAILABLE (due to DB error)');
      console.log('- POST /api/sync-user: UNAVAILABLE (due to DB error)');
    });
  }
}

// Process unhandled promise rejections to prevent server crashes
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Start the initialization
initializeAuth();