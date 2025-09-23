# Authentication Microservice

This microservice handles user authentication, user management, and role-based access control using Firebase Authentication and a local database.

## Features

- **Firebase Authentication Integration**: Secure Google sign-in with Firebase
- **User Management**: Store and manage user data locally
- **Role-Based Access Control**: Support for multiple user roles (Customer, Delivery Guy, Owner, Admin)
- **Phone Number Collection**: Collect and store user phone numbers
- **Session Management**: HTTP-only cookies for secure session handling

## User Roles

- **CUSTOMER**: Default role for new users
- **DELIVERY_GUY**: For delivery personnel
- **OWNER**: For business owners
- **ADMIN**: For system administrators

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    uid VARCHAR PRIMARY KEY,           -- Firebase UID
    email VARCHAR UNIQUE,              -- User email
    phone_number VARCHAR UNIQUE,       -- User phone number
    display_name VARCHAR,              -- User display name
    photo_url VARCHAR,                 -- Profile photo URL
    role ENUM DEFAULT 'customer',      -- User role
    is_active BOOLEAN DEFAULT true,    -- Account status
    created_at TIMESTAMP,              -- Creation timestamp
    updated_at TIMESTAMP               -- Last update timestamp
);
```

## API Endpoints

### Authentication
- `POST /auth/google-login` - Google OAuth login
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### User Management
- `POST /auth/update-phone` - Update user phone number
- `POST /auth/update-role` - Update user role (Admin/Owner only)
- `GET /auth/users/{uid}` - Get user by UID

### Health Check
- `GET /` - Service info
- `GET /health` - Health check

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend/auth_service
pip install -r requirements.txt
```

### 2. Environment Configuration
Update `.env` file with your configuration:
```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com

# Application Configuration
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
SESSION_COOKIE_NAME=auth_session
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./auth_service.db
```

### 3. Run the Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Create Admin User (Optional)
```bash
python create_admin.py
```

## User Flow

### 1. Google Sign-in
1. User signs in with Google on frontend
2. Frontend sends Firebase ID token to `/auth/google-login`
3. Service verifies token with Firebase
4. Service creates/updates user in local database
5. Service returns user data with role information

### 2. Phone Number Collection
1. If user doesn't have phone number, frontend redirects to phone collection
2. User enters phone number
3. Frontend sends phone number to `/auth/update-phone`
4. Service updates user record with phone number

### 3. Role-Based Access
- Users can view their own profile
- Admins and Owners can view any profile
- Only Admins and Owners can update user roles

## Data Flow Example

When a user logs in with Google, the service receives this data:
```json
{
  "uid": "E4l3DC8LbgcD2REF1NKT7QIC0if1",
  "email": "user@example.com",
  "phone_number": null,
  "display_name": "User Name",
  "photo_url": "https://lh3.googleusercontent.com/..."
}
```

The service then:
1. Creates/updates user in database with default CUSTOMER role
2. Returns complete user data including role and timestamps
3. Sets secure session cookie for subsequent requests

## Security Features

- **Firebase Token Verification**: All tokens verified with Firebase
- **HTTP-Only Cookies**: Session cookies not accessible via JavaScript
- **Role-Based Authorization**: Endpoints protected by user roles
- **Session Management**: Secure session creation and validation

## Development

### Database Migrations
The service automatically creates tables on startup. For production, consider using Alembic for proper migrations.

### Testing
```bash
# Run with test database
DATABASE_URL=sqlite+aiosqlite:///./test_auth.db uvicorn app.main:app --port 8001
```

### API Documentation
Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc