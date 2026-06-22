# Google OAuth Setup Guide

This guide will help you set up Google Sign-In for the Campus Sustainability Twin AI application.

## Prerequisites

- Google Account
- Access to Google Cloud Console

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name: "Campus Sustainability AI"
5. Click "Create"

### 2. Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click on it and click "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Click "Create"
4. Fill in the required information:
   - **App name**: Campus Sustainability Twin AI
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click "Save and Continue"
6. On the Scopes page, click "Add or Remove Scopes"
7. Add these scopes:
   - `email`
   - `profile`
   - `openid`
8. Click "Save and Continue"
9. Add test users (your email addresses)
10. Click "Save and Continue"

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Enter name: "Campus Sustainability Web Client"
5. Add Authorized JavaScript origins:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
6. Add Authorized redirect URIs:
   ```
   http://localhost:5000/login
   http://127.0.0.1:5000/login
   ```
7. Click "Create"
8. **IMPORTANT**: Copy the Client ID and Client Secret

### 5. Configure Your Application

1. Open your `.env` file (or create one from `.env.example`)
2. Add your Google OAuth credentials:
   ```
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```

3. Update `templates/login.html` line 244:
   ```javascript
   const GOOGLE_CLIENT_ID = 'YOUR_ACTUAL_CLIENT_ID_HERE';
   ```
   Replace with your actual Client ID

### 6. Install Required Dependencies

```bash
pip install authlib google-auth google-auth-oauthlib
```

### 7. Test the Integration

1. Start your application:
   ```bash
   python app.py
   ```

2. Navigate to `http://localhost:5000/login`

3. Click "Sign in with Google" button

4. You should see the Google Sign-In popup

5. Select your Google account

6. Grant permissions

7. You should be redirected to the dashboard

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Make sure the redirect URI in Google Cloud Console matches exactly with your application URL
- Check for trailing slashes
- Ensure you're using the correct protocol (http vs https)

### Error: "invalid_client"
- Verify your Client ID and Client Secret are correct in `.env`
- Make sure there are no extra spaces or quotes

### Error: "access_denied"
- Check if your Google account is added as a test user in OAuth consent screen
- Verify the scopes are correctly configured

### Google Sign-In button not appearing
- Check browser console for JavaScript errors
- Verify the Google Sign-In script is loading: `https://accounts.google.com/gsi/client`
- Make sure your Client ID is correctly set in the JavaScript

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use environment variables** in production
3. **Enable HTTPS** in production
4. **Regularly rotate** your Client Secret
5. **Monitor** OAuth usage in Google Cloud Console
6. **Limit scopes** to only what's necessary (email, profile, openid)

## Production Deployment

When deploying to production:

1. Update Authorized JavaScript origins and redirect URIs in Google Cloud Console with your production domain
2. Set environment variables on your hosting platform
3. Enable HTTPS
4. Move OAuth consent screen from "Testing" to "In Production"

## Features

✅ **One-Click Sign-In** - Users can sign in with their Google account
✅ **Auto-Registration** - New users are automatically registered
✅ **No Password Required** - OAuth users don't need to remember passwords
✅ **Secure** - Uses Google's OAuth 2.0 protocol
✅ **Fast** - Quick authentication process

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Google Cloud Console logs
3. Check application logs for error messages
4. Verify all configuration steps were completed

---

**Note**: This setup is for development. For production, ensure you follow all security best practices and use HTTPS.