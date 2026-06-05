📤 How to Upload Files to Your GitHub Repo
Method 1: Upload via Web Interface (Easiest)
I can see your empty repo. Let's add files:

Click "uploading an existing file" (the blue link in your screenshot)

You'll see an upload page

Create these 6 files one by one (I'll give you each file below)

📄 FILES TO UPLOAD
FILE 1: README.md
Click "Create new file" → Name it: README.md → Paste this:

# Finance Manager - Portable Version

A simple, offline personal finance manager that runs on your computer. No cloud, no costs!

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python
- Download from: https://www.python.org/downloads/
- **⚠️ IMPORTANT:** Check ☑️ "Add Python to PATH" during installation

### Step 2: Download This Repository
- Click the green **"Code"** button above
- Click **"Download ZIP"**
- Extract the ZIP file to any folder (e.g., `C:\FinanceManager\`)

### Step 3: Run the App
- Double-click **`START.bat`** (Windows)
- Wait 1-2 minutes for first-time setup
- Browser opens automatically!

## 📋 What's Included

- ✅ Income & expense tracking
- ✅ Investment management (Banks, Post Office, Insurance)
- ✅ Custom institutions
- ✅ Dashboard with charts
- ✅ PDF report generation
- ✅ Completely offline
- ✅ **$0 cost - forever!**

## 💻 System Requirements

- Windows 7/8/10/11
- Python 3.8 or higher
- 100 MB free space
- No internet required (after setup)

## 🔐 Default Login

- **Email:** admin@financeapp.com
- **Password:** admin123

(Create your own account after first login)

## 💾 Your Data

Stored locally at:
C:\Users\YourName\AppData\Roaming\FinanceManager\finance.db


**Backup:** Copy this file  
**Restore:** Replace this file

## ❓ Troubleshooting

### "Python is not installed"
- Install Python from python.org
- Make sure to check "Add Python to PATH"
- Restart computer

### "Port already in use"
- Close any apps using port 8001
- Or restart your computer

### Still not working?
Open Command Prompt in the folder and run:
```cmd
pip install -r requirements.txt
python server_desktop.py
Then open browser to: http://localhost:8001

📞 Support
Check Python is installed: python --version
Check pip works: pip --version
Read the error messages in the terminal window
📜 License
Free to use for personal and commercial purposes.

Enjoy your financial freedom! 💰
