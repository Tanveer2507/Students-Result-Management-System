# 🚀 Deployment Guide - Student Result Management System

This guide will help you deploy the SRMS project to various hosting platforms and generate a live access link.

## 📋 Table of Contents
1. [PythonAnywhere (Free & Recommended)](#pythonanywhere-deployment)
2. [Render (Free)](#render-deployment)
3. [Railway (Free)](#railway-deployment)
4. [Heroku](#heroku-deployment)

---

## 🌐 PythonAnywhere Deployment (Recommended for Beginners)

PythonAnywhere offers free hosting for Django applications.

### Step 1: Create Account
1. Go to [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free "Beginner" account
3. Verify your email

### Step 2: Open Bash Console
1. Click on "Consoles" tab
2. Start a new "Bash" console

### Step 3: Clone Repository
```bash
git clone https://github.com/Tanveer2507/Students-Result-Management-System.git
cd Students-Result-Management-System
```

### Step 4: Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 srms-env
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Configure Settings
```bash
nano srms_project/settings.py
```

Update these settings:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
STATIC_ROOT = '/home/yourusername/Students-Result-Management-System/staticfiles'
```

### Step 7: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 8: Run Migrations
```bash
python manage.py migrate
```

### Step 9: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 10: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Set source code directory: `/home/yourusername/Students-Result-Management-System`
6. Set working directory: `/home/yourusername/Students-Result-Management-System`

### Step 11: Configure WSGI File
Click on WSGI configuration file and replace content with:
```python
import os
import sys

path = '/home/yourusername/Students-Result-Management-System'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'srms_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 12: Set Virtual Environment
In the "Virtualenv" section, enter:
```
/home/yourusername/.virtualenvs/srms-env
```

### Step 13: Configure Static Files
In "Static files" section, add:
- URL: `/static/`
- Directory: `/home/yourusername/Students-Result-Management-System/staticfiles`

### Step 14: Reload Web App
Click the green "Reload" button

### 🎉 Your Live URL
Your site will be live at: `https://yourusername.pythonanywhere.com`

---

## 🎨 Render Deployment

Render offers free hosting with automatic deployments from GitHub.

### Step 1: Prepare for Deployment

1. Add `gunicorn` to requirements.txt:
```bash
echo "gunicorn>=21.0.0" >> requirements.txt
```

2. Create `build.sh` file:
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

3. Make it executable:
```bash
chmod +x build.sh
```

4. Update settings.py:
```python
import os
DEBUG = False
ALLOWED_HOSTS = ['.onrender.com']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Step 2: Deploy on Render

1. Go to [https://render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** srms-project
   - **Environment:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn srms_project.wsgi:application`
6. Click "Create Web Service"

### 🎉 Your Live URL
Your site will be live at: `https://srms-project.onrender.com`

---

## 🚂 Railway Deployment

Railway offers free hosting with easy GitHub integration.

### Step 1: Prepare Files

1. Add `gunicorn` to requirements.txt
2. Create `Procfile`:
```
web: gunicorn srms_project.wsgi --log-file -
```

3. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn srms_project.wsgi",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Deploy on Railway

1. Go to [https://railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway will auto-detect Django and deploy

### Step 3: Configure Environment
Add environment variables:
- `DJANGO_SETTINGS_MODULE` = `srms_project.settings`
- `PYTHON_VERSION` = `3.10`

### 🎉 Your Live URL
Railway will provide a URL like: `https://srms-project.up.railway.app`

---

## 🔴 Heroku Deployment

### Step 1: Install Heroku CLI
Download from [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Prepare Files

1. Add to requirements.txt:
```
gunicorn>=21.0.0
dj-database-url>=2.0.0
whitenoise>=6.5.0
```

2. Create `Procfile`:
```
web: gunicorn srms_project.wsgi
```

3. Create `runtime.txt`:
```
python-3.10.12
```

4. Update settings.py:
```python
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ['.herokuapp.com']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Step 3: Deploy

```bash
heroku login
heroku create srms-project
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku open
```

### 🎉 Your Live URL
Your site will be live at: `https://srms-project.herokuapp.com`

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is stored in environment variables
- [ ] `ALLOWED_HOSTS` is properly configured
- [ ] Database credentials are secure
- [ ] Email credentials are in environment variables
- [ ] HTTPS is enabled
- [ ] CSRF protection is enabled
- [ ] Static files are properly served

---

## 📧 Email Configuration

For production, update email settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

---

## 🐛 Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
python manage.py collectstatic
```

### Database Errors
```bash
python manage.py makemigrations
python manage.py migrate
```

### Permission Errors
```bash
chmod +x manage.py
chmod +x build.sh
```

---

## 📞 Support

If you encounter issues:
1. Check the deployment logs
2. Verify all environment variables
3. Ensure requirements.txt is up to date
4. Contact: admin@srms.com

---

## 🎯 Quick Start Commands

### Local Development
```bash
python manage.py runserver
```

### Production Check
```bash
python manage.py check --deploy
```

### Create Admin
```bash
python manage.py createsuperuser
```

---

Made with ❤️ by Tanveer Kakar
