# Better Auth Server for AI Book Project

This Node.js server handles authentication using Better Auth and integrates with the Python FastAPI backend.

## Setup

1. Navigate to the auth server directory:
```bash
cd backend/auth_server
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file with your configuration:
```env
BETTER_AUTH_SECRET=your-super-secret-key-change-this-in-production
BETTER_AUTH_BASE_URL=http://localhost:3002
PYTHON_BACKEND_URL=http://localhost:8000
```

## Running the Server

Start the Better Auth server:
```bash
npm start
```

Or for development with auto-restart:
```bash
npm run dev
```

The server will run on port 3002 by default.

## Routes

- `POST /api/auth/sign-in` - Sign in endpoint
- `POST /api/auth/sign-up` - Sign up endpoint
- `GET /api/auth/session` - Get current session
- `POST /api/auth/sign-out` - Sign out endpoint
- `POST /api/sync-user` - Sync user data with Python backend

## Integration with Docusaurus Frontend

The Docusaurus frontend is configured to communicate with this Better Auth server at `http://localhost:3002`.

## Integration with Python Backend

The Better Auth server will communicate with your Python FastAPI backend at `http://localhost:8000` for user profile data synchronization.