# 🎯 CLIENT SHARING - COMPLETE GUIDE

## What This Does

Your clients can:
1. Open a **link you share** with them
2. See a **beautiful form** with:
   - Email input field
   - Password input field
   - **Daily Limit Slider** (0–150, default 50)
   - **CSV file upload** (drag & drop)
   - Start button
3. Click Start → Their data goes to backend
4. Backend runs `linkedin_bot.py` with their credentials & CSV
5. Results come back to their screen

---

## 📁 Folder Structure

```
your-project/
├── linkedin_bot.py          ← Your original code (UNCHANGED)
├── main_csv.py              ← NEW: FastAPI with CSV upload
├── client_new.html          ← NEW: Client form with slider
├── requirements_new.txt     ← Same dependencies
└── README.md
```

---

## ✅ STEP 1: Setup (First Time)

### On Mac Terminal:

```bash
cd ~/linkedin-auto-connect

python3 -m venv venv

source venv/bin/activate

pip install -r requirements_new.txt
```

Wait for libraries to install (2-3 minutes).

---

## ✅ STEP 2: Rename Files (Important!)

You have two options:

### Option A: Keep Both (Recommended)
- Keep `main.py` and `client.html` as-is (your old setup)
- Add `main_csv.py` and `client_new.html` (new client sharing)

### Option B: Replace (Simpler)
- Delete `main.py` and `client.html`
- Rename `main_csv.py` → `main.py`
- Rename `client_new.html` → `client.html`

We recommend **Option B** because it's cleaner.

---

## ✅ STEP 3: Verify linkedin_bot.py

You **do NOT need to edit** `linkedin_bot.py` anymore!

Your **clients** will enter their own email & password.

But if you want to use it yourself, edit:
```python
EMAIL = "your-email@example.com"
PASSWORD = "your-password"
```

---

## ✅ STEP 4: Run the Server

In Terminal:

```bash
source venv/bin/activate

python main.py
```

OR:

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## ✅ STEP 5: Test It Yourself

Open browser:

```
http://127.0.0.1:8000/client
```

You see the client form with:
- ✅ Email input
- ✅ Password input
- ✅ Daily Limit Slider (0–150, default 50)
- ✅ CSV file upload
- ✅ Start button

---

## ✅ STEP 6: Create a Test CSV

Make a file called `test.csv`:

```
linkedin_url
https://www.linkedin.com/in/person1
https://www.linkedin.com/in/person2
https://www.linkedin.com/in/person3
```

Save it on your computer.

---

## ✅ STEP 7: Test the Form

1. Go to `http://127.0.0.1:8000/client`
2. Enter:
   - Email: Your LinkedIn email
   - Password: Your LinkedIn password
   - Slider: 5 (low number for testing)
   - Upload: Your test.csv
3. Click "Start Processing"
4. Watch progress bar
5. Check Terminal to see bot running

---

## 🌐 STEP 8: Share with Clients

Once you verify it works:

### Local Network (Simple)
If client is on same WiFi as your Mac:

Get your Mac's IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Example output: `192.168.1.100`

Share this link with client:
```
http://192.168.1.100:8000/client
```

### Cloud Hosting (Production)
Deploy to Heroku, AWS, or DigitalOcean:

```bash
heroku login
heroku create your-app-name
git push heroku main
```

Your app will be at:
```
https://your-app-name.herokuapp.com/client
```

Share that link with clients.

---

## 📊 What Happens When Client Submits

1. **Client opens** `http://192.168.1.100:8000/client`
2. **Client fills form:**
   - Email: `client@example.com`
   - Password: `their-password`
   - Slider: `75`
   - CSV: `linkedin_urls.csv` (200 profiles)
3. **Client clicks** "Start Processing"
4. **Browser sends** FormData to `/api/process-csv`
5. **Backend receives** email, password, daily_limit=75, file
6. **Backend:**
   - Saves CSV to temp file
   - Sets `linkedin_bot.EMAIL = "client@example.com"`
   - Sets `linkedin_bot.PASSWORD = "their-password"`
   - Sets `linkedin_bot.DAILY_LIMIT = 75`
   - Sets `linkedin_bot.CSV_FILE = "path/to/temp.csv"`
   - Runs `linkedin_bot.main()` in background thread
