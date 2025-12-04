
# ProtonPulse

PTM Charge Distribution Analyzer — Compute charge variant distributions for post-translationally modified proteins using adaptive algorithms.

![Version](https://img.shields.io/badge/version-2.3-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## Overview

ProtonPulse calculates charge distributions for proteins with multiple post-translational modification (PTM) sites. Each site may have different copy numbers and charge state probabilities (from -2 to +2).

### Key Features
- Adaptive algorithm selection based on data size
- Interactive visualizations powered by Plotly
- CSV import/export for easy data management
- Built-in validation against ground truth
- Fully offline operation after installation

---

## Quick Start

### Option 1: Windows Launchers (Recommended)

**First-time setup:**
1. Right-click `setup_env.ps1` and select "Run with PowerShell"
2. Wait for dependencies to install

**Run the app:**
- Double-click `run_protonpulse.bat`, or
- Right-click `run_protonpulse.ps1` and select "Run with PowerShell"

The app will open at [http://localhost:8501](http://localhost:8501)

---

### Option 2: Command Line

```powershell
cd path\to\ptm_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run ptm_charge_input_v2.py
```

---

## Installation Requirements

- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- pip (included with Python)

### Dependencies (auto-installed via requirements.txt)
- streamlit
- pandas
- numpy
- plotly
- scipy

---

## Algorithm Reference

ProtonPulse uses adaptive algorithm selection based on data complexity:

| Method                | Complexity | When Used      | Accuracy                |
|-----------------------|------------|---------------|-------------------------|
| Enumeration           | O(5ⁿ)      | ≤12 copies     | Exact (ground truth)    |
| Yergey Convolution    | O(n²)      | ≤50 copies     | Exact                   |
| FFT-Accelerated       | O(n log n) | 51–200 copies  | Exact                   |
| Gaussian Approximation| O(n)       | >200 copies    | Approximate             |

#### Scientific Basis

Based on Yergey’s convolution method:

Yergey, J. A. (1983). A general approach to calculating isotopic distributions for mass spectrometry. *International Journal of Mass Spectrometry and Ion Physics*, 52(2), 337–349. [DOI](https://doi.org/10.1016/0020-7381(83)85053-0)

---

## Project Structure

```
ptm_app/
├── ptm_charge_input_v2.py         # Main Streamlit application
├── advanced_algorithms.py         # FFT & Gaussian algorithm implementations
├── requirements.txt               # Python dependencies
├── setup_env.ps1                  # Windows setup script
├── run_protonpulse.bat            # Windows batch launcher
├── run_protonpulse.ps1            # PowerShell launcher
├── README.md                      # Project documentation
│
├── Data/
│   ├── sample_ptm_n100.csv        # Example dataset (100 sites)
│   └── test_csvs/                 # Test files for validation
│
├── scripts/
│   ├── generate_test_csvs.py      # Generate test data
│   ├── generate_ptm_csv.py        # CSV generation utilities
│   └── ptm_helpers.py             # Helper functions
│
├── tests/
│   ├── test_validation.py         # Algorithm validation tests
│   ├── benchmark_comparison.py    # Performance benchmarks
│   └── stress_test_copies.py      # Stress testing
│
└── docs/
    ├── ALGORITHM_DEVELOPMENT_SUMMARY.md
    ├── PTM_UPDATE_SUMMARY.md
    └── VALIDATION_FINDINGS.md
```

---

## Standalone / Offline Usage

ProtonPulse runs completely offline after installation:
- All computations are performed locally
- Visualizations are client-side
- No external API calls
- No telemetry

### Troubleshooting

**Scripts close immediately?**
- Ensure you ran `setup_env.ps1` first
- Verify Python is installed and added to PATH

**PowerShell execution policy error?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port already in use?**
```powershell
.\.venv\Scripts\python.exe -m streamlit run ptm_charge_input_v2.py --server.port 8502
```

---

## Credits

Developed by:
- Valerie Le
- Alex Goferman
MSDS Program, Rutgers University

Version: 2.3 (December 2025)

---

## License

MIT License — Free to use, modify, and distribute.
