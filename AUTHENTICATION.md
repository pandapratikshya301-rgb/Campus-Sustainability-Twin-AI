# Campus Sustainability Twin AI - Authentication System

## Overview

The Campus Sustainability Twin AI system now includes a complete user authentication system with session management. Users can register, login, and their sessions persist for 7 days without needing to sign in again.

## Features

### 1. User Registration
- Users can create accounts with:
  - Full Name
  - Email Address
  - Phone Number
  - Password (securely hashed with SHA-256)
- Duplicate email/phone validation
- Beautiful registration interface with SDG-themed design

### 2. User Login
- Login with email/phone and password
- Session tokens generated with `secrets.token_urlsafe(32)`
- 7-day session persistence (604,800 seconds)
- Automatic session verification on page load

### 3. Session Management
- Session tokens stored in browser's localStorage
- Automatic token verification on dashboard access
- Secure logout functionality
- Session cleanup on logout

### 4. Protected Endpoints
- Complaint submission requires authentication
- User complaints tracking
- Dashboard access control

## Database Schema

### Tables

#### 1. users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 2. sessions
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

#### 3. user_complaints
```sql
CREATE TABLE user_complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    complaint_id TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

## API Endpoints

### Authentication Endpoints

#### 1. Register User
```
POST /api/auth/register
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "password": "securepassword"
}

