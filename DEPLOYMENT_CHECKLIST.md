# Render.com Deployment Checklist

## Pre-Deployment Checklist ✓

- [ ] Generate a strong SECRET_KEY and update environment variable
- [ ] Review all environment variables in `.env.example`
- [ ] Verify GitHub repository is connected to Render.com
- [ ] Ensure all code is committed and pushed to GitHub
- [ ] Create PostgreSQL database on Render.com
- [ ] Note the DATABASE_URL from PostgreSQL service

## Environment Variables to Set ✓

Essential:
- [ ] `SECRET_KEY` - Generate using Django secret key generator
- [ ] `DEBUG` - Set to `False`
- [ ] `ALLOWED_HOSTS` - Your Render domain + custom domains
- [ ] `CSRF_TRUSTED_ORIGINS` - HTTPS URLs only
- [ ] `DATABASE_URL` - From PostgreSQL service

Email (Choose one):
- [ ] `EMAIL_HOST` - SMTP server (smtp.gmail.com, etc.)
- [ ] `EMAIL_HOST_USER` - Email account
- [ ] `EMAIL_HOST_PASSWORD` - App password or token
- [ ] `DEFAULT_FROM_EMAIL` - Sender email
- [ ] `SITE_URL` - Your deployed URL

OAuth (Optional):
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `GITHUB_CLIENT_ID`
- [ ] `GITHUB_CLIENT_SECRET`

Payment Gateways (Optional):
- [ ] `STRIPE_PUBLISHABLE_KEY`
- [ ] `STRIPE_SECRET_KEY`
- [ ] `PAYSTACK_PUBLIC_KEY`
- [ ] `PAYSTACK_SECRET_KEY`

Other:
- [ ] `GROQ_API_KEY` (if using AI features)

## Deployment Process ✓

1. [ ] Push code to GitHub
   ```bash
   git add -A
   git commit -m "Configure for Render.com deployment"
   git push
   ```

2. [ ] Create PostgreSQL Database on Render
   - Go to render.com → New → PostgreSQL
   - Copy connection string

3. [ ] Create Web Service on Render
   - New → Web Service
   - Select GitHub repository
   - Build Command: `bash build.sh`
   - Start Command: `gunicorn mywork.wsgi:application`
   - Select free tier

4. [ ] Add Environment Variables
   - Set all variables from checklist above

5. [ ] Connect PostgreSQL Database
   - Select your PostgreSQL instance in service settings

6. [ ] Deploy
   - Click "Deploy" and monitor logs

## Post-Deployment ✓

1. [ ] Wait for build to complete (~3-5 minutes)
2. [ ] Check deployment logs for errors
3. [ ] Access your app URL
4. [ ] Run in Shell tab:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. [ ] Test admin panel: `/admin`
6. [ ] Test homepage and main features
7. [ ] Check static files load properly
8. [ ] Test email functionality
9. [ ] Test OAuth login (Google/GitHub)

## Troubleshooting ✓

If deployment fails:
- [ ] Check Render dashboard logs
- [ ] Verify `build.sh` path is correct
- [ ] Ensure all environment variables are set
- [ ] Check SECRET_KEY is actually set (not empty)
- [ ] Verify DATABASE_URL format

If static files don't load:
- [ ] Check `STATIC_URL` and `STATIC_ROOT` in settings
- [ ] Verify `collectstatic` ran during build
- [ ] Check browser console for 404 errors
- [ ] Clear browser cache

If database migration fails:
- [ ] Check PostgreSQL service is created
- [ ] Verify DATABASE_URL in environment
- [ ] Check migration files are present
- [ ] Review migration logs in Render shell

## Custom Domain Setup ✓

- [ ] Purchase domain from registrar
- [ ] Add CNAME record pointing to Render
- [ ] Add to `ALLOWED_HOSTS` environment variable
- [ ] Add to `CSRF_TRUSTED_ORIGINS` (HTTPS version)
- [ ] Update OAuth redirect URIs in Google/GitHub console
- [ ] Wait for SSL certificate (usually 5-10 minutes)

## Security Review ✓

- [ ] DEBUG is set to `False`
- [ ] SECRET_KEY is strong and unique
- [ ] No secrets in version control
- [ ] HTTPS is enforced
- [ ] ALLOWED_HOSTS is properly configured
- [ ] CSRF_TRUSTED_ORIGINS is set
- [ ] Email backend uses real SMTP server
- [ ] API keys are in environment variables

## Performance Optimization ✓

- [ ] Static files are compressed (WhiteNoise enabled)
- [ ] Database queries are optimized
- [ ] Caching is configured (Redis optional)
- [ ] Gunicorn workers are tuned
- [ ] Image sizes are optimized

---

## Useful Links

- [Render.com Dashboard](https://dashboard.render.com)
- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/)
- [Gunicorn Documentation](https://gunicorn.org/)

---

**Last Updated:** June 2026
**Configuration Status:** ✅ Ready for Deployment
