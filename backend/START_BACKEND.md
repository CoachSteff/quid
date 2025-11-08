# How to Start the EMIS Backend

## ⚠️ Important: Use Virtual Environment

The backend requires packages that are installed in the virtual environment (`venv/`).

**DO NOT use system Python directly** - you'll get `ModuleNotFoundError: No module named 'fastapi'`

---

## ✅ Correct Methods to Start Backend

### Method 1: Start Script (Recommended)
```bash
cd backend
./start.sh
```

**What it does:**
- Automatically activates virtual environment
- Loads `.env` file via app.py
- Starts server on port 38153

---

### Method 2: Direct venv Python
```bash
cd backend
venv/bin/python app.py
```

**Best for:**
- Running in background
- Automated scripts
- When you don't want to activate venv

---

### Method 3: Activate venv first
```bash
cd backend
source venv/bin/activate
python app.py
```

**Best for:**
- Interactive development
- Running multiple commands
- Staying in venv for CLI usage

To deactivate later:
```bash
deactivate
```

---

## ❌ Common Mistakes

### Wrong: System Python
```bash
cd backend
python app.py  # ❌ Uses system Python - will fail!
```

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:** Use one of the correct methods above.

---

### Wrong: Wrong Directory
```bash
# Don't run from project root
python backend/app.py  # ❌ Can't find modules
```

**Fix:** Always `cd backend` first.

---

## 🧪 Verify Backend is Running

### Check Health
```bash
curl http://localhost:38153/
```

**Expected:**
```json
{
  "status": "ok",
  "service": "Generic Web Scraping API",
  "version": "1.0.0"
}
```

### List Available Sites
```bash
curl http://localhost:38153/sites
```

**Expected:**
```json
{
  "sites": [
    {
      "site_id": "emis",
      "name": "VITO EMIS Portal",
      ...
    }
  ]
}
```

### Test Query
```bash
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "water treatment"}'
```

**Expected:** JSON response with 100 results (takes ~8s with session reuse)

---

## 🔧 Using the CLI

The CLI also requires the virtual environment:

### Wrong
```bash
cd backend
./scrape query emis "test"  # ❌ Will fail if scrape script doesn't use venv
```

### Correct
```bash
cd backend
source venv/bin/activate
./scrape query emis "test"
```

**Or check if the `scrape` script has shebang:**
```bash
cat scrape | head -1
# If it's: #!/usr/bin/env python
# Then it needs venv activated first
```

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: No module named 'fastapi'
**Cause:** Running with system Python instead of venv Python

**Fix:** Use one of the correct methods above

---

### Error: Address already in use
**Cause:** Backend is already running on port 38153

**Fix:** Kill existing process
```bash
# Find process
ps aux | grep app.py

# Kill it
pkill -f app.py

# Or kill specific PID
kill <PID>
```

---

### Error: Cannot connect to backend
**Cause:** Backend not running

**Fix:** Start backend using correct method

**Check if running:**
```bash
curl http://localhost:38153/
# or
ps aux | grep app.py
```

---

## 📦 Check venv Installation

### Verify venv exists
```bash
cd backend
ls -la venv/
```

### Check Python version
```bash
venv/bin/python --version
# Should show: Python 3.9+ (e.g., Python 3.13.7)
```

### Check installed packages
```bash
venv/bin/pip list
# Should include: fastapi, playwright, pydantic, etc.
```

### Reinstall packages if needed
```bash
venv/bin/pip install -r requirements.txt
```

---

## 🚀 Quick Start (Copy/Paste)

```bash
# Navigate to backend
cd backend

# Start backend
./start.sh

# In another terminal - test it works
curl http://localhost:38153/

# Run a test query
source venv/bin/activate
./scrape query emis "water"
```

---

## 📝 Background vs Foreground

### Foreground (see logs)
```bash
cd backend
./start.sh
# Press Ctrl+C to stop
```

### Background (daemon)
```bash
cd backend
nohup venv/bin/python app.py > backend.log 2>&1 &
# Check logs: tail -f backend.log
# Stop: pkill -f app.py
```

---

## 🔑 Environment Variables

Backend automatically loads `.env` file if it exists:

```bash
# Check .env exists
cd backend
ls -la .env

# View template
cat .env.example

# Copy and configure
cp .env.example .env
# Edit .env with your credentials
```

**Required in .env:**
```
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password
```

---

## 📊 Performance Expectations

- **Port:** 38153 (not 8000!)
- **First query:** ~28s (authentication)
- **Subsequent:** ~8s (session reuse)
- **Results:** 100 records per query
- **Memory:** ~200-300MB

---

## ✅ Summary

**Always use virtual environment Python:**
```bash
# ✅ Good
venv/bin/python app.py

# ✅ Good
source venv/bin/activate && python app.py

# ✅ Good
./start.sh

# ❌ Bad
python app.py
```

**Default port: 38153** (configured in app.py)

**Check it works:** `curl http://localhost:38153/`
