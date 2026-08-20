# 🚀 Start RAGForge Server

## Option 1: Manual Start (Recommended for Testing)

Open a terminal and run:

```bash
cd backend
python app/main.py
```

Server will start on: **http://127.0.0.1:8000**

## Option 2: Using Uvicorn Directly

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Option 3: With Auto-Reload (Development)

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## ✅ Verify Server is Running

### Quick Check
```bash
curl http://127.0.0.1:8000/api/health
```

### Run Test Script
```bash
python test_website.py
```

### Open in Browser
- **Frontend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/api/docs
- **Health**: http://127.0.0.1:8000/api/health

---

## 🔧 Troubleshooting

### Port 8000 Already in Use

**Windows:**
```powershell
# Find process
netstat -ano | findstr ":8000"

# Kill process (replace PID)
taskkill /F /PID <PID>
```

**Linux/Mac:**
```bash
# Find and kill
lsof -ti:8000 | xargs kill -9
```

### Import Errors

```bash
cd backend
pip install -r requirements.txt --upgrade
```

### Ollama Not Found

```bash
# Check Ollama is running
ollama list

# Start Ollama
ollama serve

# Pull model if needed
ollama pull phi3:mini
```

---

## 📊 Test Checklist

After starting the server, verify:

- [ ] Health endpoint returns 200
- [ ] Frontend loads in browser
- [ ] API docs accessible at /api/docs
- [ ] Can upload PDF (if Ollama running)
- [ ] Can query documents
- [ ] Metrics endpoint works (if auth enabled)

---

## 🎯 Expected Output

When server starts successfully, you should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 💡 Tips

1. **First Run**: May take 1-2 minutes to download embedding models
2. **Ollama Required**: For chat functionality (optional for testing)
3. **Port Change**: Edit `uvicorn.run()` in `main.py` to use different port
4. **Logs**: Check console output for errors

---

**Ready to test?** 

1. Start server (Option 1 above)
2. Run: `python test_website.py`
3. Open: http://127.0.0.1:8000