7. **Client sees** progress bar while processing happens
8. **Bot logs in** with client's credentials
9. **Bot sends** connection requests (up to 75 per day)
10. **Terminal shows** all activity from bot
11. **Results saved** in `uploads/` folder

---

## 🔐 Security Notes

✅ **Client credentials are NEVER stored**
- Only used during their session
- Not saved to database
- Not sent anywhere except LinkedIn

✅ **Each client runs independently**
- Client A's CSV doesn't affect Client B
- Credentials never leak between clients
- Isolated sessions

✅ **File upload is validated**
- Must be CSV format
- Must have LinkedIn URLs in first column
- File size validated
- Temp files auto-cleaned

---

## 📝 CSV File Format

Your client must provide CSV with LinkedIn URLs in **first column**:

### ✅ Correct Format:
```csv
linkedin_url,name,company
https://www.linkedin.com/in/john,John,ABC Corp
https://www.linkedin.com/in/jane,Jane,XYZ Inc
```

### ✅ Also Works:
```csv
url
https://www.linkedin.com/in/person1
https://www.linkedin.com/in/person2
```

### ❌ Wrong Format:
```csv
name,linkedin_url
John,https://www.linkedin.com/in/john
```
(URLs not in first column)

---

## 🎯 API Endpoints

Your clients don't need to know these, but here they are:

```
GET  /                          → Health check
GET  /client                    → Serve client form
GET  /client/{token}           → Serve form with tracking
POST /api/process-csv          → Main endpoint (email, password, daily_limit, file)
```

---

## 📁 Files Created/Modified

| File | What Changed |
|------|--------------|
| `linkedin_bot.py` | NONE - same as before |
| `main_csv.py` | NEW - FastAPI with CSV upload support |
| `client_new.html` | NEW - Beautiful form with slider |
| `requirements_new.txt` | SAME - no new dependencies |

---

## 🚀 Next Time You Run It

```bash
cd ~/linkedin-auto-connect
source venv/bin/activate
python main.py
```

Then share: `http://YOUR_IP:8000/client` with clients

---

## ❓ FAQ

**Q: Can I use a password with special characters?**
A: Yes, just paste it directly into the form.

**Q: What if LinkedIn requires 2FA?**
A: The client will see a browser window asking them to verify. They complete 2FA and bot continues.

**Q: Can I see what each client is doing?**
A: Yes! Check Terminal or setup client logging (see ADVANCED section below).

**Q: How many clients can I support?**
A: Theoretically unlimited. Each runs in separate thread.

**Q: Does slider value really matter?**
A: Yes. LinkedIn has daily limits. 50-80 is safe. Higher = more risk of blocks.

**Q: What if upload fails?**
A: Try again. Make sure CSV is valid format.

---

## 🔧 ADVANCED: Logging Client Activity

If you want to track which client did what, in `main_csv.py` add this after line with `return`:

```python
# Log client activity
with open('client_activity.log', 'a') as log:
    log.write(f"[{datetime.now()}] {email} - {len(urls)} URLs - Limit: {daily_limit}\n")
```

Then check `client_activity.log` to see all client submissions.

---

## 🎉 YOU'RE DONE!

You now have a complete **client sharing system**:

✅ Beautiful web form  
✅ Slider for daily limit  
✅ CSV file upload  
✅ Secure backend processing  
✅ Real-time progress  
✅ Ready to share with clients  

**Next:** Share the link with your first client! 🚀

---

## 📞 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "Port 8000 in use" | Use `--port 8001` instead |
| "Module not found" | Run `pip install -r requirements_new.txt` |
| "Client can't access server" | Use your Mac's IP from `ifconfig` |
| "CSV upload fails" | Make sure first column has LinkedIn URLs |
| "LinkedIn login fails" | Client might need to do 2FA verification |

---

**Questions? Read the step-by-step guide again, starting from STEP 1.**

Good luck! 🚀
