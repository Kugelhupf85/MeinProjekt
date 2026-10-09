# Core User API Endpoints

## 🔐 Authentication Endpoints

### Login & Logout
- **POST** `/api/auth/login/` - User login with email/username and password
- **POST** `/api/auth/logout/` - User logout (requires authentication)
- **GET** `/api/auth/check/` - Check authentication status

### Registration & Email Verification  
- **POST** `/api/auth/register/` - Register new user
- **POST** `/api/auth/verify-email/` - Verify email with token
- **POST** `/api/auth/resend-verification/` - Resend verification email

### Password Management
- **POST** `/api/auth/change-password/` - Change password (requires current password)
- **POST** `/api/auth/reset-password-request/` - Request password reset via email
- **POST** `/api/auth/reset-password-security/` - Reset password using security questions

## 👤 Profile Management Endpoints

### Current User Profile
- **GET** `/api/auth/profile/` - Get current user profile
- **PUT/PATCH** `/api/auth/profile/update/` - Update current user profile

### User Management (Admin Only)
- **GET** `/api/auth/users/` - List all users (admin only)
- **GET** `/api/auth/users/{user_id}/` - Get specific user details (admin only)
- **PATCH** `/api/auth/users/{user_id}/toggle-active/` - Toggle user active status (admin only)

## 🔒 Security Management Endpoints

### Security Questions
- **GET** `/api/auth/security-questions/` - List all active security questions (public)
- **GET** `/api/auth/user-security-questions/?email=user@example.com` - Get security questions for specific user (public)

### User Security Answers
- **GET** `/api/auth/my-security-answers/` - Get current user's security answers (without revealing answers)
- **POST** `/api/auth/set-security-answers/` - Set security answers for current user
- **DELETE** `/api/auth/clear-security-answers/` - Clear all security answers for current user

### Admin Security Management
- **GET** `/api/auth/admin/security-questions/` - List/create security questions (admin only)
- **POST** `/api/auth/admin/security-questions/` - Create new security question (admin only)
- **PATCH** `/api/auth/admin/security-questions/{question_id}/toggle/` - Toggle security question status (admin only)

---

## 📋 Demo Superuser Credentials

**Email:** `admin@arcanovi.com`  
**Password:** `AdminPass123!`  
**Name:** Dungeon Master  
**Security Questions:** 3 configured  

### Security Question Answers:
1. **Wie heißt Ihr erster Pen-and-Paper-Charakter?** → `Gandalf`
2. **Welches war Ihr erstes Rollenspielsystem?** → `DSA`  
3. **Wie heißt Ihr Lieblings-Spielmeister/DM?** → `Tolkien`

---

## 🧪 API Testing Examples

### Login
```bash
POST /api/auth/login/
{
    "username": "admin@arcanovi.com",
    "password": "AdminPass123!"
}
```

### Register User
```bash
POST /api/auth/register/
{
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User", 
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
}
```

### Set Security Answers
```bash
POST /api/auth/set-security-answers/
{
    "answers": [
        {"question_id": 1, "answer": "Gandalf"},
        {"question_id": 2, "answer": "D&D 5e"},
        {"question_id": 5, "answer": "Wizard"}
    ]
}
```

### Reset Password with Security Questions
```bash
POST /api/auth/reset-password-security/
{
    "email": "admin@arcanovi.com",
    "security_answers": [
        {"question_id": 1, "answer": "Gandalf"},
        {"question_id": 2, "answer": "DSA"}
    ],
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!"
}
```

### Change Password
```bash
POST /api/auth/change-password/
{
    "current_password": "AdminPass123!",
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!"
}
```

---

## 🎯 Features Implemented

✅ **Aspektspezifische Architektur** - Separate Serializer, Views und URLs für Auth, Profile und Security  
✅ **Email-basierte Authentifizierung** - Login mit Email oder Username  
✅ **Pen-and-Paper-spezifische Sicherheitsfragen** - 8 rollenspiel-relevante Fragen  
✅ **Vollständiger Superuser** - Mit allen Sicherheitsfeatures konfiguriert  
✅ **POST-optimierte Endpoints** - Alle Endpoints für unsichtbare POST-Requests optimiert  
✅ **Passwort-Management** - Ändern und Reset über Sicherheitsfragen  
✅ **Tabellen-Management** - CRUD-Operationen für alle User-Daten  
✅ **Session-basierte Authentifizierung** - Für Frontend-Integration  
✅ **Admin-Interface** - Für User- und Security-Question-Management  

Das System ist jetzt vollständig funktionsfähig und bereit für die Frontend-Integration! 🚀 