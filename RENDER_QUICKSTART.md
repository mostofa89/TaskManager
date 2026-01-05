# Quick Start: Deploy to Render

## Option 1: PostgreSQL on Render (Easiest - Recommended)

### Step 1: Create PostgreSQL Database
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Name: `task-manager-db`
4. Region: `Oregon (US West)` or closest to you
5. Plan: **Free**
6. Click **"Create Database"**
7. Wait for it to provision (1-2 minutes)

### Step 2: Deploy Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `task-manager` (this becomes your-app-name.onrender.com)
   - **Environment**: `Python`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn Task_Manager.wsgi:application --bind 0.0.0.0:$PORT`

4. **Environment Variables** (click "Add Environment Variable"):
   ```
   PYTHON_VERSION = 3.13.4
   SECRET_KEY = [Click "Generate" to auto-generate]
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   CSRF_TRUSTED_ORIGINS = https://task-manager.onrender.com
   DATABASE_URL = [Select "From Database" → Choose "task-manager-db" → "Internal Database URL"]
   ```
   
   **IMPORTANT**: Update `CSRF_TRUSTED_ORIGINS` with YOUR actual URL (e.g., `https://your-service-name.onrender.com`)

5. Click **"Create Web Service"**
6. Wait for build to complete (3-5 minutes)

### Step 3: Run Initial Setup
1. In your web service dashboard, click **"Shell"** tab
2. Run these commands:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Follow prompts to create admin account

### Step 4: Access Your Site
- **Live Site**: `https://task-manager.onrender.com` (or your chosen name)
- **Admin Panel**: `https://task-manager.onrender.com/admin`

---

## Option 2: External MySQL Database

### Prerequisites
- A publicly accessible MySQL server with:
  - Host address (NOT localhost)
  - Database name
  - Username and password
  - Port (usually 3306)

### Deploy Steps
1. Follow **Step 2** from Option 1 above
2. **Environment Variables**:
   ```
   PYTHON_VERSION = 3.13.4
   SECRET_KEY = [Generate]
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   CSRF_TRUSTED_ORIGINS = https://your-service.onrender.com
   DB_HOST = your-mysql-host.com
   DB_NAME = taskmanager
   DB_USER = your_mysql_user
   DB_PASSWORD = your_mysql_password
   DB_PORT = 3306
   ```

3. Click **"Create Web Service"**
4. Migrations will run automatically if DB is accessible
5. If migrations were skipped, run them manually in Shell:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## Troubleshooting

### Build Failed: "Can't connect to MySQL server on 'localhost'"
**Cause**: Database environment variables not set

**Solution**:
1. Go to web service → **Environment** tab
2. Add `DATABASE_URL` (for PostgreSQL) OR `DB_HOST` + other DB vars (for MySQL)
3. Make sure `DB_HOST` is NOT "localhost" for external MySQL
4. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

### "DisallowedHost" Error
**Cause**: `ALLOWED_HOSTS` or `CSRF_TRUSTED_ORIGINS` not configured

**Solution**:
1. Go to **Environment** tab
2. Set `ALLOWED_HOSTS` = `.onrender.com`
3. Set `CSRF_TRUSTED_ORIGINS` = `https://YOUR-ACTUAL-SERVICE-NAME.onrender.com`
4. Redeploy

### Static Files Not Loading
**Cause**: Collectstatic failed or Whitenoise issue

**Solution**: Already handled automatically. If issues persist:
```bash
python manage.py collectstatic --clear --noinput
```

### Database Connection Works But No Tables
**Cause**: Migrations didn't run

**Solution**:
```bash
# In Render Shell
python manage.py migrate
python manage.py createsuperuser
```

---

## Updates & Redeployment

Every push to `main` branch triggers automatic redeployment on Render.

**Manual redeployment**:
1. Go to your web service dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Or: **"Clear build cache & deploy"** (if dependencies changed)

---

## Free Tier Limitations

Render Free tier:
- Web service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free (shared across all services)
- PostgreSQL database: 1GB storage, expires after 90 days

**To keep service active**: Upgrade to paid plan ($7/month)

---

## Production Checklist

Before going live:
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set correct `ALLOWED_HOSTS`
- [ ] Set correct `CSRF_TRUSTED_ORIGINS` with https://
- [ ] Database backups configured
- [ ] Environment variables secured
- [ ] Admin account created
- [ ] Test all functionality

---

## Support Resources

- [Render Docs](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Full Deployment Guide](DEPLOYMENT.md)
