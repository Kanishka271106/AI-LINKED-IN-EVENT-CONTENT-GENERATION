# Quick Start Commands

## For Windows (PowerShell)

### First-time setup:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env with your LinkedIn credentials
notepad .env
```

### Run the application:
```powershell
# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate

# Start the server
python main.py
```

### Or use the quick start script:
```powershell
.\start.bat
```

## For macOS/Linux (Bash)

### First-time setup:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your LinkedIn credentials
nano .env
```

### Run the application:
```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Start the server
python main.py
```

## After Starting

1. Open browser to: http://localhost:8000
2. Click "Connect LinkedIn" and authorize
3. Upload your event photos
4. Review AI selections
5. Post to LinkedIn!

## Stopping the Server

Press `Ctrl+C` in the terminal

## Common Issues

### "Module not found" error
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port already in use"
```powershell
# Run on different port
uvicorn main:app --port 8001
```

### LinkedIn authentication fails
- Check .env file has correct credentials
- Verify redirect URI in LinkedIn app matches: `http://localhost:8000/linkedin/callback`
- Make sure "Share on LinkedIn" product is approved in LinkedIn Developer Portal
