# ProtonPulse Installation Guide

**For: Bench Scientists & Lab Researchers**

---

## What is ProtonPulse?

ProtonPulse is a PTM Charge Distribution Analyzer that calculates charge variant distributions for post-translationally modified proteins. No coding required—just point, click, and analyze!

**Version:** 2.3 | December 2025

---

## System Requirements

| Requirement | Specification |
|---|---|
| **Operating System** | Windows 10/11, macOS, or Linux |
| **Disk Space** | ~500 MB (one-time setup) |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **Internet** | Required for first-time setup only |

---

## Installation (5 minutes, one-time)

### Step 1: Extract Files
1. Download `ProtonPulse_Setup.zip`
2. Right-click → Extract All
3. Choose a location (e.g., `C:\ProtonPulse` or `C:\Users\YourName\Documents\ProtonPulse`)
4. Open the extracted `ProtonPulse` folder

### Step 2: Install Dependencies
This runs on its own. Just watch the terminal.

**Option A - Automatic (Easiest):**
1. In the `ProtonPulse` folder, right-click `setup_env.ps1` and select "Run with PowerShell" (Windows). On Mac/Linux, open a terminal and run the script as described in the Advanced section.
2. A terminal will open and start installing
3. Wait until you see:
   ```
   Setup complete! Press Enter to close.
   ```
4. Press Enter
5. Done! You only do this once.

