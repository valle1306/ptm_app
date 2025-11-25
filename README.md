# PTM Charge Variant Input Application

A comprehensive, user-friendly computational tool for analyzing post-translational modification (PTM) charge distributions in proteins. Features interactive visualizations, multiple charge systems, and advanced data management capabilities for rapid, in-silico assessment of protein charge heterogeneity.

## ✨ Key Features

### 📊 **Interactive Data Visualization**
- **Real-time Interactive Plots**: Plotly-powered visualizations with hover details, zoom, and pan
- **Multiple Plot Types**: Combined view, distribution-only, cumulative probability, and site contributions heatmap
- **Smart Recommendations**: App suggests optimal visualization based on dataset size and characteristics
- **Customizable Display**: Adjustable plot heights, tail annotations, and export options
- **Publication Ready**: High-quality plots suitable for presentations and publications

### 📝 **Flexible Data Input**
- **Interactive Table Editor**: Real-time validation with visual status indicators
- **CSV Upload**: Auto-detection of charge systems from uploaded files with preview
- **Smart Templates**: Generate datasets for common PTM scenarios (neutral, acidic, basic, mixed populations)
- **Bulk Generation**: N=100+ site templates with varied probability patterns
- **Multiple Charge Systems**: Support for 3-state to 15-state charge ranges (-7 to +7)

### ⚙️ **Advanced Charge Systems**
- **Flexible Charge Ranges**: 3-state (-1 to +1) through 15-state (-7 to +7) systems
- **Auto-Detection**: Automatically detect charge system from existing data
- **System Switching**: Seamlessly switch between charge systems with example data
- **Dynamic Columns**: Column headers adapt automatically to selected charge range

### 🧮 **Robust Mathematical Engine**
- **Convolution-Based Calculation**: Mathematically rigorous probability distribution computation
- **Multiple Copies Support**: Handle sites with multiple copies per protein
- **Large Dataset Optimization**: Efficient algorithms for 100+ PTM sites
- **Numerical Stability**: Robust handling of floating-point precision and normalization

### 📥 **Comprehensive Export Options**
- **Interactive Plot Export**: Save plots as standalone HTML files with full interactivity
- **Multi-Format Data Export**: CSV, Excel with multiple sheets, and text summaries
- **Complete Reports**: Analysis summaries with input data, results, and metadata
- **Publication Formats**: Ready-to-use figures and data tables for scientific publications

## 🚀 Quick Start

### Installation & Setup
```bash
# Clone or download the repository
cd ptm_app

# Install dependencies
pip install streamlit pandas numpy plotly openpyxl

# Run the application
streamlit run ptm_charge_input.py
```

### Basic Workflow
1. **Choose Charge System**: Select appropriate charge range (3-state to 15-state) in sidebar
2. **Input PTM Data**: Use templates, manual entry, or CSV upload
3. **Validate Data**: Ensure all probability rows sum to 1.0 (visual indicators provided)
4. **Compute Distribution**: Click "Compute distribution now" 
5. **Analyze Results**: Explore interactive plots and download results

### 📁 Data Input Options

#### **Quick Templates**
- **N=100 Template**: Generate large dataset with varied probability patterns
- **Custom Templates**: Create datasets for specific scenarios (neutral, acidic, basic, mixed)
- **Charge System Templates**: Automatically adapt to your selected charge range

#### **CSV Upload**
```csv
Site_ID,Copies,P(-2),P(-1),P(0),P(+1),P(+2)
Ser123,1,0.0,0.2,0.6,0.2,0.0
Thr45,1,0.1,0.3,0.6,0.0,0.0
```
- Auto-detection of charge systems from file headers
- Real-time preview before loading
- Validation and error reporting for malformed data

#### **Manual Entry**
- Interactive data editor with real-time validation
- Add/remove rows dynamically
- Visual status indicators (✅/❌) for each row
- Helpful error messages and fixing suggestions

### 📊 Visualization Features

#### **Plot Types**
- **Combined View**: Distribution + cumulative plots in one view (recommended)
- **Distribution Only**: Bar chart showing probability for each charge state
- **Cumulative Only**: Line chart showing cumulative probability distribution  
- **Site Contributions**: Heatmap showing individual PTM site patterns

#### **Customization Options**
- **Plot Heights**: Compact, Standard, or Large sizing
- **Tail Annotations**: Toggle display of probability mass outside [-5,+5] window
- **Smart Recommendations**: App suggests best plot type for your dataset size

#### **Export Options**
- **Interactive HTML**: Save plots with full interactivity (zoom, hover, pan)
- **Publication Ready**: High-quality figures for presentations and papers
- **Multiple Formats**: CSV, Excel, text summaries with metadata

