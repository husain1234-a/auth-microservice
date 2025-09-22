# Authentication Microservice

A secure, production-ready authentication microservice using FastAPI and Next.js with Firebase integration.

## Features

- **Google OAuth Login** via Firebase Authentication
- **Phone Number Authentication** with SMS OTP
- **Secure Session Management** using HTTP-only cookies
- **Rate Limiting** on OTP endpoints
- **CORS Protection** with credential support
- **Input Validation** and error handling
- **Production-ready** with Docker support

## Architecture

### Backend (FastAPI)
- Firebase Admin SDK for token verification
- Redis for rate limiting
- HTTP-only secure cookies for sessions
- Comprehensive input validation
- RESTful API design

### Frontend (Next.js)
- Firebase Client SDK for authentication flows
- App Router architecture
- TypeScript support
- Tailwind CSS styling
- Secure API communication

## Security Features

- **XSS Protection**: HTTP-only cookies, input sanitization
- **CSRF Protection**: SameSite cookies, CORS configuration
- **Rate Limiting**: Redis-based OTP abuse prevention
- **Session Security**: Firebase session cookies with revocation
- **Input Validation**: Pydantic schemas, phone number validation

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.11+
- Redis
- Firebase project with Authentication enabled

### Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication with Google and Phone providers
3. Generate a service account key for Admin SDK
4. Get web app configuration for client SDK

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Configure Firebase credentials in `.env`

5. Start Redis:
```bash
redis-server
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment file:
```bash
cp .env.local.example .env.local
```

4. Configure Firebase client settings in `.env.local`

5. Run the development server:
```bash
npm run dev
```

### Docker Setup

1. Copy environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

2. Configure environment variables

3. Start all services:
```bash
docker-compose up --build
```

## API Endpoints

### Authentication Routes

- `POST /auth/google-login` - Google OAuth login
- `POST /auth/send-otp` - Validate phone and prepare OTP
- `POST /auth/verify-otp` - Verify OTP and create session
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout and clear session

### Health Check

- `GET /health` - Service health status

## Deployment

### Backend Deployment (Google Cloud Run)

1. Build and push Docker image:
```bash
docker build -t gcr.io/PROJECT_ID/auth-backend ./backend
docker push gcr.io/PROJECT_ID/auth-backend
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy auth-backend \
  --image gcr.io/PROJECT_ID/auth-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend Deployment (Vercel)

1. Connect repository to Vercel
2. Configure environment variables
3. Deploy automatically on push

## Security Considerations

### Backend Security
- Firebase Admin SDK for server-side token verification
- HTTP-only, secure, SameSite cookies
- Rate limiting on sensitive endpoints
- CORS configuration for trusted origins
- Input validation with Pydantic schemas

### Frontend Security
- Firebase Client SDK for authentication flows only
- No sensitive data in client-side storage
- HTTPS enforcement in production
- Input sanitization before API calls
- Session validation with backend

## Separation of Responsibilities

### Frontend Responsibilities
- User interface and experience
- Firebase authentication flow initiation
- ID token acquisition
- Client-side input validation
- Routing and navigation

### Backend Responsibilities
- Token verification and validation
- Session management and security
- Rate limiting and abuse prevention
- Business logic enforcement
- Database operations (if applicable)

## Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

## Environment Variables

### Backend (.env)
- Firebase service account credentials
- Redis connection URL
- CORS origins
- Session cookie configuration

### Frontend (.env.local)
- Firebase client configuration
- API URL for backend communication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License