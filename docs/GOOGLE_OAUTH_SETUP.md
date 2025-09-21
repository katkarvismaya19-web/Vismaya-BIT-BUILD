# Google OAuth Setup Instructions

## 🔐 Secure Configuration Guide

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Google+ API" and "OAuth2 API"
4. Go to "Credentials" > "Create Credentials" > "OAuth 2.0 Client ID"
5. Configure OAuth consent screen with your app details
6. Set authorized origins:
   - `http://localhost:3000`
   - `http://127.0.0.1:3000`
   - Your production domain
7. Copy the **Client ID** (you'll need this)

### Step 2: Configure Backend Environment

1. **Open `backend/.env` file**
2. **Replace the placeholder values:**
   ```env
   # Replace this line:
   GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
   
   # With your actual Client ID:
   GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
   ```

3. **Also add your Google Client Secret:**
   ```env
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   ```

### Step 3: Configure Frontend

1. **Open `frontend/config.js`**
2. **Replace the placeholder:**
   ```javascript
   // Replace this line:
   GOOGLE_CLIENT_ID: 'your_google_client_id.apps.googleusercontent.com',
   
   // With your actual Client ID:
   GOOGLE_CLIENT_ID: '123456789-abcdefghijklmnop.apps.googleusercontent.com',
   ```

### Step 4: Update Database Schema

Run the SQL commands from `database/add_google_oauth.sql`:

```sql
ALTER TABLE Users ADD COLUMN google_id VARCHAR(255) NULL;
CREATE INDEX idx_users_google_id ON Users(google_id);
ALTER TABLE Users MODIFY COLUMN password_hash VARCHAR(255) NULL;
```

### Step 5: Install Dependencies

```bash
cd backend
pip install requests PyJWT python-dotenv
```

## 🛡️ Security Best Practices

### ✅ DO:
- Keep your Client ID in environment variables
- Use HTTPS in production
- Set proper CORS origins
- Never commit .env files to git
- Use different credentials for development and production

### ❌ DON'T:
- Put credentials directly in code
- Share your Client Secret publicly
- Use the same credentials across environments
- Commit sensitive files to version control

## 🧪 Testing

1. **Start your backend:**
   ```bash
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Open login page:**
   ```
   frontend/login.html
   ```

3. **Test Google login:**
   - Click "Continue with Google"
   - Sign in with your Google account
   - Should redirect to portfolio page

## 🔧 Troubleshooting

### Common Issues:

1. **"Google API not loaded"**
   - Check internet connection
   - Verify script loading in browser console

2. **"Invalid Google token"**
   - Verify Client ID is correct
   - Check authorized origins in Google Console

3. **Database errors**
   - Ensure database schema is updated
   - Check MySQL connection

4. **CORS errors**
   - Add your domain to Google Console
   - Check CORS settings in backend

## 🚀 Production Deployment

For production:

1. **Use environment-specific config:**
   ```bash
   # Create production .env
   cp .env .env.production
   ```

2. **Set secure cookie settings:**
   ```python
   secure=True  # Enable HTTPS-only cookies
   ```

3. **Update CORS origins:**
   ```python
   origins = ["https://yourdomain.com"]
   ```

4. **Use proper domain in Google Console**

## 📝 Notes

- The Client ID can be public (it's safe to include in frontend)
- The Client Secret must be kept private (backend only)
- Environment files are automatically ignored by git
- Test with multiple Google accounts to ensure it works properly