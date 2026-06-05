📄 FILE 6: HOWTO.md (Installation Guide)
Click "Add file" → "Create new file" → Name it: HOWTO.md → Paste:

# How to Install & Run Finance Manager

## 📥 Step-by-Step Installation

### 1. Install Python

**Download Python:**
- Go to: https://www.python.org/downloads/
- Click "Download Python 3.x.x"
- Run the installer

**⚠️ CRITICAL - During Installation:**
- ✅ Check the box: **"Add Python to PATH"**
- Click "Install Now"
- Wait for completion

**Verify Installation:**
Open Command Prompt (cmd) and type:
```cmd
python --version
Should show: Python 3.x.x

If it says "python not found":

Reinstall Python
Make sure "Add Python to PATH" is checked
Restart your computer
2. Download This Repository
Option A: Download ZIP

Click the green "Code" button at the top
Click "Download ZIP"
Extract to any folder (e.g., C:\FinanceManager\)
Option B: Clone with Git

git clone https://github.com/sriram1947/finance-manager-portable.git
cd finance-manager-portable
3. Run the Application
Easy Method (Windows):

Double-click START.bat
Wait 1-2 minutes (first time only)
Browser opens automatically!
Manual Method: Open Command Prompt in the folder and run:

pip install -r requirements.txt
python server_desktop.py
Then open browser to: http://localhost:8001

🔐 First Login
Default Account:

Email: admin@financeapp.com
Password: admin123
Or Create Your Own:

Click "Create Account"
Fill in your details
Start using!
❓ Troubleshooting
Problem: "Python is not installed"
Solution:

Install Python from python.org
Check "Add Python to PATH"
Restart computer
Try again
Problem: "pip is not recognized"
Solution:

python -m pip install -r requirements.txt
python server_desktop.py
Problem: "ModuleNotFoundError: No module named 'fastapi'"
Solution: Dependencies didn't install. Run:

pip install fastapi uvicorn aiosqlite pydantic email-validator pyjwt bcrypt
Problem: "Port 8001 is already in use"
Solution:

Close any apps using port 8001
Or restart your computer
Or kill the process:
netstat -ano | findstr :8001
taskkill /PID <number> /F
Problem: Browser doesn't open automatically
Solution:

Manually open your browser
Go to: http://localhost:8001
Problem: "This site can't be reached"
Solution:

Check the terminal window for errors
Make sure server is running (you'll see "Uvicorn running...")
Wait 10 seconds and refresh browser
Check Windows Firewall isn't blocking port 8001
Problem: "bcrypt installation fails"
Solution: Windows needs Visual C++ Build Tools:

Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
Install "Desktop development with C++"
Restart
Run: pip install bcrypt
💾 Your Data Location
All your financial data is stored locally:

C:\Users\YourName\AppData\Roaming\FinanceManager\finance.db
To Backup:

Close the app (Ctrl+C in terminal)
Copy the finance.db file
Store it safely (cloud, USB, etc.)
To Restore:

Close the app
Replace finance.db with your backup
Start the app again
🛑 How to Stop the App
Method 1: Close the terminal/command window

Method 2: Press Ctrl+C in the terminal

Method 3: Close your browser and then terminal

Your data is automatically saved!

✅ Post-Installation Checklist
 Python installed with "Add to PATH" checked
 Files extracted to a folder
 Run START.bat or python server_desktop.py
 Browser opens to http://localhost:8001
 Login successful
 Create your account
 Add first transaction
 Test all features
🎯 Features Guide
Track Transactions
Click "Add Transaction"
Select Income or Expense
Enter category, amount, date
Save
Manage Investments
Click "Add Investment"
Select institution type (Bank/Post Office/Insurance)
Enter details (amount, dates, maturity)
Save
Add Custom Institutions
When adding investment, click the "+" button
Or go to Settings (gear icon)
Add your bank/insurance company
It appears in dropdown
Generate Reports
Click "Generate Report" button
PDF downloads automatically
Includes all transactions and investments
🔄 Updating
To update to a new version:

Backup your database file (see above)
Download new version from GitHub
Extract and overwrite old files
Run normally - your data is safe!
💡 Tips
Keep terminal open while using the app
Backup weekly - copy your database file
Use consistent categories for better analytics
Record transactions daily for accuracy
Check dashboard regularly to track progress
🆘 Still Need Help?
Check error messages in terminal window
Read this guide again carefully
Ensure Python is properly installed
Try manual installation method
Check Windows Firewall settings
💰 Cost
FREE Forever!

No cloud costs
No subscriptions
No hidden fees
Works 100% offline
Enjoy tracking your finances! 🎉
