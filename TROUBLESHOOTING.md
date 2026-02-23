# 🔧 Troubleshooting Guide

## Common Issues and Solutions

---

## 🚨 Installation Issues

### Issue: "Python is not recognized as an internal or external command"

**Problem:** Python not installed or not in PATH

**Solutions:**
1. Install Python from https://python.org/downloads
2. During installation, check "Add Python to PATH"
3. Or manually add Python to PATH:
   ```powershell
   # Find Python location
   where python
   
   # Add to PATH (Windows)
   $env:Path += ";C:\Path\To\Python"
   ```

### Issue: "pip: command not found"

**Problem:** pip not installed or not in PATH

**Solutions:**
```powershell
# Reinstall pip
python -m ensurepip --upgrade

# Or use python -m pip instead
python -m pip install -r requirements.txt
```

### Issue: "Failed to build opencv-python"

**Problem:** Missing build tools or incompatible version

**Solutions:**
1. Try headless version:
   ```powershell
   pip uninstall opencv-python
   pip install opencv-python-headless
   ```

2. Install Visual C++ Build Tools (Windows):
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select "Desktop development with C++"

3. Use pre-compiled wheels:
   ```powershell
   pip install opencv-python --only-binary :all:
   ```

### Issue: "No module named 'backend'"

**Problem:** Running from wrong directory or missing `__init__.py`

**Solutions:**
1. Make sure you're in the project root directory:
   ```powershell
   cd c:\Users\mourish\Desktop\Projects\AI-Driven-LinkedIn-Event-Content-Generation
   ```

2. Check `backend/__init__.py` exists:
   ```powershell
   dir backend\__init__.py
   ```

3. Ensure virtual environment is activated:
   ```powershell
   .\venv\Scripts\Activate
   ```

---

## 🔐 LinkedIn Authentication Issues

### Issue: "LinkedIn authentication failed"

**Problem:** Incorrect credentials or configuration

**Solutions:**
1. Verify credentials in `.env`:
   ```ini
   LINKEDIN_CLIENT_ID=your_actual_client_id
   LINKEDIN_CLIENT_SECRET=your_actual_client_secret
   ```

2. Check redirect URI matches EXACTLY:
   - In `.env`: `http://localhost:8000/auth/linkedin/callback`
   - In LinkedIn Developer Portal: Same URL
   - No trailing slashes
   - Correct port (8000)

3. Verify products are approved:
   - Go to https://www.linkedin.com/developers/apps
   - Select your app → "Products" tab
   - "Share on LinkedIn" should show "Approved"
   - "Sign In with LinkedIn" should show "Approved"

### Issue: "Redirect URI mismatch"

**Problem:** LinkedIn redirect URI doesn't match configuration

**Solutions:**
1. In LinkedIn Developer Portal:
   - Go to "Auth" tab
   - Under "OAuth 2.0 settings"
   - Click "Add redirect URL"
   - Enter: `http://localhost:8000/auth/linkedin/callback`
   - Click "Update"

2. In `.env` file:
   ```ini
   LINKEDIN_REDIRECT_URI=http://localhost:8000/auth/linkedin/callback
   ```

3. Restart the server after changes

### Issue: "Access token expired"

**Problem:** LinkedIn token expired or invalid

**Solutions:**
1. Simply reconnect:
   - Click "Reconnect LinkedIn" button
   - Authorize again
   - Token will refresh automatically

2. Clear database and reconnect:
   ```powershell
   # Stop server (Ctrl+C)
   del linkedin_event_curator.db
   python main.py
   # Reconnect LinkedIn
   ```

### Issue: "OAuth popup blocked by browser"

**Problem:** Browser blocking popup window

**Solutions:**
1. Allow popups for localhost:
   - Click popup blocked icon in address bar
   - Select "Always allow popups from localhost"

2. Or open in new tab manually:
   - Right-click "Connect LinkedIn"
   - Select "Open in new tab"

---

## 📤 Upload & Processing Issues

### Issue: "No files uploaded" or upload fails silently

**Problem:** Invalid file format or size

**Solutions:**
1. Check file format:
   - Only JPEG (.jpg, .jpeg) and PNG (.png) supported
   - Convert other formats using image editor

2. Check file size:
   - Max 50MB total recommended
   - Individual files < 10MB recommended
   - Compress large images if needed

3. Check file permissions:
   ```powershell
   # Ensure upload directory is writable
   icacls uploads /grant Users:F
   ```

### Issue: "Maximum 20 files allowed"

**Problem:** Trying to upload too many files

**Solution:**
- Upload in batches of 10-15 images
- Create multiple events for larger galleries

### Issue: Processing takes too long or freezes

**Problem:** Large images or slow system

**Solutions:**
1. Compress images before uploading:
   - Use tools like TinyPNG, ImageOptim
   - Target 1-2MB per image

2. Reduce number of images:
   - Upload 10 instead of 20
   - Process in batches

3. Check system resources:
   ```powershell
   # Windows Task Manager
   # Check CPU and Memory usage
   ```

