# ProtonPulse

**PTM Charge Distribution Analyzer** — Standalone desktop app for bench scientists

Calculate charge variant distributions for post-translationally modified proteins using adaptive algorithms. No coding required—just click and analyze!

![Version](https://img.shields.io/badge/version-2.3-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ⚡ TL;DR (Quick Start)

**For Windows bench scientists:**

1. **Download & extract** this repo (`Code` → `Download ZIP`)
2. **Run once:** Double-click `INSTALL/setup_env.ps1` (installs Python dependencies)
3. **Then every time:** Double-click the desktop shortcut created by `INSTALL/create_shortcut.ps1`
4. **App opens automatically** in your browser — start analyzing!

**Need details?** See `INSTALL/INSTALLATION_GUIDE.md`

---

## What is ProtonPulse?

ProtonPulse calculates the **overall charge state distribution** of proteins with multiple post-translational modifications (PTMs).

### Real-World Example

You have a protein with 5 phosphorylation sites:
- Site 1: Unmodified (charge 0)
- Site 2: Can be -1 or 0 (60% neutral, 40% -1)
- Site 3: Can be 0 or +1 (80% neutral, 20% +1)
- Sites 4-5: Similar variations...

**Question:** What's the probability the protein has total charge -3? Or +2? Or any other charge?

**ProtonPulse Answer:** Instant visualization showing all possible charge states and their probabilities.

### Why It Matters

This is critical for understanding:
- **Mass spectrometry** ionization patterns
- **Protein biophysics** (charge-dependent interactions)
- **PTM validation** (comparing expected vs. observed distributions)
- **Therapeutic design** (optimizing charge for efficacy)

---

## Key Features

✅ **For Bench Scientists:**
- No Python knowledge required
- Point-and-click interface
- Upload CSV, get instant visualizations
- Download results for reports

✅ **For Your Data:**
- Fully offline (after one-time internet setup)
- Your data never leaves your computer
- Import/export CSV for Excel workflows
- Built-in validation against benchmark datasets

✅ **For the Science:**
- Adaptive algorithms that scale from exact to approximate
- Validates against ground truth for accuracy
- Automatic algorithm selection based on data size
- References to peer-reviewed literature

---

## Installation & Setup

### System Requirements

| Requirement | Specification |
|---|---|
| **OS** | Windows 10 or 11 |
| **Storage** | ~500 MB (one-time) |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **Internet** | ✅ Required for setup **ONLY**<br>❌ NOT needed to run the app |

### What You Need to Download

**Full repository** — You must download/clone the **entire repo** to get:
- The Python application code
- Pre-trained dependencies
- Helper scripts and data templates
- Configuration files

You cannot use just individual files. The app depends on the project structure.

**Where to get it:**
- GitHub: `https://github.com/valle1306/ptm_app`
- Click `Code` → `Download ZIP`
- Or use Git: `git clone https://github.com/valle1306/ptm_app.git`

### Installation Steps (5 minutes, one-time)

**Step 1: Extract**
1. Download the ZIP file
2. Right-click → Extract All
3. Choose location (e.g., `C:\ProtonPulse`)

**Step 2: Install Python Dependencies** (requires internet)
1. Navigate into the extracted folder
2. Double-click: `INSTALL/setup_env.ps1`
3. PowerShell window opens showing installation progress
4. Wait until you see: "✅ Setup complete!"
5. Close the window

**Step 3: Create Desktop Shortcut** (optional but recommended)
1. Double-click: `INSTALL/create_shortcut.ps1`
2. A "ProtonPulse" shortcut appears on your desktop
3. Done!

### Running the App

**Option A: Desktop Shortcut** (easiest)
- Double-click the "ProtonPulse" shortcut on your desktop
- Browser opens automatically
- App is ready to use

**Option B: Manual Launch**
- Double-click `run_protonpulse.bat` in the main folder
- Browser opens automatically

For more details, see `INSTALL/INSTALLATION_GUIDE.md`

---

## Using the App

### In-App Instructions

Once you launch ProtonPulse, the app has **four main sections** (tabs):

1. **🏠 Welcome** — Introduction, algorithm overview, example use cases
2. **📝 Data Input** — Upload CSV or edit PTM sites
3. **📊 Compute & Visualize** — Calculate and view charge distribution
4. **✅ Validate** — Verify accuracy against benchmarks

**Start here:** Click the Welcome tab when the app opens for interactive instructions.

### Typical Workflow

```
1. Open app (click shortcut)
2. Go to "📝 Data Input" tab
3. Either:
   a) Upload your CSV file, OR
   b) Download template → edit in Excel → upload back, OR
   c) Edit example data directly in the app
4. Go to "📊 Compute & Visualize" tab
5. Click "🚀 Compute Distribution" button
6. See results! (graphs, statistics, download option)
```

### Data Format

Your CSV needs these columns:
```
Site_ID,Copies,P(-2),P(-1),P(0),P(+1),P(+2)
Site_1,1,0.0,0.0,1.0,0.0,0.0
Site_2,1,0.0,0.1,0.8,0.1,0.0
```

**Download a template from the app** — easier than creating from scratch.

---

## Offline Operation

✅ **Completely offline after setup:**
- All computation happens on your computer
- No cloud services, no API calls
- Visualizations generated locally
- No telemetry or usage tracking

**Data Privacy:**
- Files you upload are only in your browser's memory
- Cleared automatically when you close the app
- Downloaded results go to your Downloads folder
- Nothing is saved to our servers

---

## Troubleshooting

### "Setup script won't run"

**Solution:**
1. Right-click PowerShell from Start menu
2. Select "Run as administrator"
3. Navigate to folder: `cd C:\Path\To\ProtonPulse`
4. Run: `.\INSTALL\setup_env.ps1`

### "Python not found when running app"

**Solution:** You skipped Step 2 (Install Dependencies)
- Double-click `INSTALL/setup_env.ps1` and let it finish completely

### "App won't open / port error"

**Solution:**
1. Close the browser and terminal
2. Wait 5 seconds
3. Double-click the shortcut again
4. If you see "port 8501 in use", try a different port (see advanced section below)

### "CSV upload fails"

**Solution:**
- Download the template from inside the app
- Match the exact column names and format
- Save as `.csv` (not `.xlsx`)

### More help

See `INSTALL/INSTALLATION_GUIDE.md` for extended troubleshooting

---

## Advanced (For Developers)

### Manual Setup (Command Line)

```powershell
cd path\to\ProtonPulse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run ptm_charge_input_v2.py
```

### Custom Port

```powershell
.\.venv\Scripts\python.exe -m streamlit run ptm_charge_input_v2.py --server.port 9000
```

### Linux/Mac Installation

ProtonPulse is Windows-optimized, but can run on Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run ptm_charge_input_v2.py
```

---

## Algorithm Reference

ProtonPulse automatically selects the best algorithm based on your data:

| Algorithm | Time | When Used | Accuracy |
|---|---|---|---|
| **Enumeration** | O(5ⁿ) | ≤12 copies | Exact ✓ |
| **Yergey Convolution** | O(n²) | ≤50 copies | Exact ✓ |
| **FFT** | O(n log n) | 51–200 copies | Exact ✓ |
| **Gaussian** | O(n) | >200 copies | Approximate |

**Why different algorithms?**
- 10 copies = 9.7 million charge combinations
- 20 copies = 95 trillion combinations
- Convolution and FFT avoid brute-force enumeration

**Reference:**
Yergey, J. A. (1983). "A general approach to calculating isotopic distributions for mass spectrometry." *International Journal of Mass Spectrometry and Ion Physics*, 52(2), 337–349.

---

## Project Structure

```
ProtonPulse/
├── 📖 INSTALL/
│   ├── INSTALLATION_GUIDE.md      ← Detailed setup instructions
│   ├── setup_env.ps1              ← Run once (installs dependencies)
│   └── create_shortcut.ps1        ← Run once (makes desktop shortcut)
│
├── 🚀 run_protonpulse.bat         ← Launch app (double-click)
├── 🚀 run_protonpulse.ps1         ← Alternative launcher
│
├── 💻 ptm_charge_input_v2.py      ← Main Streamlit app
├── 🧮 advanced_algorithms.py      ← Computation backend
│
├── 📄 README.md                   ← This file (overview)
├── 📄 QUICKSTART.md               ← Detailed usage guide
├── requirements.txt               ← Python dependencies
├── LICENSE                        ← MIT License
│
├── 📊 Data/
│   ├── sample_ptm_n100.csv        ← Example dataset
│   └── test_csvs/                 ← Test files
│
├── 🧪 tests/
│   ├── test_validation.py
│   ├── benchmark_comparison.py
│   └── stress_test_copies.py
│
├── 📂 scripts/                    ← Helper utilities
├── 📂 docs/                       ← Technical documentation
└── 📂 .venv/                      ← Python environment (auto-created)
```

---

## Frequently Asked Questions

**Q: Do I need to know Python?**  
A: No! ProtonPulse is designed for lab scientists. Just click buttons and upload files.

**Q: Can I use this on Mac/Linux?**  
A: Yes, but instructions are optimized for Windows. Follow the "Advanced" section above.

**Q: Can I modify the code?**  
A: Yes! MIT License allows modification. See QUICKSTART.md for insights into the codebase.

**Q: How do I report bugs?**  
A: Submit issues on GitHub or contact the development team.

**Q: Can I share my results?**  
A: Yes! Download results as CSV and share freely. Your data is never saved server-side.

---

## Credits

Developed by:
- **Valerie Le**
- **Alex Goferman**

MSDS Program, Rutgers University

**Version:** 2.3 (December 2025)

**License:** MIT License — Free to use, modify, and distribute.

---

## Next Steps

1. **Extract the repo** (download ZIP and extract)
2. **Follow installation** (see above or `INSTALL/INSTALLATION_GUIDE.md`)
3. **Launch the app** (click desktop shortcut or `run_protonpulse.bat`)
4. **Read Welcome tab** (in-app tutorial with examples)
5. **Start analyzing!** (upload CSV or use template)
