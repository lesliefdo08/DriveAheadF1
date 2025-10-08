# 🚀 RENDER DEPLOYMENT GUIDE
# DriveAhead F1 Analytics Platform

## 📋 Quick Deployment Checklist

### ✅ 1. Repository Setup
- [x] GitHub repository: `lesliefdo08/DriveAheadF1` 
- [x] Branch: `master`
- [x] Root directory: `website`
- [x] All files cleaned and optimized

### ✅ 2. Render Service Configuration
```
Service Type: Web Service
Name: driveahead-f1-analytics  
Environment: Python 3
Region: Oregon (US West) or closest to you
Branch: master
Root Directory: website
```

### ✅ 3. Build Settings
```
Build Command: pip install --upgrade pip && pip install --only-binary=all -r requirements.txt || pip install -r requirements.txt
Start Command: python -m gunicorn --bind 0.0.0.0:$PORT app:app
```

### ✅ 4. Environment Variables (Copy to Render Dashboard)

**Essential Variables:**
- `LOG_LEVEL` = `INFO`
- `FLASK_ENV` = `production`
- `SECRET_KEY` = `driveahead-f1-2025-production-secret-change-this-random-key-abc123`

**API Configuration:**
- `JOLPICA_API_BASE` = `http://api.jolpi.ca/ergast/f1`
- `API_TIMEOUT` = `10`
- `API_CACHE_TTL` = `300`
- `API_RETRY_ATTEMPTS` = `3`
- `API_RETRY_DELAY` = `1.0`

**Performance Settings:**
- `DATA_REFRESH_INTERVAL` = `30000`
- `LOADING_TIMEOUT` = `5000`
- `CHART_ANIMATION_DURATION` = `1000`

**Cache Configuration:**
- `CACHE_ENABLED` = `true`
- `CACHE_TIMEOUT` = `300`
- `CACHE_MAX_SIZE` = `1000`

**F1 Data Configuration:**
- `F1_SEASON` = `2025`
- `DEFAULT_RACE_LIMIT` = `23`
- `TELEMETRY_UPDATE_INTERVAL` = `1000`

**Production Optimizations:**
- `WERKZEUG_RUN_MAIN` = `true`
- `FLASK_SKIP_DOTENV` = `true`
- `PYTHONUNBUFFERED` = `1`

## 🔗 Deployment Steps

### Step 1: Create Render Service
1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub and select `DriveAheadF1` repository

### Step 2: Configure Service
1. **Name**: driveahead-f1-analytics
2. **Branch**: master  
3. **Root Directory**: website
4. **Environment**: Python 3
5. **Plan**: Free (or upgrade as needed)

### Step 3: Set Build Commands
1. **Build Command**: 
   ```
   pip install --upgrade pip && pip install --only-binary=all -r requirements.txt || pip install -r requirements.txt
   ```
2. **Start Command**: 
   ```
   python -m gunicorn --bind 0.0.0.0:$PORT app:app
   ```

### Step 4: Add Environment Variables
Copy all the environment variables listed above to your Render service environment variables section.

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build to complete (~5-10 minutes)
3. Your app will be live at: `https://driveahead-f1-analytics.onrender.com`

## 🎯 Expected Features After Deployment

✅ **Live Race Countdown Timer** (00DAYS : 00HOURS : 00MINUTES)
✅ **Professional F1 Telemetry Interface** with real-time updates
✅ **Analytics Dashboard** with standings and predictions
✅ **Ultra-fast 1-second telemetry updates**
✅ **Professional F1 broadcast styling**
✅ **Mobile-responsive design**

## 🔧 Troubleshooting

**Build Fails?**
- Check Python version (app uses Python 3.10+)
- Verify all requirements.txt dependencies

**App Won't Start?**
- Check environment variables are set correctly
- Verify SECRET_KEY is set
- Check logs in Render dashboard

**API Issues?**
- Verify JOLPICA_API_BASE URL is accessible
- Check API timeout settings

## 📊 Monitoring

Monitor your app at:
- **Render Logs**: Check for any runtime errors
- **Performance**: Monitor response times
- **API Calls**: Track F1 data API usage

## 🚀 Go Live!

Once deployed, your F1 analytics platform will be available at:
`https://driveahead-f1-analytics.onrender.com`

Enjoy your live F1 analytics platform! 🏁