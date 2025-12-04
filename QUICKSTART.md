# ProtonPulse - Detailed Usage Guide

**For users who want to understand the app in depth**

> **First time?** Read [README.md](README.md) first for setup and overview.

---

## Table of Contents

1. [Complete Workflow with Examples](#complete-workflow)
2. [Data Format & Templates](#data-format)
3. [In-App Features](#in-app-features)
4. [Results Interpretation](#results)
5. [Advanced Tips](#advanced)
6. [For Developers](#developers)

---

## Complete Workflow

### Start to Finish: A Real Example

Let's say you're analyzing a protein with 3 phosphorylation sites and want to understand its charge distribution.

#### Phase 1: Prepare Data

**Option A: Use a CSV file you already have**
- Make sure it has columns: `Site_ID`, `Copies`, `P(-2)`, `P(-1)`, `P(0)`, `P(+1)`, `P(+2)`
- Save as `.csv` (not `.xlsx`)

**Option B: Create from template**
1. Open ProtonPulse (double-click shortcut)
2. Go to **Data Input** tab
3. Click Download Template
4. Open in Excel
5. Fill in your data:
   ```
   Site_ID,Copies,P(-2),P(-1),P(0),P(+1),P(+2)
   Phos_Site1,1,0.0,0.0,1.0,0.0,0.0
   Phos_Site2,1,0.0,0.3,0.6,0.1,0.0
   Phos_Site3,1,0.0,0.0,0.8,0.2,0.0
   ```
6. Save as `.csv`
7. Go back to ProtonPulse and upload

**Option C: Edit example data directly in the app**
1. The app comes with example data pre-loaded
2. Click the data table in Data Input to edit directly
3. Click cells to change probability values

#### Phase 2: Generate Results

1. Go to **Compute & Visualize** tab
2. Select your preferred charge range (default: -5 to +5)
3. Click Compute Distribution
4. Instant results:
   - Bar chart of charge distribution
   - Cumulative line plot
   - Summary statistics

#### Phase 3: Download & Analyze

1. Scroll down to see detailed results
2. Click Download CSV to save results
3. Use downloaded file in Excel, papers, presentations

#### Phase 4: Validate (Optional)

1. Go to **Validate** tab
2. Choose a validation method
3. Compare your results against benchmarks
4. Verify accuracy

---

## Data Format

### Required Columns

Your CSV **must** have these exact columns (case-sensitive):

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Site_ID` | Text | Name of PTM site | "Phospho_S123" |
| `Copies` | Number | How many times this site appears | 1, 2, 3... |
| `P(-2)` | Decimal | Probability of -2 charge | 0.0 - 1.0 |
| `P(-1)` | Decimal | Probability of -1 charge | 0.0 - 1.0 |
| `P(0)` | Decimal | Probability of 0 charge (neutral) | 0.0 - 1.0 |
| `P(+1)` | Decimal | Probability of +1 charge | 0.0 - 1.0 |
| `P(+2)` | Decimal | Probability of +2 charge | 0.0 - 1.0 |

### Data Rules

**Probabilities must sum to 1.0 for each site:**
```
✅ CORRECT:   0.0 + 0.2 + 0.6 + 0.2 + 0.0 = 1.0
❌ WRONG:     0.0 + 0.2 + 0.6 + 0.1 + 0.0 = 0.9
```

**Copies must be positive integers:**
```
✅ CORRECT:   Copies = 1, 2, 3, 100
❌ WRONG:     Copies = 0, 1.5, -1
```

### Example CSV

```
Site_ID,Copies,P(-2),P(-1),P(0),P(+1),P(+2)
Site_1,1,0.0,0.0,1.0,0.0,0.0
Site_2,1,0.0,0.1,0.8,0.1,0.0
Site_3,2,0.0,0.0,1.0,0.0,0.0
Acetyl_K,1,0.0,0.0,0.7,0.3,0.0
```

**Meaning:** 
- Site_1: Always neutral (100% P(0))
- Site_2: Mostly neutral (80%), slight variations
- Site_3: Appears twice, always neutral
- Acetyl_K: Can be neutral or +1

### Charge Range Options

The app supports different charge ranges. Download the correct template for your needs:

| Range | States | Template | When to Use |
|-------|--------|----------|-------------|
| -1 to +1 | 3 | Minimal (basic PTMs) |
| -2 to +2 | 5 | Default (most common) |
| -3 to +3 | 7 | Large proteins |
| -5 to +5 | 11 | Complex PTM scenarios |
| Custom | Any | User-defined | Extreme cases |

---

## In-App Features

### Tab 1: Welcome

**What it contains:**
- Overview of what ProtonPulse does
- Algorithm explanations
- Example use cases
- Links to this guide

**When to use:** First time opening the app

### Tab 2: Data Input

**What it contains:**
- CSV file uploader
- Template downloader
- Data editor (click cells to edit)
- Charge range selector

**Key actions:**
1. **Upload CSV** → Click "Upload CSV" and choose your file
2. **Download Template** → Click Download Template for blank CSV
3. **Edit Directly** → Click data cells to change values
4. **Change Range** → Select different -N to +N range if needed

**Tips:**
- Template format is easiest if you have data in Excel
- Charge range locks once you upload CSV (prevents accidental reset)
- "Reset to Example" button restores demo data

### Tab 3: Compute & Visualize

**What it contains:**
- Charge range selector
- Compute button
- Results visualization
- Download button

**The results show:**
1. **Bar Chart** - Probability at each charge state
2. **Cumulative Chart** - Cumulative probability
3. **Summary Statistics:**
   - Most likely charge (mode)
   - Peak probability
   - Mean charge
   - Standard deviation
   - Tail probabilities

**Colors in charts:**
- Red: Very negative (< -2)
- Orange: Negative (-2 to -1)
- Green: Neutral (0)
- Blue: Positive (+1 to +2)
- Purple: Very positive (> +2)

### Tab 4: Validate

**What it contains:**
- Validation method selector
- Benchmark datasets
- Accuracy metrics
- Comparison visualizations

**Use this to:**
- Verify your algorithm works correctly
- Compare different charge ranges
- Test edge cases
- Build confidence in results

---

## Understanding Results

### What Does the Output Mean?

#### Bar Chart
- **X-axis:** Total charge of protein
- **Y-axis:** Probability (0% to 100%)
- **Bars:** Show likelihood of each charge

**Example interpretation:**
```
Charge +2 has height 0.35 → 35% chance protein has charge +2
Charge -1 has height 0.12 → 12% chance protein has charge -1
```

#### Statistics

**Most Likely Charge (Mode)**
- The charge state with highest probability
- If result shows "+1", the protein is most likely positively charged

**Peak Probability**
- The highest bar in the chart
- Higher = more certain that charge occurs
- Lower = charge distribution is spread out

**Mean Charge**
- Average charge across all possibilities
- Positive = net positive charge
- Negative = net negative charge

#### Cumulative Distribution
- Shows percentage of probability "up to" each charge
- Useful for understanding range (e.g., "80% chance charge is -3 to +3")

---

## Advanced Tips

### Tip 1: Large vs. Small Datasets

The app automatically picks the best algorithm:

| Copies | Method | Accuracy |
|--------|--------|----------|
| ≤50 | Yergeev Convolution | Exact |
| 51-200 | FFT-Accelerated | Exact |
| >200 | Gaussian (CLT) | Approximate |

**Small data (≤50 copies):** Uses exact Yergeev convolution
- Results are mathematically guaranteed correct
- Fast computation

**Medium data (51-200 copies):** Uses FFT-accelerated convolution
- Still exact results
- Faster for larger datasets

**Large data (>200 copies):** Uses Gaussian approximation
- Trades some precision for speed
- Still very accurate for most purposes (Central Limit Theorem)

**Check which was used:** Look at the "Algorithm Used" line in results

### Tip 2: Multiple Sites with Different Copy Numbers

You can specify different copy numbers for different modifications:

```
Phos_Site1,1,...    ← Appears 1 time
Acetyl_K,2,...      ← Appears 2 times
Ubiquitin,5,...     ← Appears 5 times
```

The tool multiplies probabilities correctly for each copy number.

### Tip 3: Probability Distribution Shapes

**Uniform distribution:**
```
P(-2)=0.2, P(-1)=0.2, P(0)=0.2, P(+1)=0.2, P(+2)=0.2
```
→ Result: Very spread-out distribution

**Narrow distribution:**
```
P(-2)=0.0, P(-1)=0.0, P(0)=0.95, P(+1)=0.05, P(+2)=0.0
```
→ Result: Sharp peak at charge 0

### Tip 4: Validation for Confidence

Always validate if possible:
1. Use validation tab with test datasets
2. Compare against published data
3. Run with different charge ranges
4. Check if results make biological sense

### Tip 5: Download Format

Downloaded CSV contains:
- Column 1: Charge value
- Column 2: Probability (as decimal)
- Column 3: Probability (as percentage)
- Column 4: Cumulative probability

**Use in Excel:**
- Charts → Create visualizations
- Formulas → Calculate statistics
- Pivot tables → Analyze subsets

---

## For Developers

### Modifying the App

ProtonPulse is open-source (MIT License). You can modify the code:

**Main files:**
- `ptm_charge_input_v2.py` — UI and app logic
- `advanced_algorithms.py` — Computation backend

**To modify:**
1. Edit the Python files
2. Run: `streamlit run ptm_charge_input_v2.py`
3. Changes reload automatically

### Adding Custom Charge Ranges

Edit `ptm_charge_input_v2.py`, find this section:

```python
charge_options = {
    "3-state (-1 to +1)": (-1, 1),
    "5-state (-2 to +2)": (-2, 2),
    # Add your own:
    "Custom Range": (-4, +3),
}
```

### Custom Algorithms

To add a new algorithm, edit `advanced_algorithms.py` and add a function:

```python
def my_algorithm(sites_data, charge_range):
    """Your algorithm here"""
    return probability_distribution
```

Then integrate into the selector in `ptm_charge_input_v2.py`.

### Command-Line Usage

For batch processing:

```bash
python ptm_charge_input_v2.py --input data.csv --output results.csv
```

(Requires custom command-line interface—see GitHub for examples)

---

## Troubleshooting Reference

### "My probabilities don't sum to 1.0"

**What's happening:** You entered 0.2 + 0.3 + 0.3 + 0.1 = 0.9

**Fix:**
- Adjust one probability to make sum = 1.0
- (0.2 + 0.3 + 0.3 + 0.2 = 1.0) ✓

### "Results look wrong"

**Check:**
1. Did you validate with known test data first?
2. Are your probabilities correct?
3. Did you use the right charge range?

**Validate:** Use the "Validate" tab

### "CSV won't upload"

**Check:**
- Column names exactly match: `Site_ID`, `Copies`, `P(-2)`, etc.
- All probabilities are decimals (0.0 to 1.0)
- File is `.csv` not `.xlsx`

**Try:** Download template from app and use that format

### "Different result than expected"

**Possible causes:**
1. You calculated by hand and made an error
2. Different algorithm selected (try validation tab)
3. Charge range different than expected

**Verify:** Use validation with known-good data

---

## Questions?

 - **Setup issues:** See [INSTALL/INSTALLATION_GUIDE.md](INSTALL/INSTALLATION_GUIDE.md)
 - **Algorithm details:** See [README.md](README.md) or in-app Welcome tab
 - **Feature requests:** Submit on GitHub
 - **Bug reports:** Contact development team

---

**Version:** 2.3 | December 2025
**For more info:** See [README.md](README.md) or launch the app and check the Welcome tab
