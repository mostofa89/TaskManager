# Render Deployment Guide

## Prerequisites
- A Render account at https://render.com
- Your MySQL database host credentials (or use Render PostgreSQL)
- This repository pushed to GitHub/GitLab

## Deployment Steps

### 1. Create Database (Choose One Option)

#### Option A: External MySQL Database
If you have an existing MySQL database (e.g., on your local server, PlanetScale, AWS RDS):
- Ensure it's publicly accessible
- Note down: host, port (3306), database name, username, password

#### Option B: Use Render PostgreSQL (Recommended)
1. In Render Dashboard, click "New +" → "PostgreSQL"
2. Name it (e.g., "task-manager-db")
3. Select free tier
4. Click "Create Database"
5. Copy the "Internal Database URL" (starts with `postgresql://`)

### 2. Deploy Web Service

1. **Connect Repository**
   - Click "New +" → "Web Service"
   - Connect your GitHub/GitLab repository
   - Select the repository containing this project

2. **Configure Service**
   - **Name**: `task-manager` (or your preferred name)
   - **Environment**: `Python`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or specify if in subdirectory)
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn Task_Manager.wsgi:application --bind 0.0.0.0:$PORT`

3. **Set Environment Variables**

   Click "Advanced" → Add Environment Variables:

   **Required:**
   - `SECRET_KEY`: (Auto-generated or use your own)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://YOUR-SERVICE-NAME.onrender.com` (replace with actual URL)

   **Database (Option A - MySQL):**
   - `DB_HOST`: Your MySQL host (e.g., `myserver.com`)
   - `DB_NAME`: `taskmanager` (or your database name)
   - `DB_USER`: Your MySQL username
   - `DB_PASSWORD`: Your MySQL password
   - `DB_PORT`: `3306`

   **Database (Option B - PostgreSQL):**
   - `DATABASE_URL`: Paste the Internal Database URL from step 1

4. **Create Web Service**
   - Click "Create Web Service"
   - Wait for the build to complete (3-5 minutes)

### 3. Run Migrations (If Skipped)

If migrations were skipped during build:

1. Go to your web service dashboard
2. Click "Shell" tab
3. Run:
   ```bash
   python manage.py migrate
   ```

### 4. Create Superuser

After deployment succeeds:
1. Click "Shell" tab in Render dashboard
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow prompts to create admin account

### 5. Access Your Site

- **Live URL**: `https://YOUR-SERVICE-NAME.onrender.com`
- **Admin**: `https://YOUR-SERVICE-NAME.onrender.com/admin`

## Common Issues & Solutions

### Build Fails: "Can't connect to MySQL server on 'localhost'"
**Solution**: You haven't set database environment variables yet.
- Go to your service → Environment
- Add `DATABASE_URL` OR all `DB_*` variables
- Manually redeploy

### "DisallowedHost" Error
**Solution**: 
- Add your Render URL to `ALLOWED_HOSTS`: `.onrender.com`
- Add to `CSRF_TRUSTED_ORIGINS`: `https://your-service.onrender.com`

### Static Files Not Loading
**Solution**: Already handled by Whitenoise. If issues persist:
```bash
python manage.py collectstatic --noinput
```

### Database Migration Errors
**Solution**:
- Ensure database is accessible from Render
- For MySQL: Database must be publicly accessible
- For Postgres: Use Render's Internal Database URL
- Run migrations manually via Shell

## Switching from MySQL to PostgreSQL

If you want to use PostgreSQL instead of MySQL on Render:

1. Create Render PostgreSQL database (see step 1, Option B above)
2. Update `requirements.txt`:
   ```
   Django>=6.0,<6.1
   psycopg2-binary>=2.9.9
   gunicorn>=21.2.0
   whitenoise>=6.6.0
   python-decouple>=3.8
   dj-database-url>=2.1.0
   ```
3. Set `DATABASE_URL` env var in Render
4. Redeploy

## Updating Your Deployment

Whenever you push to your `main` branch:
- Render automatically rebuilds and redeploys
- Migrations run automatically if database is configured

Manual redeployment:
- Click "Manual Deploy" → "Deploy latest commit"

## Environment Variables Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `SECRET_KEY` | Yes | Auto-generated | Django secret key |
| `DEBUG` | Yes | `False` | Never `True` in production |
| `ALLOWED_HOSTS` | Yes | `.onrender.com` | Comma-separated domains |
| `CSRF_TRUSTED_ORIGINS` | Yes | `https://app.onrender.com` | Full URL with https:// |
| `DATABASE_URL` | Option 1 | `postgresql://user:pass@host/db` | Full database URL |
| `DB_HOST` | Option 2 | `mysql.example.com` | MySQL host only |
| `DB_NAME` | Option 2 | `taskmanager` | Database name |
| `DB_USER` | Option 2 | `dbuser` | Database username |
| `DB_PASSWORD` | Option 2 | `secretpass` | Database password |
| `DB_PORT` | Option 2 | `3306` | Database port |

## Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Troubleshooting: https://render.com/docs/troubleshooting-deploys