4. Close other applications

### Issue: "All images marked as blurry"

**Problem:** Blur threshold too strict or images actually blurry

**Solutions:**
1. Adjust threshold in `.env`:
   ```ini
   BLUR_THRESHOLD=150  # Increase for more lenient
   ```

2. Use higher quality source images:
   - Minimum 1920x1080 resolution recommended
   - Avoid heavily compressed images
   - Use proper camera focus

### Issue: "No duplicates detected" when there are obvious duplicates

**Problem:** Duplicate threshold too lenient

**Solution:**
Adjust in `.env`:
```ini
DUPLICATE_THRESHOLD=8  # Increase to catch more similarities
```

---

## 📱 LinkedIn Posting Issues

### Issue: "Failed to post to LinkedIn"

**Problem:** Various API or authentication issues

**Solutions:**
1. Check authentication:
   - Status should show "Connected"
   - If not, click "Reconnect LinkedIn"

2. Check image selection:
   - At least 1 image must be selected
   - Maximum 9 images per post (LinkedIn limit)

3. Check network connection:
   ```powershell
   ping linkedin.com
   ```

4. View detailed error:
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for error messages

### Issue: "Images not appearing in LinkedIn post"

**Problem:** Upload failed or format issue

**Solutions:**
1. Verify image format:
   - Must be JPEG or PNG
   - No animated GIFs
   - No WebP format

2. Check image size:
   - LinkedIn max: 8MB per image
   - Compress if needed

3. Try with fewer images:
   - Start with 1 image
   - Gradually increase

### Issue: "Post succeeds but doesn't appear on profile"

**Problem:** Post visibility or LinkedIn delay

**Solutions:**
1. Check post visibility:
   - App posts as "Public" by default
   - May take 1-2 minutes to appear

2. Refresh LinkedIn profile:
   - Clear browser cache
   - Log out and back in

3. Check LinkedIn activity feed:
   - Go to "Me" → "Posts & Activity"
   - Should appear there

### Issue: "Caption not appearing in post"

**Problem:** Caption encoding or API issue

**Solutions:**
1. Avoid special characters in caption:
   - Remove emojis temporarily
   - Use plain ASCII text

2. Check caption length:
   - LinkedIn max: 3,000 characters
   - Shorter captions recommended

---

## 🗄️ Database Issues

### Issue: "Database locked" error

**Problem:** Multiple processes accessing database

**Solutions:**
1. Stop all instances:
   ```powershell
   # Press Ctrl+C in all terminals
   # Check for running processes
   Get-Process -Name python
   ```

2. If stuck, delete and recreate:
   ```powershell
   # Backup first
   copy linkedin_event_curator.db linkedin_event_curator.db.backup
   # Delete
   del linkedin_event_curator.db
   # Restart server
   python main.py
   ```

### Issue: "Table does not exist"

**Problem:** Database not initialized properly

**Solution:**
```powershell
# Delete database
del linkedin_event_curator.db
# Restart server (will recreate)
python main.py
```

### Issue: Data not persisting between sessions

**Problem:** Database path issue or permissions

**Solutions:**
1. Check `.env` file:
   ```ini
   DATABASE_URL=sqlite:///./linkedin_event_curator.db
   ```

2. Check file permissions:
   ```powershell
   icacls linkedin_event_curator.db
   ```

3. Verify database file exists:
   ```powershell
   dir linkedin_event_curator.db
   ```

---

## 🌐 Server & Network Issues

### Issue: "Address already in use" / Port 8000 in use

**Problem:** Another process using port 8000

**Solutions:**
1. Find and kill process:
   ```powershell
   # Find process
   netstat -ano | findstr :8000
   
   # Kill process (replace PID)
   taskkill /PID <PID> /F
   ```

2. Or use different port:
   ```powershell
   uvicorn main:app --port 8001
   # Then open http://localhost:8001
   ```

### Issue: "Cannot connect to server" after starting

**Problem:** Firewall or binding issue

**Solutions:**
1. Check if server actually started:
   - Look for "SERVER READY" message
   - No error messages during startup

2. Try 127.0.0.1 instead of localhost:
   ```
   http://127.0.0.1:8000
   ```

3. Check Windows Firewall:
   - Allow Python through firewall
   - Or temporarily disable firewall for testing

### Issue: "CORS error" in browser console

**Problem:** Cross-origin request issue

**Solution:**
- Should not occur in this app (same origin)
- If it does, clear browser cache
- Try incognito/private mode

---

## 🖥️ Browser Issues

### Issue: Images not displaying or broken thumbnails

**Problem:** Path issue or caching

**Solutions:**
1. Hard refresh browser:
   - Windows: Ctrl + F5
   - Mac: Cmd + Shift + R

2. Clear browser cache:
   - Settings → Privacy → Clear browsing data

3. Check upload directory:
   ```powershell
   dir uploads\event_*
   ```

4. Check browser console for errors:
   - F12 → Console tab

