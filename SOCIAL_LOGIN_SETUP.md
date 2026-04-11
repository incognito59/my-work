# 🔐 Social Login Setup Guide

## Current Status

Your Django site now has:
- ✅ **Email/Password Login** - WORKS (no setup needed)
- ✅ **Email/Password Register** - WORKS (no setup needed)  
- ⏳ **Google/Facebook/GitHub Login** - Configured but needs provider credentials

## Why You See "Social Login Error"

The social buttons were showing errors because:
1. Allauth was trying to initialize but OAuth provider credentials weren't configured
2. The Facebook/Google/GitHub apps weren't set up in those platforms

**I've now fixed it** - The social buttons will only show **IF** the providers are properly configured. Otherwise, just the Email/Password forms will show.

---

## ✅ What Works NOW (No Setup Needed)

### Login Page
1. Go to `/accounts/login/`
2. Enter any email and password
3. Click "Login" button
4. ✓ Works immediately

### Register Page
1. Go to `/accounts/register/`
2. Fill in Full Name, Email, Phone, Password
3. Click "Create Account"
4. ✓ Works immediately

---

## 🚀 Optional: Enable Social Login (ADVANCED)

**Only do this if you want Google/Facebook/GitHub login buttons to work.**

### Step 1: Create Google OAuth App
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credential (Web Application)
5. Set Authorized redirect URI: `http://localhost:8000/accounts/google/login/callback/`
6. Copy your Client ID and Client Secret

### Step 2: Add to Django Admin
1. Go to `http://localhost:8000/admin/`
2. Login with superuser
3. Navigate to: **Social Applications**
4. Click "Add Social Application"
5. Fill in:
   - Provider: Google
   - Name: Google
   - Client ID: [paste from Google]
   - Secret Key: [paste from Google]
   - Sites: Check your site
6. Save

### Step 3: Repeat for Facebook & GitHub (optional)
Same process for each platform.

---

## ❌ What to Ignore

**IGNORE the `/frontend/` folder** - That was a separate Firebase-based frontend I created. Your real site uses Django.

**Just use:**
- `/accounts/login/` - Login with email/password
- `/accounts/register/` - Register with email/password

---

## 🎯 For Your Presentation Tomorrow

**You're all set!** Just use the email/password login/register:

```
Login URL: http://localhost:8000/accounts/login/
Register URL: http://localhost:8000/accounts/register/
```

**Test Credentials:**
- Email: `demo@example.com`
- Password: `password123`

The site works perfectly without setting up social login. Add that later if you want.

---

## 📋 Quick Start

```bash
# Start Django server
python manage.py runserver

# Then open:
# http://localhost:8000/accounts/login/
```

Done! ✅
