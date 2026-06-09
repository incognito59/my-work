# Render.com Deployment Quick Reference

## 🎯 One-Page Quick Start

### Pre-Deployment (5 min)
```bash
# 1. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Commit changes
git add -A
git commit -m "Configure for Render deployment"
git push
```

### On Render Dashboard
```
Step 1: Create PostgreSQL Service
  - Type: PostgreSQL
  - Name: retail-db
  - Plan: Free (or paid)
  - Copy the DATABASE_URL

Step 2: Create Web Service
  - Source: GitHub repo
  - Name: retail-logistics-core
  - Environment: Python
  - Build Command: bash build.sh
  - Start Command: gunicorn mywork.wsgi:application

Step 3: Add Environment Variables (Critical!)
  SECRET_KEY=<your-generated-key>
  DEBUG=False
  ALLOWED_HOSTS=<render-url>.onrender.com
  DATABASE_URL=<from-postgres-service>
  EMAIL_HOST_USER=<your-email>
  EMAIL_HOST_PASSWORD=<your-app-password>
  DEFAULT_FROM_EMAIL=noreply@yourdomain.com

Step 4: Connect PostgreSQL
  - Select the database from dropdown
  - Click Deploy
```

### Post-Deployment (2 min)
```bash
# 1. Open Shell tab in Render dashboard

# 2. Create superuser
python manage.py createsuperuser

# 3. Test
- Visit https://<service-name>.onrender.com
- Admin: https://<service-name>.onrender.com/admin
```

---

## 📋 Essential Environment Variables

```env
# DJANGO (Required)
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.onrender.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.onrender.com

# DATABASE (Required)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# EMAIL (For notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SITE_URL=https://yourdomain.onrender.com

# OAUTH (Optional - for login)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# PAYMENTS (Optional)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
PAYSTACK_PUBLIC_KEY=pk_live_...
PAYSTACK_SECRET_KEY=sk_live_...
```

---

## ✅ Verification Checklist

After deployment, verify these work:

```
[ ] Homepage loads: https://<your-domain>/
[ ] Admin panel: https://<your-domain>/admin
[ ] Static files load (CSS, JS visible)
[ ] Products display with images
[ ] Login/Register works
[ ] Email sends (if configured)
[ ] Cart functionality works
[ ] No 500 errors in logs
[ ] Database connected (check admin)
```

---

## 🔧 Common Commands

```bash
# Access Render Shell
# (From Render dashboard → Service → Shell)

# View logs
tail -f /var/log/render-run.log

# Run migrations manually
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check static files
python manage.py collectstatic --dry-run

# Django shell
python manage.py shell
```

---

## 🚨 If Something Goes Wrong

| Problem | Solution |
|---------|----------|
| **Build fails** | Check render logs, ensure build.sh exists |
| **500 error** | Check Render logs, verify environment vars |
| **Static files 404** | Verify STATIC_URL, run collectstatic |
| **Database error** | Verify DATABASE_URL, ensure PostgreSQL running |
| **Email not sending** | Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD |
| **Page not loading** | Check ALLOWED_HOSTS includes your domain |
| **CSRF error** | Add domain to CSRF_TRUSTED_ORIGINS |

---

## 🔑 Getting API Keys

**Gmail App Password:**
1. Enable 2FA on Gmail
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Select Mail & Windows > Copy password

**Google OAuth:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials (Web application)
3. Add authorized redirect URI: `https://<your-domain>/accounts/google/login/callback/`

**GitHub OAuth:**
1. Settings → Developer settings → OAuth Apps
2. Callback URL: `https://<your-domain>/accounts/github/login/callback/`

**Stripe API Keys:**
- Available in [stripe.com/dashboard](https://stripe.com/dashboard)
- Use **Test keys** during development
- Use **Live keys** in production

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────┐
│       Your GitHub Repository        │
│    (with render.yaml configured)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        Render.com Dashboard         │
│  - Web Service (Python + Gunicorn)  │
│  - PostgreSQL Database              │
│  - Environment Variables            │
│  - Automatic SSL Certificate        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Your Live Application            │
│  https://<your-domain>.onrender.com │
└─────────────────────────────────────┘
```

---

## 📱 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Render Docs:** https://render.com/docs
- **Your Logs:** https://dashboard.render.com → Services → Logs
- **Render Status:** https://status.render.com

---

## 💡 Pro Tips

1. **Monitor in Production:**
   - Use Django admin to check data
   - Monitor errors via Render logs
   - Set up error tracking (Sentry.io)

2. **Optimize Performance:**
   - Enable caching (Redis optional)
   - Compress images before upload
   - Use CloudFlare (free CDN)

3. **Backup Strategy:**
   - Render provides backups
   - Export database regularly
   - Keep `.env` file locally (never commit!)

4. **Cost Management:**
   - Free tier: $0/month
   - Upgrade PostgreSQL when needed
   - Monitor resource usage

---

## 🎓 Learning Resources

- Django Docs: https://docs.djangoproject.com
- Render Docs: https://render.com/docs
- Python Documentation: https://docs.python.org
- PostgreSQL: https://www.postgresql.org/docs

---

**Last Updated:** June 2026  
**Configuration:** ✅ Complete and Ready

**Questions? Check RENDER_DEPLOYMENT_GUIDE.md for detailed instructions**
