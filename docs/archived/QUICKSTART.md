# Quick Start Guide - Local Virtual Environment

## First Time Setup (5 minutes)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browser
playwright install chromium

# 6. Create .env file
cp .env.example .env
# Edit .env and add your EMIS credentials

# 7. Start server
python app.py
```

## Daily Usage (30 seconds)

```bash
cd backend
source venv/bin/activate  # If not already activated
python app.py
```

**OR** use the helper script (auto-activates venv):

```bash
cd backend
./start.sh
```

## Verify It's Working

Open another terminal and test:

```bash
curl http://localhost:38153/
```

Should return: `{"status":"ok","service":"EMIS Scraping API"}`

## Troubleshooting

**"Module not found" errors?**
- Make sure venv is activated: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**Server on wrong port (8000)?**
- You started it wrong! Use `python app.py` NOT `uvicorn app:app`
- See `PORT_CONFIGURATION.md` for details

**Port already in use?**
- Kill existing process: `lsof -ti :38153 | xargs kill`
- Or change PORT in `.env`

## Need More Help?

- Detailed setup: `SETUP_LOCAL.md`
- Port issues: `PORT_CONFIGURATION.md`
- Main README: `../README.md`

