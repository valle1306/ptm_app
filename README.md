# 🔬 ProtonPulse

**PTM Charge Distribution Analyzer** — Compute charge variant distributions for post-translationally modified proteins using adaptive algorithms.

![Version](https://img.shields.io/badge/version-2.3-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📖 Overview

ProtonPulse calculates overall charge distributions for proteins with multiple post-translational modification (PTM) sites. Each site can have different copy numbers and charge state probabilities (-2 to +2).

**Key Features:**
- 🧮 **Adaptive Algorithms** — Automatically selects the best method based on data size
- 📊 **Interactive Visualizations** — Plotly-powered charts with interpretation
- 📁 **CSV Import/Export** — Edit data in Excel, import seamlessly
- ✅ **Built-in Validation** — Compare algorithms against ground truth
- 💻 **Runs Offline** — No internet required after installation

---

## 🚀 Quick Start

### Option 1: Windows Launchers (Recommended)

**First-time setup:**
1. Right-click `setup_env.ps1` → **Run with PowerShell**
2. Wait for dependencies to install

**Run the app:**
- Double-click `run_protonpulse.bat`  
- OR right-click `run_protonpulse.ps1` → **Run with PowerShell**

The app opens at **http://localhost:8501**

---

### Option 2: Command Line

```powershell
# Navigate to project folder
cd path\to\ptm_app

# Create virtual environment (first time only)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the app
streamlit run ptm_charge_input_v2.py
```

---

## 📦 Installation Requirements

- **Python 3.8+** (download from [python.org](https://www.python.org/downloads/))
- **pip** (included with Python)

### Dependencies (auto-installed via requirements.txt)
- streamlit
- pandas
- numpy
- plotly
- scipy

---

## 🔬 Algorithm Reference

ProtonPulse uses **adaptive algorithm selection** based on data complexity:

| Method | Complexity | When Used | Accuracy |
|--------|-----------|-----------|----------|
| **Enumeration** | O(5ⁿ) | ≤12 copies | Exact (ground truth) |
| **Yergey Convolution** | O(n²) | ≤50 copies | Exact |
| **FFT-Accelerated** | O(n log n) | 51-200 copies | Exact |
| **Gaussian Approximation** | O(n) | >200 copies | Approximate |

### Scientific Basis

Based on Yergey's convolution method (1983):

> Yergey, J. A. (1983). A general approach to calculating isotopic distributions for mass spectrometry. *International Journal of Mass Spectrometry and Ion Physics*, 52(2), 337–349.  
> https://doi.org/10.1016/0020-7381(83)85053-0

---

## 📁 Project Structure

```
ptm_app/
├── ptm_charge_input_v2.py     # Main Streamlit application
├── advanced_algorithms.py      # FFT & Gaussian algorithm implementations
├── requirements.txt            # Python dependencies
├── setup_env.ps1               # Windows setup script
├── run_protonpulse.bat         # Windows batch launcher
├── run_protonpulse.ps1         # PowerShell launcher
├── README.md                   # This file
│
├── Data/
│   ├── sample_ptm_n100.csv    # Example dataset (100 sites)
│   └── test_csvs/             # Test files for validation
│
├── scripts/
│   ├── generate_test_csvs.py  # Generate test data
│   ├── generate_ptm_csv.py    # CSV generation utilities
│   └── ptm_helpers.py         # Helper functions
│
├── tests/
│   ├── test_validation.py     # Algorithm validation tests
│   ├── benchmark_comparison.py # Performance benchmarks
│   └── stress_test_copies.py  # Stress testing
│
└── docs/
    ├── ALGORITHM_DEVELOPMENT_SUMMARY.md
    ├── PTM_UPDATE_SUMMARY.md
    └── VALIDATION_FINDINGS.md
```

---

## 🖥️ Standalone / Offline Usage

ProtonPulse runs **completely offline** once installed:

- ✅ All computations run locally (numpy, scipy)
- ✅ Visualizations are client-side (Plotly)
- ✅ No external API calls
- ✅ No telemetry (disabled by default)

### Troubleshooting

**Scripts close immediately?**
- Make sure you ran `setup_env.ps1` first
- Check that Python is installed and on PATH

**PowerShell execution policy error?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port already in use?**
```powershell
.\.venv\Scripts\python.exe -m streamlit run ptm_charge_input_v2.py --server.port 8502
```

---

## 👥 Credits

**Developed by:**  
Valerie Le & Alex Goferman  
MSDS Program, Rutgers University

**Version:** 2.3 | December 2025

---

## 📄 License

MIT License — Free to use, modify, and distribute.
