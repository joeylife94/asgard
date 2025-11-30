# 🔐 JWT Authentication Guide

## Overview

Heimdall now includes JWT (JSON Web Token) based authentication for secure API access. This guide explains how to use the authentication system.

## Features

- ✅ JWT token generation and validation
- ✅ Stateless authentication
- ✅ Role-based access control (RBAC)
- ✅ Secure password encoding (BCrypt)
- ✅ Token expiration management
- ✅ In-memory user store (demo/testing)

## Default Users

For testing purposes, three users are preconfigured:

| Username | Password | Roles |
|----------|----------|-------|
| `admin` | `admin123` | ADMIN, USER |
| `developer` | `dev123` | DEVELOPER, USER |
| `user` | `user123` | USER |

⚠️ **Security Warning**: These are demo credentials. In production, replace with database-backed user management.

## API Endpoints

### Authentication Endpoints

#### 1. Login (Get JWT Token)

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response (Success - 200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzUxMiJ9...",
  "type": "Bearer",
  "expiresIn": 86400000,
  "username": "admin"
}
```

**Response (Failure - 401 Unauthorized):**
```json
{
  "error": "Invalid username or password"
}
```

#### 2. Get Current User Info

**Request:**
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzUxMiJ9...
```

**Response:**
```json
{
  "username": "admin",
  "authorities": [
    {"authority": "ROLE_ADMIN"},
    {"authority": "ROLE_USER"}
  ],
  "authenticated": true
}
```

#### 3. Validate Token

**Request:**
```http
GET /api/v1/auth/validate
Authorization: Bearer eyJhbGciOiJIUzUxMiJ9...
```

**Response:**
```json
{
  "valid": true,
  "username": "admin"
}
```

#### 4. Logout

**Request:**
```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzUxMiJ9...
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

## Usage Examples

### PowerShell (Windows)

#### 1. Login and Get Token
```powershell
$loginBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$token = $response.token
Write-Host "Token: $token"
```

#### 2. Use Token for Authenticated Request
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/me" `
    -Method GET `
    -Headers $headers
```

### cURL (Linux/Mac)

#### 1. Login and Get Token
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"
```

#### 2. Use Token for Authenticated Request
```bash
curl -X GET http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### JavaScript (Fetch API)

```javascript
// Login
const login = async () => {
  const response = await fetch('http://localhost:8080/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'admin',
      password: 'admin123',
    }),
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data.token;
};

// Authenticated request
const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8080/api/v1/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return await response.json();
};
```

### Python (requests)

```python
import requests

# Login
login_response = requests.post(
    'http://localhost:8080/api/v1/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)

token = login_response.json()['token']
print(f"Token: {token}")

# Authenticated request
headers = {'Authorization': f'Bearer {token}'}
user_response = requests.get(
    'http://localhost:8080/api/v1/auth/me',
    headers=headers
)

print(user_response.json())
```

## Authorization Rules

### Public Endpoints (No Authentication Required)
- `POST /api/v1/auth/login` - Login endpoint
- `GET /actuator/health` - Health check
- `GET /actuator/info` - Application info

### Authenticated Endpoints (Requires Valid JWT)
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/validate` - Token validation
- `GET /api/v1/**` - All other API endpoints (requires authentication)

### Admin-Only Endpoints
- `GET /api/v1/admin/**` - Requires ADMIN role

## Configuration

### Environment Variables

```bash
# JWT Secret (Base64 encoded, at least 256 bits)
JWT_SECRET=your-base64-encoded-secret-key-here

# Token expiration in seconds (default: 86400 = 24 hours)
JWT_EXPIRATION=86400
```

### Generate Secure Secret

#### PowerShell
```powershell
$bytes = New-Object byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

#### Linux/Mac
```bash
openssl rand -base64 32
```

## Security Best Practices

### ✅ DO
- Store JWT secret in environment variables
- Use HTTPS in production
- Set reasonable token expiration (24 hours recommended)
- Implement refresh token mechanism for production
- Replace in-memory users with database-backed authentication
- Implement rate limiting on login endpoint

### ❌ DON'T
- Don't commit JWT secret to version control
- Don't use default passwords in production
- Don't store tokens in localStorage (use httpOnly cookies)
- Don't expose token in URL parameters
- Don't set very long expiration times

## Testing

### Run JWT Tests

```powershell
# All tests
.\gradlew :heimdall:test

# JWT-specific tests
.\gradlew :heimdall:test --tests "*JwtTokenProviderTest"
.\gradlew :heimdall:test --tests "*AuthControllerTest"
```

## Troubleshooting

### Issue: "401 Unauthorized" on authenticated endpoints

**Solution:**
1. Check if token is included in Authorization header
2. Verify token format: `Authorization: Bearer <token>`
3. Check if token has expired
4. Validate token using `/api/v1/auth/validate` endpoint

### Issue: "Invalid JWT signature"

**Solution:**
1. Ensure JWT_SECRET matches between token generation and validation
2. Check if secret is properly Base64 encoded
3. Verify secret is at least 256 bits (32 bytes)

### Issue: "JWT token is expired"

**Solution:**
1. Login again to get a new token
2. Implement refresh token mechanism
3. Adjust JWT_EXPIRATION if needed

## Next Steps

- [ ] Implement database-backed user management
- [ ] Add refresh token mechanism
- [ ] Implement remember-me functionality
- [ ] Add OAuth2/OIDC integration
- [ ] Implement account lockout after failed attempts
- [ ] Add email verification
- [ ] Implement password reset functionality

## API Documentation

For interactive API documentation, visit:
- Swagger UI: http://localhost:8080/swagger-ui.html (Coming soon in P1)
- API Docs: http://localhost:8080/api-docs (Coming soon in P1)

## Support

For issues or questions:
- Create an issue in GitHub
- Check existing documentation in `/docs`
- Review test cases for usage examples