### 📈 Sample Data & Examples
- `sample_ptm_n100.csv`: 100 PTM sites with varied probability patterns
- Built-in templates for common PTM scenarios
- Example charge systems from 3-state to 15-state ranges

## 🔬 Scientific Applications

### **Use Cases**
- **Protein Charge Prediction**: Model how PTMs affect overall protein charge distribution
- **Isoelectric Point Analysis**: Understand charge variants around theoretical pI
- **PTM Stoichiometry Studies**: Analyze effects of partial modification at multiple sites
- **Biotherapeutic Development**: Assess charge heterogeneity in protein drugs
- **Mass Spectrometry Planning**: Predict charge states for MS method optimization

### **Supported PTM Types**
- **Phosphorylation**: Typically negative charges (-1 to -2)
- **Acetylation**: Neutral to positive charges (0 to +1) 
- **Methylation**: Usually neutral or slightly positive
- **Ubiquitination**: Large positive charge addition
- **Custom PTMs**: Any charge state combination with user-defined probabilities

### **Mathematical Foundation**
- **Convolution Mathematics**: Rigorous probability theory for combining independent sites
- **Fast Algorithms**: Exponentiation by squaring for sites with multiple copies
- **Numerical Stability**: Robust normalization and precision handling
- **Scalability**: Efficient computation for 100+ PTM sites

## 📁 File Structure
```
ptm_app/
├── ptm_charge_input.py      # Main Streamlit application with interactive features
├── sample_ptm_n100.csv      # Sample data (N=100 PTM sites)
├── README.md                # This documentation
└── .venv/                   # Virtual environment (created after setup)
```

## 🛠️ Technical Requirements

### **Dependencies**
```bash
pip install streamlit>=1.28.0 pandas>=2.0.0 numpy>=1.24.0 plotly>=5.15.0 openpyxl>=3.1.0
```

### **System Requirements**
- **Python**: 3.8+ (recommended: 3.11+)
 # PTM Charge Distribution Analyzer — Quick README

This repository runs a Streamlit app that computes overall protein net-charge distributions
from per-site PTM charge-state probabilities. Most usage tips are shown inside the app's
landing page; this README gives a short, focused run & quick-start guide.

## Quick start (Windows PowerShell)

1) Activate the virtual environment (if you created one in this repo):

```powershell
& .\\.venv\\Scripts\\Activate.ps1
```

2) Install dependencies (if not already installed):

```powershell
python -m pip install -r requirements.txt
```

3) Run the Streamlit app (recommended — uses the venv Python):

```powershell
python -m streamlit run ptm_charge_input_v2.py
```

If you see a launcher error like "Fatal error in launcher: Unable to create process", use the
exact command above (`python -m streamlit ...`) instead of `streamlit run ...`. Reinstalling
Streamlit inside the venv can also fix the Windows wrapper:

```powershell
python -m pip install --upgrade --force-reinstall streamlit
```

Open the displayed Local URL (e.g., http://localhost:8501) in your browser.

## What to do in the app (short)

- Landing page: short guide and tips.
- Design Input tab:
	- Select a charge range (3-state … 15-state).
	- Use "📋 Generate N=100" to create a test template.
	- Edit site rows in the table. Probability columns (P(...)) are highlighted.
	- Each row shows a "Prob_Sum" and "Status" (✅ means the row sums to 1.0).
- Compute & Visualize tab:
	- Click ▶️ Compute Distribution Now to run the PGF/convolution engine.
	- View combined Distribution + Cumulative plots, metrics, and a table of the central window.

Notes:
- If a row's probabilities don't sum to 1.0, the app will auto-normalize on compute (you'll be warned).
- Default editor height is compact (300px) to reduce scrolling; you can still add/remove rows.

## Quick troubleshooting

- Streamlit launcher errors — use `python -m streamlit run ...` (see above).
- Missing/incorrect probability columns — ensure column names like `P(-1)`, `P(0)`, `P(+1)` match the active range.
- Very large datasets may take longer; the app is optimized for >100 sites but expect increased compute time.

## Files you may care about

- `ptm_charge_input_v2.py` — main Streamlit app (current development version).
- `ptm_charge_input.py` — earlier/reference version.
- `requirements.txt` — Python dependencies.
- `Data/sample_ptm_n100.csv` — example dataset (100 sites).

## Credits

Developed by Valerie Le & Alex Goferman — MSDS Program, Rutgers University.

---

If you want, I can (a) trim or expand sections, (b) add copy for a public GitHub README, or
(c) add an example command to run on a specific port. Tell me which and I'll update the README.
