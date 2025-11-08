# EMIS Backend - User Guide

**For non-technical users**

This guide shows you how to set up and use the EMIS backend without using the terminal.

---

## 📦 What You'll Need

- **macOS** (10.13 or later) or **Windows** (10 or later)
- **Python 3.9+** installed ([Download here](https://www.python.org/downloads/))
- **EMIS Portal credentials** (email and password)

---

## 🚀 Quick Start (3 Easy Steps)

### Step 1: Setup (One-time only)

**macOS Users:**
1. **Double-click** the file: `macos/setup-emis.command`
2. If you see a security warning:
   - Right-click the file
   - Select "Open"
   - Click "Open" in the dialog
3. Follow the on-screen instructions
4. When asked, add your EMIS credentials to the `.env` file

**Windows Users:**
1. **Double-click** the file: `windows\setup-emis.bat`
2. Follow the on-screen instructions
3. When asked, add your EMIS credentials to the `.env` file

**This installs everything you need. Only do this once!**

---

### Step 2: Start the Backend

**macOS Users:**
1. **Double-click** the file: `macos/start-emis-backend.command`
2. A terminal window will open showing:
   ```
   ✅ Starting backend on http://localhost:38153
   ```
3. **Keep this window open** while using EMIS
4. The backend is now running!

**Windows Users:**
1. **Double-click** the file: `windows\start-emis-backend.bat`
2. A command prompt window will open showing:
   ```
   ✅ Starting backend on http://localhost:38153
   ```
3. **Keep this window open** while using EMIS
4. The backend is now running!

---

### Step 3: Choose How to Use EMIS

Now that the backend is running, choose the method that works best for you:

**Option A: Use with Claude Desktop (MCP Server)** - Best if you use Claude Desktop
- **macOS**: Double-click `macos/generate-mcp-config.command`
- **Windows**: Double-click `windows\generate-mcp-config.bat`
- See the [MCP Setup Guide](MCP_CLAUDE_DESKTOP_SETUP.md) for easy setup
- Ask Claude questions like "Search EMIS for water treatment"
- No terminal needed after setup

**Option B: Use Command Line (CLI)** - Best if you prefer typing commands
- Open Terminal
- Navigate to the `backend` folder
- Type: `./scrape query emis "your search term"`
- See results instantly

Both methods are equally easy to use! Choose what fits your workflow.

---

## 🛑 Stopping the Backend

**Option 1: Close the terminal window**
- Click the red X button on the terminal window
- Or press `Ctrl+C` in the terminal

**Option 2: Use the stop script**
- **macOS**: Double-click `macos/stop-emis-backend.command`
- **Windows**: Double-click `windows\stop-emis-backend.bat`

---

## 🔧 Configuration

### Adding Your Credentials

1. Open the file: `backend/.env`
2. Find these lines:
   ```
   EMIS_EMAIL=your_email@example.com
   EMIS_PASSWORD=your_password_here
   ```
3. Replace with your actual credentials:
   ```
   EMIS_EMAIL=john.doe@company.com
   EMIS_PASSWORD=MySecurePassword123
   ```
4. Save the file
5. Restart the backend (if running)

**⚠️ Important:** Never share your `.env` file with anyone!

---

## ✅ Testing It Works

### Method 1: Web Browser
1. Start the backend
2. Open your web browser
3. Go to: http://localhost:38153
4. You should see:
   ```json
   {
     "status": "ok",
     "service": "Generic Web Scraping API",
     "version": "1.0.0"
   }
   ```

### Method 2: Check the Terminal
After starting, the terminal shows:
```
✅ Starting backend on http://localhost:38153
```

If you see this, it's working!

---

## 📁 File Overview

### Files You'll Use

| File | What It Does |
|------|-------------|
| **macOS**: `macos/setup-emis.command`<br>**Windows**: `windows\setup-emis.bat` | Sets up everything (run once) |
| **macOS**: `macos/start-emis-backend.command`<br>**Windows**: `windows\start-emis-backend.bat` | Starts the backend server |
| **macOS**: `macos/stop-emis-backend.command`<br>**Windows**: `windows\stop-emis-backend.bat` | Stops the backend server |
| `backend/.env` | Your credentials (keep private!) |

### Other Files (Don't Touch)

| File/Folder | Purpose |
|-------------|---------|
| `backend/venv/` | Python virtual environment |
| `backend/data/` | Session data (automatic) |
| `backend/*.py` | Backend code |

---

## 🐛 Troubleshooting

### "Permission Denied" When Double-Clicking

**Problem:** macOS won't let you open the file

**Solution:**
1. Right-click the file
2. Select "Open"
3. Click "Open" in the security dialog
4. This only needs to be done once per file

---

### "Port Already in Use"

**Problem:** Backend is already running

**Solution:**
1. **macOS**: Double-click `macos/stop-emis-backend.command`<br>**Windows**: Double-click `windows\stop-emis-backend.bat`
2. Wait 5 seconds
3. Try starting again

---

### "Module Not Found" Error

**Problem:** Setup didn't complete properly

**Solution:**
1. **macOS**: Double-click `macos/setup-emis.command` again<br>**Windows**: Double-click `windows\setup-emis.bat` again
2. Let it complete fully
3. Try starting the backend again

---

### Backend Won't Start

**Check these:**

1. ✅ Did you run setup script first? (`macos/setup-emis.command` or `windows\setup-emis.bat`)
2. ✅ Is Python 3 installed?
3. ✅ Did you add credentials to `.env`?
4. ✅ Is port 38153 free? (run stop script first)

**Still not working?**
- Check the terminal output for error messages
- Contact support with the error message

---

### Slow First Query

**This is normal!**

- **First query:** ~28 seconds (logging in to EMIS)
- **Next queries:** ~8 seconds (reuses session)

The backend remembers your login for 1 hour.

---

## 📊 What Happens Behind the Scenes

### When You Start the Backend:

```
1. Checks Python is installed ✓
2. Checks virtual environment exists ✓
3. Loads your credentials from .env ✓
4. Starts the API server on port 38153 ✓
5. Ready to receive queries! ✓
```

### When You Query EMIS:

```
First Time:
1. Opens browser (invisible) ✓
2. Logs in to EMIS portal (~12s) ✓
3. Searches for your query ✓
4. Extracts 100 results ✓
5. Saves session for reuse ✓
→ Total: ~28 seconds

Next Times:
1. Reuses saved session ✓
2. Searches for your query ✓
3. Extracts 100 results ✓
→ Total: ~8 seconds (81% faster!)
```

---

## 🔒 Security Notes

### Your Credentials Are Safe

- ✅ Stored in `.env` file (local only)
- ✅ Never sent anywhere except EMIS portal
- ✅ Not included in backups (`.gitignore`)
- ✅ Only readable by you

### Best Practices

- ❌ Don't share your `.env` file
- ❌ Don't commit it to git
- ❌ Don't send it via email
- ✅ Keep it in the `backend/` folder
- ✅ Use a strong EMIS password

---

## 💡 Tips & Tricks

### Keep the Backend Running

- Leave the terminal window open
- The backend stays active
- Queries are faster (session reuse)

### Multiple Queries

- You can run many queries
- Session lasts 1 hour
- After 1 hour, you'll need to log in again (automatic)

### Check If It's Running

```
1. Open browser
2. Go to: http://localhost:38153
3. See "status": "ok" → It's running!
4. See error → Not running (start it)
```

---

## 📞 Getting Help

### Check These First

1. **Error in terminal?** Read the error message
2. **Setup issues?** Run setup script again (`macos/setup-emis.command` or `windows\setup-emis.bat`)
3. **Credentials wrong?** Check `backend/.env` file
4. **Port blocked?** Run stop script (`macos/stop-emis-backend.command` or `windows\stop-emis-backend.bat`)

### Common Error Messages

| Error | Solution |
|-------|----------|
| "Module not found" | Run setup script again |
| "Port in use" | Run stop script first |
| "Permission denied" | Right-click → Open |
| "Authentication failed" | Check credentials in .env |

---

## ⚙️ Advanced Options

### Change the Port

Edit `backend/.env`:
```
PORT=8000  # Change to any available port
```

### Enable Debug Mode

Edit `backend/.env`:
```
HEADLESS=false  # See the browser window
```

### View Logs

The terminal shows all activity:
- Query requests
- Login attempts
- Errors
- Results extracted

---

## 🎯 Using EMIS - Two Easy Methods

### Method 1: MCP Server (Claude Desktop)

**Perfect for:** Users who want to ask Claude questions naturally

**Setup:**
1. Make sure backend is running (Step 2 above)
2. **macOS**: Double-click `macos/generate-mcp-config.command`<br>**Windows**: Double-click `windows\generate-mcp-config.bat`
3. Copy the configuration it shows
4. Open Claude Desktop → Settings → Developer → Edit Config
5. Paste the configuration and save
6. Restart Claude Desktop

**Usage:**
Just ask Claude: "Search EMIS for water treatment" or "What does EMIS say about waste management?"

**See:** [MCP_CLAUDE_DESKTOP_SETUP.md](MCP_CLAUDE_DESKTOP_SETUP.md) for detailed instructions

---

### Method 2: Command Line (CLI)

**Perfect for:** Users who prefer typing commands or want quick results

**Setup:**
No extra setup needed! Just make sure the backend is running.

**Usage:**
1. Open Terminal
2. Navigate to the project folder:
   ```bash
   cd backend
   ```
3. Run queries:
   ```bash
   ./scrape query emis "water treatment"
   ./scrape query emis "waste management" --format table
   ```

**See:** [docs/user/CLI_USAGE.md](docs/user/CLI_USAGE.md) for more examples

---

## 📝 Summary

### To Use EMIS Backend:

1. **Setup** (once): 
   - **macOS**: Double-click `macos/setup-emis.command`
   - **Windows**: Double-click `windows\setup-emis.bat`
2. **Start**: 
   - **macOS**: Double-click `macos/start-emis-backend.command`
   - **Windows**: Double-click `windows\start-emis-backend.bat`
3. **Choose Method**: Use MCP Server (Claude Desktop) or CLI (Terminal)
4. **Stop**: Close terminal or:
   - **macOS**: Double-click `macos/stop-emis-backend.command`
   - **Windows**: Double-click `windows\stop-emis-backend.bat`

### Remember:

- ✅ Keep terminal window open while using
- ✅ First query is slow (~28s), then fast (~8s)
- ✅ Credentials stay in `backend/.env`
- ✅ Backend runs on http://localhost:38153
- ✅ Both MCP and CLI are equally easy to use!

---

**That's it! You're ready to use the EMIS backend.** 🎉