**Option B - Manual (If Option A doesn't work):**
1. Right-click the `ProtonPulse` folder
2. Select Open PowerShell window here as administrator
3. Copy and paste this command:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup_env.ps1
   ```
4. Press Enter and wait for completion

---

## Using ProtonPulse

### First Time: Create Desktop Shortcut

In the `ProtonPulse` folder, right-click `create_shortcut.ps1` and select "Run with PowerShell" (Windows). On Mac/Linux, use the terminal as described in the Advanced section.

This creates a "ProtonPulse" icon on your desktop (Windows only).

### Every Other Time: Just Click!

1. Double-click the "ProtonPulse" desktop shortcut
2. A terminal opens and shows status
3. Browser automatically opens to the app
4. Start analyzing!

---

## How to Use the App

### Main Workflow

1. Welcome Tab
   - Learn what the app does
   - Understand the algorithms
2. Data Input Tab
   - Upload a CSV file, OR
   - Edit example data manually
   - Download template to edit in Excel
3. Compute Tab
   - Click "Compute Distribution" button
   - See instant results with graphs
   - Download results as CSV
4. Validate Tab
   - Compare different calculation methods
   - Verify accuracy

### Quick Example

```
1. Click Data Input tab
2. Click Download Template
3. Open downloaded file in Excel
4. Add your PTM sites and probabilities
5. Upload the CSV back into the app
6. Click Compute Distribution
7. See results!
```

---

## Folder Structure

```
ProtonPulse/
├── INSTALL/
│   ├── INSTALLATION_GUIDE.md (this file)
│   ├── setup_env.ps1 (run once)
│   ├── create_shortcut.ps1 (run once)
│   └── requirements.txt (Python dependencies)
│
├── QUICKSTART.md (read this)
├── README.md (technical details)
│
├── run_protonpulse.bat (launcher - don't edit)
├── run_protonpulse.ps1 (launcher - don't edit)
│
├── ptm_charge_input_v2.py (main app - don't edit)
├── advanced_algorithms.py (backend - don't edit)
│
├── Data/
│   ├── sample_ptm_n100.csv (example data)
│   └── test_csvs/ (test files)
│
├── scripts/
│   └── (helper scripts)
│
└── .venv/
    └── (installed Python packages - don't touch)
```

---

## Troubleshooting

### Problem: "PowerShell cannot be opened"

**Solution:**
1. Right-click Windows PowerShell on Start menu
2. Select Run as administrator
3. Navigate to ProtonPulse folder:
   ```powershell
   cd C:\Path\To\ProtonPulse
   ```
4. Run setup:
   ```powershell
   .\setup_env.ps1
   ```

---

### Problem: "Python not found" when running app

**Solution:**
- You skipped Step 2 (Install Dependencies)
- Double-click `setup_env.ps1` and let it finish
- Then try the shortcut again

---

### Problem: App opens but shows "Connection refused"

**Solution:**
1. Close the browser and the terminal
2. Wait 5 seconds
3. Double-click the ProtonPulse shortcut again
4. Wait for the terminal to say "You can now view..."

---

### Problem: CSV upload fails

**Solution:**
- Make sure your CSV has these columns (exactly):
  - `Site_ID` - name of your PTM site
  - `Copies` - how many times this site appears
  - `P(-2)`, `P(-1)`, `P(0)`, `P(+1)`, `P(+2)` - probabilities
- Download the template from the app to see the correct format
- Save as `.csv` (not `.xlsx` or `.xls`)

---

### Problem: "Port 8501 is already in use"

**Solution:**
1. Close any other ProtonPulse windows or terminals
2. Open Task Manager (Ctrl+Shift+Esc)
3. Find "python.exe" in the list
4. Right-click → End Task
5. Try launching again

---

## Where Does My Data Go?

- Uploaded CSVs: Only stored in your browser (cleared when you close)
- Downloaded results: Go to your Downloads folder
- Local computer: Your computer stores nothing permanently
- Cloud: Your files are NOT uploaded anywhere

Your data is always private and under your control.

---

## Updating ProtonPulse

If a new version is released:

1. Download the new `ProtonPulse_Setup.zip`
2. Extract to a different folder (e.g., `ProtonPulse_v2.4`)
3. Run `setup_env.ps1` in the new folder
4. Update your desktop shortcut to point to the new folder

---

## Advanced Usage (For Power Users)

### Run from Terminal

If you prefer the command line:

```powershell
cd C:\Path\To\ProtonPulse
.\run_protonpulse.bat
```

Or with PowerShell:

```powershell
cd C:\Path\To\ProtonPulse
.\run_protonpulse.ps1
```

### Command-Line Flags

If you want to customize the app:

```powershell
.venv\Scripts\python.exe -m streamlit run ptm_charge_input_v2.py `
    --server.port 9000 `
    --server.headless false
```

(Changes the port from 8501 to 9000)

### Manual Setup (Command Line)

```powershell
cd path\to\ProtonPulse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r INSTALL/requirements.txt
streamlit run ptm_charge_input_v2.py
```

### Linux/Mac Installation

ProtonPulse is Windows-optimized, but can run on Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r INSTALL/requirements.txt
streamlit run ptm_charge_input_v2.py
```

---

## Support & Feedback

 - Issues? Check [QUICKSTART.md](../QUICKSTART.md) in the main folder
 - Questions? See [README.md](../README.md) for technical details
 - Bug reports? Contact the development team
 - Feature requests? Submit via GitHub issues

See [LICENSE](../LICENSE) file for details.

## License

Questions? Refer to [README.md](../README.md) or contact support.
See [LICENSE](../LICENSE) file for details.

---

## Citation

If you use ProtonPulse in research, please cite:

```
ProtonPulse v2.3 (2025)
PTM Charge Distribution Analyzer
Developed at: Rutgers University MSDS Program
Authors: Valerie Le & Alex Goferman
```

---

## For IT Administrators

### Network Installation

To deploy ProtonPulse across your organization:

1. Extract to a shared network drive
2. Run `setup_env.ps1` once (creates `.venv` folder)
3. Create shortcuts pointing to `run_protonpulse.bat`
4. Users can then launch without installing anything

### Silent Installation

```batch
powershell -ExecutionPolicy Bypass -File setup_env.ps1 -Silent
```

---

**Last Updated:** December 3, 2025

Questions? Refer to [README.md](../README.md) or contact support.