Response:
{
    "success": true,
    "message": "Registration successful",
    "token": "session_token_here",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

#### 2. Login
```
POST /api/auth/login
Content-Type: application/json

{
    "identifier": "john@example.com",  // email or phone
    "password": "securepassword"
}

Response:
{
    "success": true,
    "message": "Login successful",
    "token": "session_token_here",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

#### 3. Verify Session
```
POST /api/auth/verify
Content-Type: application/json

{
    "token": "session_token_here"
}

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

#### 4. Logout
```
POST /api/auth/logout
Content-Type: application/json

{
    "token": "session_token_here"
}

Response:
{
    "success": true,
    "message": "Logged out successfully"
}
```

### Protected Endpoints

#### Submit Complaint (Requires Authentication)
```
POST /api/complaint/submit
Content-Type: application/json
Authorization: Bearer session_token_here

{
    "complaint": "Water leakage in Building A",
    "location": "Building A, Floor 2",
    "users_affected": 50,
    "date": "15-06-2026"
}
```

#### Get User Complaints
```
GET /api/user/complaints
Authorization: Bearer session_token_here

Response:
{
    "success": true,
    "complaints": [
        {
            "Complaint_ID": "C001",
            "Complaint": "Water leakage...",
            "Category": "Water",
            "Priority": "High",
            ...
        }
    ]
}
```

## Frontend Integration

### Login Page (`/login`)
- Beautiful gradient design with SDG icons
- Tabbed interface for Login/Register
- Form validation
- Session token storage in localStorage
- Automatic redirect to dashboard on successful login

### Dashboard Authentication Flow
1. **Page Load**: Check for session token in localStorage
2. **Token Verification**: Verify token with backend API
3. **Valid Session**: Display dashboard with user info
4. **Invalid/Missing Token**: Redirect to login page
5. **Logout**: Clear token and redirect to login

### JavaScript Functions

```javascript
// Check authentication on page load
async function checkAuthentication() {
    const token = localStorage.getItem('session_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    // Verify token with backend
    const response = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
    });
    const data = await response.json();
    if (!data.success) {
        localStorage.removeItem('session_token');
        window.location.href = '/login';
    }
}

// Logout function
async function logout() {
    const token = localStorage.getItem('session_token');
    await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
    });
    localStorage.removeItem('session_token');
    window.location.href = '/login';
}

// Submit complaint with authentication
async function handleComplaintSubmit(e) {
    e.preventDefault();
    const token = localStorage.getItem('session_token');
    const response = await fetch('/api/complaint/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ /* complaint data */ })
    });
}
```

## Security Features

### 1. Password Security
- Passwords hashed using SHA-256
- Never stored in plain text
- Secure comparison during login

### 2. Session Security
- Cryptographically secure tokens (32 bytes)
- Token expiration (7 days)
- Automatic session cleanup
- Token validation on every protected request

### 3. Input Validation
- Email format validation
- Phone number validation
- Duplicate user prevention
- SQL injection prevention (parameterized queries)

### 4. Authorization
- Decorator-based route protection (`@login_required`)
- Token verification middleware
- User context in protected routes

## Usage Guide

### For Users

#### First Time Setup
1. Navigate to `http://localhost:5000/login`
2. Click on "Register" tab
3. Fill in your details:
   - Full Name
   - Email Address
   - Phone Number
   - Password
4. Click "Register"
5. You'll be automatically logged in and redirected to dashboard

#### Subsequent Logins
1. Navigate to `http://localhost:5000/login`
2. Enter your email/phone and password
3. Click "Login"
4. Your session will persist for 7 days

#### Submitting Complaints
1. Once logged in, navigate to "Submit Complaint" section
2. Fill in complaint details
3. Submit - your complaint will be linked to your account
4. View your complaints in "My Complaints" section

#### Logout
1. Click the "Logout" button in the top-right corner
2. You'll be redirected to the login page

### For Developers

#### Adding Protected Routes
```python
from modules.database import Database

db = Database()

@app.route('/api/protected/endpoint', methods=['POST'])
@login_required
def protected_endpoint():
    user = request.user  # User info available via decorator
    # Your protected logic here
    return jsonify({'success': True})
```

#### Accessing User Info in Protected Routes
```python
@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    user = request.user
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    })
```

## Database File

- **Location**: `campus_ai.db` (in project root)
- **Type**: SQLite3
- **Auto-created**: Yes (on first run)
- **Backup**: Recommended to backup regularly

## Testing Authentication

### Manual Testing
1. Start the Flask app: `python app.py`
2. Open browser: `http://localhost:5000/login`
3. Register a new user
4. Verify redirect to dashboard
5. Check user info displayed in header
6. Submit a complaint
7. Logout and login again
8. Verify session persistence

### API Testing with curl

#### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","phone":"1234567890","password":"test123"}'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com","password":"test123"}'
```

#### Submit Complaint (with token)
```bash
curl -X POST http://localhost:5000/api/complaint/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"complaint":"Test complaint","location":"Test location","users_affected":10,"date":"15-06-2026"}'
```

## Troubleshooting

### Issue: "Session expired" message
**Solution**: Your session has expired after 7 days. Simply login again.

### Issue: Can't register with same email
**Solution**: Email addresses must be unique. Use a different email or login with existing account.

### Issue: Dashboard redirects to login immediately
**Solution**: 
1. Check if session token exists in localStorage (F12 > Application > Local Storage)
2. Verify Flask app is running
3. Check browser console for errors

### Issue: "Unauthorized" error when submitting complaint
**Solution**: 
1. Verify you're logged in
2. Check if session token is being sent in Authorization header
3. Try logging out and logging in again

## Future Enhancements

1. **Password Reset**: Email-based password reset functionality
2. **Two-Factor Authentication**: SMS/Email OTP verification
3. **Role-Based Access**: Admin, User, Moderator roles
4. **OAuth Integration**: Login with Google, Microsoft, etc.
5. **Session Management UI**: View and revoke active sessions
6. **Account Settings**: Update profile, change password
7. **Email Verification**: Verify email on registration
8. **Rate Limiting**: Prevent brute force attacks

## Files Modified/Created

### New Files
- `modules/database.py` - Database management and authentication logic
- `templates/login.html` - Login/Register portal
- `AUTHENTICATION.md` - This documentation

### Modified Files
- `app.py` - Added authentication routes and decorators
- `static/js/dashboard.js` - Added authentication checks and logout
- `templates/index.html` - Added user info display area

## Support

For issues or questions about the authentication system:
1. Check this documentation
2. Review the code comments in `modules/database.py`
3. Check Flask app logs for error messages
4. Verify database file exists and has correct permissions

---

**Last Updated**: June 15, 2026
**Version**: 1.0.0