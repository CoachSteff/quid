# Port Configuration Guide

## ⚠️ IMPORTANT: Port 38153 vs Port 8000

The EMIS backend **MUST** run on port **38153**, not the default uvicorn port 8000.

## The Problem

When you run `uvicorn app:app` directly, uvicorn uses its default port **8000**. However, the EMIS backend is configured to use port **38153** (as specified in `.env` and `docker-compose.yml`).

This causes issues because:
- The MCP Server expects the backend on port 38153
- Docker Compose maps port 38153
- All documentation assumes port 38153

## ✅ Correct Ways to Start the Server

### Method 1: Use `python app.py` (RECOMMENDED)
```bash
cd backend
python app.py
```

This automatically:
- Loads `.env` file (via `load_dotenv()`)
- Reads `PORT=38153` from `.env`
- Starts uvicorn on the correct port

### Method 2: Use the helper script
```bash
cd backend
./start.sh
```

### Method 3: Explicitly set port with uvicorn
```bash
cd backend
PORT=38153 uvicorn app:app --port 38153
```

Or if you have `.env` loaded:
```bash
source .env  # or export variables
uvicorn app:app --port 38153
```

## ❌ Wrong Ways (Will Use Port 8000)

These commands will start the server on port 8000, which is incorrect:

```bash
# WRONG - defaults to port 8000
uvicorn app:app

# WRONG - still defaults to port 8000
uvicorn app:app --reload

# WRONG - port not specified
uvicorn app:app --host 0.0.0.0
```

## How to Verify

After starting the server, check which port it's actually using:

```bash
# Check what's listening on port 38153
lsof -i :38153

# Check what's listening on port 8000
lsof -i :8000

# Or test the health endpoint
curl http://localhost:38153/  # Should work
curl http://localhost:8000/   # Should fail if server is on 38153
```

## Troubleshooting

### Server is running on port 8000 instead of 38153

1. **Stop the server** (Ctrl+C or kill the process)
2. **Check your `.env` file** - it should have `PORT=38153`
3. **Restart using the correct method:**
   ```bash
   python app.py
   ```
4. **Verify it's on the correct port:**
   ```bash
   curl http://localhost:38153/
   ```

### Why does this happen?

When you run `uvicorn app:app` directly:
- The `if __name__ == "__main__"` block in `app.py` doesn't execute
- Uvicorn doesn't automatically read the `PORT` environment variable
- Uvicorn defaults to port 8000

When you run `python app.py`:
- The `if __name__ == "__main__"` block executes
- `load_dotenv()` loads the `.env` file
- The PORT environment variable is read
- Uvicorn is started with the correct port

## Configuration Files

- **`.env`**: Contains `PORT=38153`
- **`docker-compose.yml`**: Maps port `38153:38153` and sets `PORT=38153`
- **`app.py`**: Defaults to port 38153 if PORT env var is not set

## Summary

**Always use `python app.py` to start the server!**

This ensures:
- ✅ Correct port (38153)
- ✅ Environment variables loaded from `.env`
- ✅ Consistent behavior across environments

