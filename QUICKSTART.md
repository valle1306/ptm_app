# ProtonPulse - One-Click Launcher

This folder contains **ProtonPulse v2.3** - a PTM Charge Distribution Analyzer.

## ⚡ How to Launch (Pick ONE method)

### **Method 1: Double-Click (EASIEST) 👈**
Right-click on your Windows Desktop and select:
```
Create shortcut → Link to file location:
C:\Users\<YourUsername>\OneDrive\Documents\ptm_app\run_protonpulse.bat
```

Then **double-click the shortcut** from your desktop to launch the app.

**OR** - Save this as `ProtonPulse Shortcut.lnk` and put it on your desktop:

```vb
[InternetShortcut]
URL=file:///C:/Users/<YourUsername>/OneDrive/Documents/ptm_app/run_protonpulse.bat
```

---

### **Method 2: Batch File**
Double-click: `run_protonpulse.bat`

The batch file will:
- ✅ Launch Streamlit automatically
- ✅ Open your browser to http://localhost:8501
- ✅ Show status messages
- ✅ Clean shutdown when you close it

---

### **Method 3: PowerShell**
Right-click `run_protonpulse.ps1` → "Run with PowerShell"

---

## ✨ What Happens When You Launch

1. Terminal window appears showing status
2. Browser automatically opens to the app
3. **ProtonPulse** loads with sample data ready to analyze
4. Press `Ctrl+C` in the terminal to stop

---

## 📊 Using ProtonPulse

1. **Welcome Tab** - Learn about the app
2. **Data Input Tab** - Upload CSV or edit PTM sites
3. **Compute Tab** - Calculate charge distribution (shows results as graphs)
4. **Validate Tab** - Verify accuracy against benchmarks

### Example Workflow:
```
1. Go to "Data Input" tab
2. Click "📋 Download Template" 
3. Edit in Excel (add your PTM sites)
4. Upload the CSV back
5. Click "📊 Compute Distribution"
6. See results!
```

---

## 💾 System Requirements

- **Windows 10/11**
- **~400 MB disk space** (one-time)
- **Internet** (only needed for first-time Python setup)

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Run `setup_env.ps1` first to install dependencies |
| App doesn't open | Click the batch file again or wait 10 seconds |
| Port 8501 in use | Close other Streamlit instances first |
| CSV won't upload | Make sure columns are: `Site_ID`, `Copies`, `P(-2)`, etc. |

---

## 📝 For Bench Scientists

If you're not comfortable with terminals:
- **Just use Method 1** (Desktop Shortcut)
- Double-click the shortcut
- App opens automatically
- That's it!

---

## ✉️ Support

Questions? Check the README.md in this folder or contact the development team.

**ProtonPulse v2.3** | December 2025 | Rutgers University MSDS Program
