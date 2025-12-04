# ProtonPulse - Quick Start Guide

**For Bench Scientists & Lab Researchers**

This guide assumes you've already completed the one-time installation. If not, see the `INSTALL/INSTALLATION_GUIDE.md` first.

---

## ⚡ The Fast Version (TL;DR)

**Every time you want to use ProtonPulse:**

1. **Double-click the "ProtonPulse" shortcut on your desktop**
2. Wait ~5 seconds
3. Browser opens automatically
4. Start analyzing!

**That's it.** No terminal, no commands, no setup—just click.

---

## 🎯 First Time Setup

If you don't see a "ProtonPulse" shortcut on your desktop yet:

1. Open the `ProtonPulse` folder
2. Go to the `INSTALL` subfolder
3. Double-click: `create_shortcut.ps1`
4. Check your desktop—shortcut is there!

---

## 📊 Using the App

### The Four Tabs

#### 1️⃣ Welcome (`🏠`)
- Learn what ProtonPulse does
- See algorithm explanations
- Read example use cases

#### 2️⃣ Data Input (`📝`)
- **Upload a CSV file** (if you have one)
- **OR edit example data** directly in the app
- **OR download a template**, edit in Excel, upload back

**Example CSV format:**
```
Site_ID,Copies,P(-2),P(-1),P(0),P(+1),P(+2)
Site_1,1,0.0,0.0,1.0,0.0,0.0
Site_2,1,0.0,0.2,0.6,0.2,0.0
Site_3,2,0.0,0.0,1.0,0.0,0.0
```

#### 3️⃣ Compute (`📊`)
- Click the **"🚀 Compute Distribution"** button
- See instant results:
  - Bar charts (probability distribution)
  - Line chart (cumulative distribution)
  - Summary statistics
  - Download results as CSV

#### 4️⃣ Validate (`✅`)
- Compare different calculation methods
- Verify accuracy of results
- For verification purposes only

---

## 🔄 Typical Workflow

### Scenario: You have a protein with PTM sites

```
Step 1: Click "📝 Data Input" tab

Step 2: OPTION A - Use Your Own Data
        - Click "📤 Upload CSV"
        - Select your file
        - App auto-detects format
        
        OR OPTION B - Use Template
        - Click "📋 Download Template"
        - Edit in Excel (add your sites)
        - Save and upload back
        
        OR OPTION C - Edit Directly
        - Edit the example data in the table
        - Add/remove rows as needed

Step 3: Click "📊 Compute & Visualize" tab

Step 4: Click "🚀 Compute Distribution" button

Step 5: See Results!
        - Graph of charge distribution
        - Summary statistics (most likely charge, etc.)
        - Download button for CSV results

Step 6: (Optional) Expand "View Full Distribution"
        - See charges beyond -5 to +5 range
        - Download full results if needed
```

---

## 💾 About Your Data

| Question | Answer |
|----------|--------|
| **Where is my data stored?** | Only in your browser (temporary) |
| **Is it uploaded to the cloud?** | No, never |
| **Can the app see my files?** | Only what you upload to it |
| **What happens when I close?** | Everything is deleted |
| **Is it private?** | Yes, 100% |

---

## ⚙️ Settings & Options

### In the "Data Input" tab:

- **Charge Range**: Select from 3-state to 21-state (default: 5-state)
- **Load 100-site template**: Quick test with 100 sample sites
- **Reset to default**: Go back to original example
- **Edit probabilities**: Click cells in the table to change values

### In the "Compute" tab:

- **View Full Distribution**: Expand to see all charge states (beyond -5 to +5)
- **Download results**: Click to save as CSV

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **App doesn't open** | Double-click shortcut again, wait 10 sec |
| **CSV won't upload** | Download template and use that format |
| **Numbers look wrong** | Make sure probabilities sum to 1.0 in each row |
| **Need to stop the app** | Close the browser and terminal |
| **Port error (8501 in use)** | Close other ProtonPulse windows |

**For detailed troubleshooting, see:** `INSTALL/INSTALLATION_GUIDE.md`

---

## 📚 More Help

- **Full installation guide**: `INSTALL/INSTALLATION_GUIDE.md`
- **Technical details**: `README.md`
- **Questions?** Email the development team

---

## 🎓 Understanding the Results

### What is "Charge Distribution"?

Each PTM site can be in different charge states (e.g., -2, -1, 0, +1, +2).

The app calculates: **For all possible combinations of charges across all sites, what's the probability of each total charge?**

### The Graph

- **X-axis**: Total charge (e.g., -5 to +5)
- **Y-axis**: Probability (0% to 100%)
- **Bars colored by**:
  - 🔴 Red = Very negative (< -2)
  - 🟠 Orange = Negative (-2 to -1)
  - 🟢 Green = Neutral (0)
  - 🔵 Blue = Positive (+1 to +2)
  - 🟣 Purple = Very positive (> +2)

### Summary Statistics

- **Most Likely Charge**: The peak of the distribution (highest probability)
- **Peak Prob**: The probability at that peak
- **Central Mass**: Percentage of probability in the main range (-5 to +5)
- **Tails**: Probability at extreme charges

---

## 💡 Tips & Tricks

1. **Keep files organized**: Save templates in a folder like `C:\PTM_Data\`

2. **Edit in Excel**: Download template → Edit → Upload (easier than clicking cells)

3. **Test with different ranges**: Try 5-state vs 11-state to see differences

4. **Download for sharing**: Export results as CSV to share with colleagues

5. **Use validation tab**: Run comparison if you want to verify results

---

## 🔧 Advanced: If You Know Command Line

```powershell
# Run app from terminal (instead of shortcut)
cd C:\Path\To\ProtonPulse
.\run_protonpulse.bat

# Or with PowerShell
.\run_protonpulse.ps1
```

---

**Version:** 2.3 | December 2025

**Questions?** See the INSTALL folder or check README.md
