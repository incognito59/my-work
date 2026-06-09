# Render.com Deployment Guide

## 📋 Summary of Configuration Changes

Your Django application has been configured for Render.com deployment. Here's what was set up:

### ✅ Files Created/Modified:

1. **requirements.txt** - Added all necessary Python packages including:
   - `gunicorn` - WSGI server for production
   - `whitenoise` - Static files serving
   - `dj-database-url` - PostgreSQL database URL parsing
   - `psycopg2-binary` - PostgreSQL adapter
   - All existing dependencies

2. **mywork/settings.py** - Production-ready configuration:
   - Database auto-detection (PostgreSQL on Render, SQLite locally)
   - WhiteNoise middleware for static files
   - Security settings (HTTPS, CSRF protection)
   - Environment variable support

3. **build.sh** - Build script that runs:
   - Installs dependencies
   - Collects static files
   - Runs database migrations

4. **runtime.txt** - Specifies Python 3.11.7 (compatible with Django 5.1)

5. **.env.example** - Updated with Render-specific variables

6. **render.yaml** - Render.com infrastructure configuration

---

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository
```bash
git add -A
git commit -m "Configure for Render.com deployment"
git push
```

### Step 2: Create a Render.com Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account (recommended)

### Step 3: Create a PostgreSQL Database
1. In Render dashboard → "New" → "PostgreSQL"
2. Name: `retail-logistics-db`
3. Choose free tier
4. Copy the database connection string (save for Step 4)

### Step 4: Deploy Web Service
1. In Render dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `retail-logistics-core`
   - **Environment:** Python
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn mywork.wsgi:application`
4. Add Environment Variables (from .env.example):

```
DEBUG=False
SECRET_KEY=<generate-a-strong-secret-key>
ALLOWED_HOSTS=<your-render-url>.onrender.com,www.<your-domain>.com
CSRF_TRUSTED_ORIGINS=https://<your-render-url>.onrender.com
DATABASE_URL=<from-postgresql-service>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SITE_URL=https://<your-render-url>.onrender.com
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
STRIPE_PUBLISHABLE_KEY=<your-stripe-key>
STRIPE_SECRET_KEY=<your-stripe-secret>
PAYSTACK_PUBLIC_KEY=<your-paystack-key>
PAYSTACK_SECRET_KEY=<your-paystack-secret>
GROQ_API_KEY=<your-groq-api-key>
```

5. Select the PostgreSQL database connection
6. Click "Deploy"

### Step 5: Initialize Database
After deployment completes:
1. Go to your service's "Shell" tab
2. Run:
```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### Step 6: Access Your App
- Your app will be available at: `https://<service-name>.onrender.com`
- Admin panel: `https://<service-name>.onrender.com/admin`

---

## 📝 Important Notes

### Security
- ⚠️ **Generate a new SECRET_KEY** for production:
  ```python
  from django.core.management.utils import get_random_secret_key
  print(get_random_secret_key())
  ```
- Update `SECRET_KEY` environment variable with the generated key
- Keep all API keys and secrets in environment variables (never in code)

### Database
- PostgreSQL from Render is automatically configured
- Migrations run automatically during builds
- **Backup data** before making major changes

### Static Files
- WhiteNoise is configured to serve static files
- Run `python manage.py collectstatic` locally to test
- CSS, JS, and images are compressed for faster delivery

### Email
- Configure a real SMTP provider (Gmail, SendGrid, etc.)
- Gmail: Use "App Passwords" for `EMAIL_HOST_PASSWORD`
- Verify sender email address with your provider

### Custom Domain
1. In Render → Service → Settings → "Custom Domain"
2. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in environment variables
3. Update OAuth callback URLs in Google/GitHub console

---

## 🔧 Troubleshooting

### Deployment fails
- Check build logs in Render dashboard
- Verify `build.sh` has correct permissions (should be executable)
- Ensure all environment variables are set

### Static files not loading
- Run: `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATICFILES_DIRS` in settings
- WhiteNoise should automatically serve them

### Database connection error
- Verify `DATABASE_URL` format: `postgresql://user:password@host:port/dbname`
- Ensure PostgreSQL service is attached to web service
- Check service logs for connection errors

### Migrations not running
- Check build.sh has execution permissions
- View build logs to see if `python manage.py migrate` is running

---

## 📚 Useful Commands

**Local testing:**
```bash
python manage.py runserver
python manage.py collectstatic --noinput
```

**Create superuser:**
```bash
python manage.py createsuperuser
```

**Check static files:**
```bash
python manage.py findstatic --list
```

---

## 🎯 Next Steps

1. ✅ Test deployment on Render.com free tier
2. Upgrade to paid plan when ready for production
3. Set up custom domain with SSL certificate
4. Configure backup strategy for database
5. Set up monitoring and error tracking (e.g., Sentry)
6. Optimize images and cache static files

---

## 📞 Support

For issues during deployment:
- Check [Render Documentation](https://render.com/docs)
- Review [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- Check service logs in Render dashboard for specific errors