### Issue: "JavaScript not working" or buttons don't respond

**Problem:** JS error or not loading

**Solutions:**
1. Check browser console (F12):
   - Look for red error messages
   - Fix any reported issues

2. Verify file exists:
   ```powershell
   dir static\js\app.js
   ```

3. Clear cache and hard reload

4. Try different browser (Chrome, Firefox, Edge)

### Issue: Styling looks broken

**Problem:** CSS not loading

**Solutions:**
1. Verify file exists:
   ```powershell
   dir static\css\styles.css
   ```

2. Clear browser cache

3. Check browser DevTools:
   - Network tab
   - Ensure styles.css loads (200 status)

---

## ⚡ Performance Issues

### Issue: Application running slowly

**Problem:** System resources or large files

**Solutions:**
1. Close other applications

2. Check system resources:
   - Task Manager (Ctrl + Shift + Esc)
   - Ensure CPU < 80%, RAM available

3. Use smaller images

4. Process fewer images per batch

### Issue: High memory usage

**Problem:** Memory leak or large batch

**Solutions:**
1. Restart server periodically:
   ```powershell
   # Ctrl+C to stop
   python main.py
   ```

2. Process smaller batches (5-10 images)

3. Compress images before upload

---

## 🐍 Python Version Issues

### Issue: "SyntaxError" or compatibility issues

**Problem:** Python version too old

**Solutions:**
1. Check Python version:
   ```powershell
   python --version
   ```

2. Must be 3.9 or higher

3. Update Python:
   - Download from https://python.org/downloads
   - Install newer version
   - Recreate virtual environment:
     ```powershell
     rmdir /s venv
     python -m venv venv
     .\venv\Scripts\Activate
     pip install -r requirements.txt
     ```

---

## 📋 Configuration Issues

### Issue: Settings not taking effect

**Problem:** `.env` file not loaded or incorrect format

**Solutions:**
1. Check `.env` file location:
   - Must be in project root
   - Same directory as `main.py`

2. Check file name:
   - Must be exactly `.env` (not `.env.txt`)
   - Windows: Enable "Show file extensions"

3. Restart server after changes:
   ```powershell
   # Ctrl+C to stop
   python main.py
   ```

4. Check format:
   ```ini
   # No spaces around =
   QUALITY_THRESHOLD=0.6  # ✅ Correct
   QUALITY_THRESHOLD = 0.6  # ❌ Wrong (spaces)
   ```

---

## 🆘 Emergency Fixes

### Nuclear Option: Complete Reset

If nothing else works:

```powershell
# 1. Stop server
# Press Ctrl+C

# 2. Backup important data
copy .env .env.backup
copy linkedin_event_curator.db linkedin_event_curator.db.backup

# 3. Clean everything
rmdir /s venv
rmdir /s uploads
del linkedin_event_curator.db

# 4. Reinstall
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# 5. Restore config
copy .env.backup .env

# 6. Restart
python main.py
```

### Get More Help

If you're still stuck:

1. **Check logs:**
   - Server console output
   - Browser console (F12)
   - Windows Event Viewer

2. **Test individual components:**
   ```powershell
   # Test Python
   python --version
   
   # Test imports
   python -c "import cv2; print('OpenCV OK')"
   python -c "import fastapi; print('FastAPI OK')"
   ```

3. **Search GitHub Issues:**
   - Similar problems may have solutions

4. **Create minimal test case:**
   - Try with 1 simple image
   - No special features
   - Narrow down the problem

---

## ✅ Preventive Measures

### Best Practices to Avoid Issues

1. **Always use virtual environment**
   ```powershell
   .\venv\Scripts\Activate
   ```

2. **Keep dependencies updated**
   ```powershell
   pip install --upgrade -r requirements.txt
   ```

3. **Regular backups**
   ```powershell
   copy linkedin_event_curator.db backups\db_$(Get-Date -Format "yyyyMMdd").db
   ```

4. **Monitor system resources**
   - Don't run on low-spec machines
   - Close unnecessary applications

5. **Use quality images**
   - Good source = good results
   - Proper format and size

6. **Test after changes**
   - Always test with sample images
   - Verify end-to-end workflow

---

## 📞 Quick Diagnostic Commands

Copy and run these to diagnose issues:

```powershell
# Check Python installation
python --version
pip --version

# Check virtual environment
.\venv\Scripts\python --version

# Check dependencies
pip list | Select-String -Pattern "fastapi|opencv|pillow|sqlalchemy"

# Check files
dir main.py
dir .env
dir backend\*.py
dir static\css\styles.css
dir static\js\app.js

# Check server
netstat -ano | findstr :8000

# Test LinkedIn API (replace with your Client ID)
Invoke-WebRequest -Uri "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID"
```

---

**Remember: Most issues can be solved by:**
1. ✅ Reading error messages carefully
2. ✅ Checking configuration (.env)
3. ✅ Restarting the server
4. ✅ Clearing browser cache

**Still stuck? Check SETUP_GUIDE.md for detailed instructions!**
