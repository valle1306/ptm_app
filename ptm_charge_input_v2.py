"""
ProtonPulse - PTM Charge Distribution Analyzer
Version 2.3 | December 2025
Developed by Valerie Le & Alex Goferman
"""
import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import advanced algorithms
try:
    from advanced_algorithms import adaptive_charge_distribution
    ADVANCED_ALGORITHMS_AVAILABLE = True
except ImportError:
    ADVANCED_ALGORITHMS_AVAILABLE = False

# ============ PAGE CONFIG (MUST BE FIRST) ============
st.set_page_config(
    page_title="ProtonPulse",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🔬"
)

# ============ CSS ============
st.markdown("""
<style>
    /* Compact layout - reduce padding and margins */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Reduce main content font size slightly */
    .stMarkdown, .stText, p, span {
        font-size: 0.9rem !important;
    }
    
    /* Compact headers */
    h1 { font-size: 1.6rem !important; margin-bottom: 0.3rem !important; }
    h2 { font-size: 1.3rem !important; margin-bottom: 0.3rem !important; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.2rem !important; }
    
    /* Compact tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.3rem 0.8rem !important;
        font-size: 0.85rem !important;
    }
    
    /* Compact expanders */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important;
        padding: 0.4rem 0.6rem !important;
    }
    .streamlit-expanderContent {
        padding: 0.5rem !important;
    }
    
    /* Compact metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    
    /* Compact buttons */
    .stButton > button {
        padding: 0.3rem 0.8rem !important;
        font-size: 0.85rem !important;
    }
    
    /* Compact data editor */
    .stDataFrame, [data-testid="stDataFrame"] {
        font-size: 0.85rem !important;
    }
    
    /* Compact selectbox */
    .stSelectbox > div > div {
        font-size: 0.85rem !important;
    }
    
    /* Compact file uploader */
    .stFileUploader {
        font-size: 0.85rem !important;
    }
    
    /* Reduce vertical spacing */
    .element-container {
        margin-bottom: 0.3rem !important;
    }
    
    /* Compact dividers */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    /* Welcome box with molecular background image */
    .welcome-box {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.85) 0%, rgba(79, 70, 229, 0.8) 50%, rgba(139, 92, 246, 0.85) 100%);
        padding: 25px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(79, 70, 229, 0.4);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .welcome-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url('https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=1200');
        background-size: cover;
        background-position: center;
        opacity: 0.15;
        z-index: 0;
    }
    .welcome-box::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        animation: pulse 3s ease-in-out infinite;
        z-index: 0;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.3; }
        50% { transform: scale(1.2); opacity: 0.6; }
    }
    .welcome-box h2 {
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
        position: relative;
        z-index: 1;
        font-weight: 600;
    }
    .welcome-box p {
        font-size: 1rem !important;
        margin-bottom: 0 !important;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
    }
    
    /* Compact sidebar */
    .css-1d391kg {
        padding: 1rem 0.5rem !important;
    }
    
    /* Plotly chart - make more compact */
    .js-plotly-plot {
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🔬 ProtonPulse")
    st.caption("PTM Charge Distribution Analyzer")
    st.markdown("---")
    st.markdown("""
    **Developed by:**  
    Valerie Le & Alex Goferman  
    MSDS Program, Rutgers University
    
    **Version:** 2.3 | December 2025
    """)

# ============ HELPER FUNCTIONS ============
def generate_charge_columns(min_charge, max_charge):
    base_cols = ["Site_ID", "Copies"]
    charge_cols = []
    for charge in range(min_charge, max_charge + 1):
        if charge == 0:
            charge_cols.append("P(0)")
        elif charge > 0:
            charge_cols.append(f"P(+{charge})")
        else:
            charge_cols.append(f"P({charge})")
    return base_cols + charge_cols

def index_for_charge(charge, min_charge):
    return int(charge - min_charge)

def neutral_index_for_range(min_charge, max_charge):
    if min_charge <= 0 <= max_charge:
        return index_for_charge(0, min_charge)
    candidate = min(range(min_charge, max_charge + 1), key=lambda x: abs(x))
    return index_for_charge(candidate, min_charge)

def parse_charge_from_column(col):
    """Parse charge value from column name like P(-2), P(0), P(+3)"""
    charge_str = col[2:-1]  # Extract content between P( and )
    if charge_str.startswith('+'):
        return int(charge_str[1:])
    elif charge_str.startswith('-'):
        return -int(charge_str[1:])
    else:
        return int(charge_str)

def detect_charge_range_from_df(df):
    """Detect min and max charge from dataframe columns"""
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    if not prob_cols:
        return -2, 2  # Default
    charges = [parse_charge_from_column(col) for col in prob_cols]
    return min(charges), max(charges)

def yergeev_overall_charge_distribution(df, tol=1e-9):
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    charges = [parse_charge_from_column(col) for col in prob_cols]
    
    min_charge = min(charges)
    result_pmf = np.array([1.0])
    result_offset = 0
    
    for idx, row in df.iterrows():
        if pd.isna(row.get("Copies")):
            continue
        copies = int(row["Copies"])
        if copies <= 0:
            continue
        
        site_probs = row[prob_cols].astype(float).fillna(0.0).to_numpy()
        s = site_probs.sum()
        if s > 0:
            site_pmf = site_probs / s
        else:
            site_pmf = site_probs
        
        site_offset = min_charge
        for _ in range(copies):
            result_pmf = np.convolve(result_pmf, site_pmf)
            result_offset = result_offset + site_offset
    
    s = result_pmf.sum()
    if s > 0:
        result_pmf = result_pmf / s
    result_pmf[result_pmf < tol] = 0.0
    s2 = result_pmf.sum()
    if s2 > 0:
        result_pmf = result_pmf / s2
    
    return result_pmf, result_offset

def enumerate_charge_combinations(df, max_combinations=100000000, timeout=30):
    start_time = time.time()
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    charges = [parse_charge_from_column(col) for col in prob_cols]
    
    min_charge, max_charge = min(charges), max(charges)
    
    total_combinations = 1
    for _, row in df.iterrows():
        if pd.isna(row.get("Copies")):
            continue
        copies = int(row["Copies"])
        if copies > 0:
            total_combinations *= (len(prob_cols) ** copies)
    
    if total_combinations > max_combinations:
        return None, None, "unavailable"
    
    sites_data = []
    for _, row in df.iterrows():
        if pd.isna(row.get("Copies")):
            continue
        copies = int(row["Copies"])
        if copies <= 0:
            continue
        probs = row[prob_cols].astype(float).fillna(0.0).to_numpy()
        s = probs.sum()
        if s > 0:
            probs = probs / s
        charge_list = np.array(charges)
        for _ in range(copies):
            sites_data.append({'charges': charge_list, 'probs': probs})
    
    distribution = {}
    
    def enumerate_recursive(site_idx, current_charge, current_prob):
        if time.time() - start_time > timeout:
            raise TimeoutError()
        if site_idx == len(sites_data):
            distribution[current_charge] = distribution.get(current_charge, 0.0) + current_prob
            return
        site = sites_data[site_idx]
        for charge_idx, charge in enumerate(site['charges']):
            prob = site['probs'][charge_idx]
            if prob > 0:
                enumerate_recursive(site_idx + 1, current_charge + charge, current_prob * prob)
    
    try:
        enumerate_recursive(0, 0, 1.0)
    except TimeoutError:
        return None, None, "unavailable"
    
    if not distribution:
        return np.array([1.0]), 0, "exact"
    
    n_sites_total = len(sites_data)
    min_result = n_sites_total * min_charge
    max_result = n_sites_total * max_charge
    offset = min_result
    
    pmf = np.zeros(max_result - min_result + 1)
    for charge, prob in distribution.items():
        idx = charge - offset
        if 0 <= idx < len(pmf):
            pmf[idx] = prob
    
    s = pmf.sum()
    if s > 0:
        pmf = pmf / s
    return pmf, offset, "exact"

def window_distribution(arr, off, low=-5, high=+5):
    charges = np.arange(off, off + len(arr))
    mask = (charges >= low) & (charges <= high)
    window = pd.DataFrame({"Charge": charges[mask], "Probability": arr[mask]})
    tail_low = arr[charges < low].sum()
    tail_high = arr[charges > high].sum()
    return window, float(tail_low), float(tail_high)

def get_charge_color(charge):
    """Color scheme: gradient from red (negative) → green (neutral) → blue (positive)"""
    if charge < -2:
        return '#d62728'  # Dark red for very negative
    elif charge < 0:
        return '#ff7f0e'  # Orange for slightly negative
    elif charge == 0:
        return '#2ca02c'  # Green for neutral
    elif charge <= 2:
        return '#1f77b4'  # Blue for slightly positive
    else:
        return '#9467bd'  # Purple for very positive

# ============ SESSION STATE ============
if "charge_system" not in st.session_state:
    st.session_state.charge_system = "5-state"
    st.session_state.min_charge = -2
    st.session_state.max_charge = 2

if "df" not in st.session_state:
    cols = generate_charge_columns(-2, 2)
    st.session_state.df = pd.DataFrame([
        ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
        ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ["Site_3", 2, 0.0, 0.0, 1.0, 0.0, 0.0],
        ["Site_4", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ["Site_5", 1, 0.1, 0.2, 0.4, 0.2, 0.1],
    ], columns=cols)

if "last_results" not in st.session_state:
    st.session_state.last_results = None

# ============ MAIN TITLE ============
st.title("🔬 ProtonPulse")

# ============ TABS ============
tab_welcome, tab_input, tab_compute, tab_validate = st.tabs([
    "🏠 Welcome", "📝 Data Input", "📊 Compute & Visualize", "✅ Validate"
])

# ============ TAB: WELCOME ============
with tab_welcome:
    st.markdown("""
    <div class="welcome-box">
        <h2>🔬 Welcome to ProtonPulse</h2>
        <p>Compute charge variant distributions for PTM-modified proteins using adaptive algorithms that scale from exact convolution to FFT-accelerated methods.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **📝 Data Input** - Upload CSV or enter PTM sites
        2. **📊 Compute** - Calculate charge distribution  
        3. **✅ Validate** - Verify accuracy against benchmarks
        """)
        
        with st.expander("📖 What is this tool?"):
            st.markdown("""
            This tool calculates the **overall charge state distribution** of a protein 
            with multiple post-translational modification (PTM) sites.
            
            Each site can exist in different charge states (e.g., -2 to +2), 
            and you provide the probability of each charge state at each site.
            
            The algorithm computes the probability distribution of the **total charge** 
            across all sites combined.
            """)
        
        with st.expander("🧪 Example Use Case"):
            st.markdown("""
            **Scenario:** A protein with 5 phosphorylation sites.
            
            - Site 1: 100% neutral (unphosphorylated)
            - Site 2: 60% neutral, 20% -1, 20% +1
            - Site 3: 2 copies, both neutral
            
            → Tool calculates P(total charge = -5, -4, ..., +5)
            """)
    
    with col2:
        st.markdown("### 🔬 Algorithm Overview")
        with st.expander("How does it work?", expanded=True):
            st.markdown("""
            **Adaptive Algorithm Selection:**
            
            ProtonPulse automatically chooses the best method based on your data size:
            
            | Copies | Method | Accuracy |
            |--------|--------|----------|
            | ≤50 | Yergeev Convolution | Exact |
            | 51-200 | FFT-Accelerated | Exact |
            | >200 | Gaussian (CLT) | Approximate |
            
            **Why not enumerate all combinations?**
            - For 5 charge states & n copies: 5ⁿ combinations
            - 10 copies = 9.7 million combinations
            - 20 copies = 95 trillion combinations 🤯
            - Convolution avoids this exponential explosion
            """)
        
        with st.expander("📚 References"):
            st.markdown("""
            - Yergey, J.A. (1983). *A general approach to calculating isotopic distributions for mass spectrometry*
            - Central Limit Theorem for Gaussian approximation
            - FFT-based convolution for large datasets
            """)
    
    # App Demo Section
    st.markdown("---")
    with st.expander("🎬 App Demo (Quick Walkthrough)", expanded=False):
        demo_col1, demo_col2 = st.columns(2)
        
        with demo_col1:
            st.markdown("""
            #### Step 1: Prepare Your Data
            1. Go to **📝 Data Input** tab
            2. Choose your charge range (e.g., -2 to +2)
            3. Either:
               - Download a template CSV
               - Edit the example data directly
               - Upload your own CSV
            
            #### Step 2: Enter PTM Sites
            - Each row = one PTM site
            - Set **Copies** (how many times it appears)
            - Enter probabilities for each charge state
            - Ensure each row sums to 1.0
            """)
        
        with demo_col2:
            st.markdown("""
            #### Step 3: Compute Results
            1. Go to **📊 Compute & Visualize** tab
            2. Click **🚀 Compute Distribution**
            3. View:
               - Distribution chart
               - Summary statistics
               - Most likely charge state
            
            #### Step 4: Export & Validate
            - Download results as CSV
            - Use **✅ Validate** tab to verify accuracy
            - Compare against benchmark methods
            """)
        
        st.info("💡 **Tip:** Start with the example data to see how the tool works before uploading your own data.")

# ============ TAB: DATA INPUT ============
with tab_input:
    st.markdown("### 📝 Data Input")
    st.caption("Define your PTM sites and their charge state probabilities")
    
    # Track if CSV was just loaded
    if "csv_loaded" not in st.session_state:
        st.session_state.csv_loaded = False
    
    # CSV Upload Section - collapsible after successful load
    if st.session_state.csv_loaded:
        # Show compact success message with option to upload new file
        up_col1, up_col2, up_col3 = st.columns([3, 2, 2])
        with up_col1:
            st.success(f"✅ Data loaded: {len(st.session_state.df)} sites, {int(st.session_state.df['Copies'].sum())} total copies")
        with up_col2:
            csv_data = st.session_state.df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="ptm_data.csv",
                mime="text/csv",
                help="Download current data for editing in Excel"
            )
        with up_col3:
            if st.button("📤 Upload New CSV", key="btn_new_upload"):
                st.session_state.csv_loaded = False
                st.rerun()
    else:
        # Show file uploader
        st.markdown("#### 📁 Load Data")
        file_col1, file_col2 = st.columns([3, 2])
        
        with file_col1:
            uploaded_file = st.file_uploader(
                "📤 Upload CSV", 
                type=['csv'], 
                key="csv_uploader",
                help="CSV with columns: Site_ID, Copies, P(-2), P(-1), P(0), P(+1), P(+2)"
            )
            if uploaded_file is not None:
                try:
                    uploaded_df = pd.read_csv(uploaded_file)
                    # Auto-detect charge range from columns
                    prob_cols_uploaded = [c for c in uploaded_df.columns if c.startswith("P(")]
                    if prob_cols_uploaded:
                        charges = []
                        for col in prob_cols_uploaded:
                            charge_str = col[2:-1]
                            if charge_str.startswith('+'):
                                charges.append(int(charge_str[1:]))
                            elif charge_str.startswith('-'):
                                charges.append(-int(charge_str[1:]))
                            else:
                                charges.append(int(charge_str))
                        st.session_state.min_charge = min(charges)
                        st.session_state.max_charge = max(charges)
                    st.session_state.df = uploaded_df
                    st.session_state.last_results = None
                    st.session_state.csv_loaded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading CSV: {e}")
        
        with file_col2:
            # Adaptive template download with charge range selector
            st.markdown("**📋 Download Template**")
            
            # Template charge range options
            template_options = {
                "-1 to +1 (3 states)": (-1, 1),
                "-2 to +2 (5 states)": (-2, 2),
                "-3 to +3 (7 states)": (-3, 3),
                "-5 to +5 (11 states)": (-5, 5),
                "-7 to +7 (15 states)": (-7, 7),
            }
            
            selected_template = st.selectbox(
                "Charge range for template:",
                list(template_options.keys()),
                index=1,  # Default to -2 to +2
                key="template_range_selector",
                help="Choose the charge range for your CSV template"
            )
            
            tpl_min, tpl_max = template_options[selected_template]
            template_cols = generate_charge_columns(tpl_min, tpl_max)
            neutral = neutral_index_for_range(tpl_min, tpl_max)
            template_probs = [0.0] * (tpl_max - tpl_min + 1)
            template_probs[neutral] = 1.0
            template_df = pd.DataFrame([["Site_1", 1] + template_probs], columns=template_cols)
            template_csv = template_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download",
                data=template_csv,
                file_name=f"ptm_template_{tpl_min}_to_{tpl_max}.csv",
                mime="text/csv",
                help=f"Download template with {selected_template}"
            )
            st.caption("Edit in Excel, then upload")
    
    st.markdown("---")
    st.markdown("#### ⚙️ Settings")
    
    # Controls
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    
    with c1:
        # Build charge options dynamically - include current range if custom
        charge_options = {
            "3-state (-1 to +1)": (-1, 1),
            "5-state (-2 to +2)": (-2, 2),
            "7-state (-3 to +3)": (-3, 3),
            "9-state (-4 to +4)": (-4, 4),
            "11-state (-5 to +5)": (-5, 5),
            "13-state (-6 to +6)": (-6, 6),
            "15-state (-7 to +7)": (-7, 7),
            "21-state (-10 to +10)": (-10, 10),
        }
        
        # Detect current range from loaded data
        current_min = st.session_state.min_charge
        current_max = st.session_state.max_charge
        n_states = current_max - current_min + 1
        current_key = f"{n_states}-state ({current_min} to +{current_max})"
        
        # Add current range to options if not already present
        if current_key not in charge_options:
            charge_options[current_key] = (current_min, current_max)
        
        # Sort options by number of states
        sorted_options = dict(sorted(charge_options.items(), key=lambda x: x[1][1] - x[1][0]))
        option_keys = list(sorted_options.keys())
        
        # Find the index of current selection
        try:
            current_index = option_keys.index(current_key)
        except ValueError:
            current_index = 1  # Default to 5-state
        
        # Only show the selector if NOT in csv_loaded mode (to prevent accidental reset)
        if st.session_state.csv_loaded:
            # Show read-only display of current range
            st.info(f"📊 Loaded: {n_states}-state ({current_min} to +{current_max})")
            if st.button("🔄 Change Range", key="btn_change_range", help="Reset data and choose a different charge range"):
                st.session_state.csv_loaded = False
                st.rerun()
        else:
            selection = st.selectbox("🔢 Charge Range", option_keys,
                                     index=current_index,
                                     key="input_charge_range")
            new_min, new_max = sorted_options[selection]
            
            if new_min != st.session_state.min_charge or new_max != st.session_state.max_charge:
                st.session_state.min_charge = new_min
                st.session_state.max_charge = new_max
                new_cols = generate_charge_columns(new_min, new_max)
                neutral_idx = neutral_index_for_range(new_min, new_max)
                probs1 = [0.0] * (new_max - new_min + 1)
                probs2 = [0.0] * (new_max - new_min + 1)
                probs1[neutral_idx] = 1.0
                probs2[neutral_idx] = 0.6
                if new_min <= -1 <= new_max:
                    probs2[index_for_charge(-1, new_min)] = 0.2
                if new_min <= 1 <= new_max:
                    probs2[index_for_charge(1, new_min)] = 0.2
                st.session_state.df = pd.DataFrame([
                    ["Site_1", 1] + probs1,
                    ["Site_2", 1] + probs2,
                ], columns=new_cols)
                st.session_state.last_results = None
                st.rerun()
    
    with c2:
        if st.button("📄 Load 100-site template", key="btn_template"):
            template_data = []
            for i in range(1, 101):
                copies = (i % 3) + 1
                neutral = neutral_index_for_range(st.session_state.min_charge, st.session_state.max_charge)
                probs = [0.0] * (st.session_state.max_charge - st.session_state.min_charge + 1)
                probs[neutral] = 0.6
                if st.session_state.min_charge <= -1:
                    probs[index_for_charge(-1, st.session_state.min_charge)] = 0.2
                if st.session_state.max_charge >= 1:
                    probs[index_for_charge(1, st.session_state.min_charge)] = 0.2
                template_data.append([f"Site_{i}", copies] + probs)
            st.session_state.df = pd.DataFrame(template_data,
                columns=generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge))
            st.session_state.last_results = None
            st.rerun()
    
    with c3:
        if st.button("🔄 Reset to default", key="btn_reset"):
            neutral = neutral_index_for_range(st.session_state.min_charge, st.session_state.max_charge)
            probs1 = [0.0] * (st.session_state.max_charge - st.session_state.min_charge + 1)
            probs2 = [0.0] * (st.session_state.max_charge - st.session_state.min_charge + 1)
            probs1[neutral] = 1.0
            probs2[neutral] = 0.6
            if st.session_state.min_charge <= -1:
                probs2[index_for_charge(-1, st.session_state.min_charge)] = 0.2
            if st.session_state.max_charge >= 1:
                probs2[index_for_charge(1, st.session_state.min_charge)] = 0.2
            st.session_state.df = pd.DataFrame([
                ["Site_1", 1] + probs1,
                ["Site_2", 1] + probs2,
            ], columns=generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge))
            st.session_state.last_results = None
            st.rerun()
    
    with c4:
        st.metric("Sites", len(st.session_state.df))
    
    st.markdown("---")
    
    with st.expander("💡 How to enter data"):
        st.markdown("""
        | Column | Description |
        |--------|-------------|
        | Site_ID | Name for your site (e.g., "Ser123") |
        | Copies | How many copies of this site (usually 1) |
        | P(-2)...P(+2) | Probability of each charge state (must sum to 1.0) |
        
        **💡 Tip:** For easier editing, download the data as CSV, edit in Excel, then upload!
        """)
    
    # Data editor - use a cleaner approach to avoid flickering
    st.markdown("**Edit probabilities below** (each row should sum to 1.0)")
    
    prob_cols = [col for col in st.session_state.df.columns if col.startswith("P(")]
    
    # Create a working copy for the editor (without computed columns)
    editor_df = st.session_state.df.copy()
    
    # Column configuration
    col_config = {
        "Site_ID": st.column_config.TextColumn("Site ID", width="small"),
        "Copies": st.column_config.NumberColumn("Copies", min_value=1, max_value=10, step=1, width="small"),
    }
    for col in prob_cols:
        col_config[col] = st.column_config.NumberColumn(col, min_value=0.0, max_value=1.0, step=0.01, format="%.3f")
    
    # Use on_change callback to properly handle edits
    edited = st.data_editor(
        editor_df,
        column_config=col_config,
        num_rows="dynamic",
        hide_index=True,
        key="main_data_editor",
        width="stretch"
    )
    
    # Update session state with edited data
    st.session_state.df = edited.copy()
    
    # Show validation status separately (not in the editor)
    if prob_cols and len(edited) > 0:
        sums = edited[prob_cols].sum(axis=1)
        valid_mask = np.isclose(sums, 1.0, atol=1e-6)
        invalid_count = sum(~valid_mask)
        
        # Show summary metrics
        val_col1, val_col2, val_col3 = st.columns(3)
        with val_col1:
            st.metric("Total Rows", len(edited))
        with val_col2:
            st.metric("Valid Rows", sum(valid_mask))
        with val_col3:
            if invalid_count > 0:
                st.metric("Invalid Rows", invalid_count, delta=f"-{invalid_count}", delta_color="inverse")
            else:
                st.metric("Invalid Rows", 0)
        
        if invalid_count > 0:
            st.warning(f"⚠️ {invalid_count} row(s) have Sum ≠ 1.0 (will be auto-normalized during compute)")
            # Show which rows are invalid
            with st.expander("Show invalid rows"):
                invalid_indices = np.where(~valid_mask)[0]
                for idx in invalid_indices[:5]:  # Show first 5
                    row_sum = sums.iloc[idx]
                    st.write(f"Row {idx+1} (Site: {edited.iloc[idx]['Site_ID']}): Sum = {row_sum:.4f}")
                if len(invalid_indices) > 5:
                    st.write(f"... and {len(invalid_indices) - 5} more")
        else:
            st.success("✅ All rows valid!")

# ============ TAB: COMPUTE ============
with tab_compute:
    st.markdown("### 📊 Compute & Visualize")
    
    df = st.session_state.df.copy()
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    n_sites = len(df)
    total_copies = int(df['Copies'].sum()) if 'Copies' in df.columns else n_sites
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sites", n_sites)
    with col2:
        st.metric("Total Copies", total_copies)
    with col3:
        if prob_cols:
            df["_sum"] = df[prob_cols].sum(axis=1)
            n_valid = sum(np.isclose(df["_sum"].fillna(0), 1.0, atol=1e-6))
            if n_valid == n_sites:
                st.success("✓ All valid")
            else:
                st.warning(f"⚠ {n_sites - n_valid} invalid")
    
    st.markdown("---")
    
    if st.button("🚀 Compute Distribution", type="primary", key="btn_compute"):
        with st.spinner("Computing..."):
            try:
                df_compute = df.copy()
                if prob_cols:
                    # Detect charge range from the actual data columns
                    data_min_charge, data_max_charge = detect_charge_range_from_df(df_compute)
                    
                    for idx, row in df_compute.iterrows():
                        probs = row[prob_cols].astype(float).fillna(0.0)
                        s = probs.sum()
                        if s <= 0:
                            # Use detected range from data, not session state
                            neutral_idx = neutral_index_for_range(data_min_charge, data_max_charge)
                            probs = pd.Series(0.0, index=prob_cols)
                            probs.iloc[neutral_idx] = 1.0
                        else:
                            probs = probs / s
                        df_compute.loc[idx, prob_cols] = probs.values

                if ADVANCED_ALGORITHMS_AVAILABLE:
                    start = time.time()
                    pmf_arr, pmf_off, method_used, _ = adaptive_charge_distribution(df_compute, method="auto")
                    elapsed = time.time() - start
                else:
                    start = time.time()
                    pmf_arr, pmf_off = yergeev_overall_charge_distribution(df_compute)
                    elapsed = time.time() - start
                    method_used = "Yergeev"
                
                # Per challenge requirements: main display shows -5 to +5
                # But also compute full distribution for those who want to see more
                window_df, tail_low, tail_high = window_distribution(pmf_arr, pmf_off, -5, +5)
                
                # Also compute full distribution for expanded view
                full_charges = np.arange(pmf_off, pmf_off + len(pmf_arr))
                full_df = pd.DataFrame({
                    "Charge": full_charges,
                    "Probability": pmf_arr
                })
                # Filter out zero probabilities for cleaner display
                full_df = full_df[full_df['Probability'] > 1e-10].reset_index(drop=True)
                
                st.session_state.last_results = {
                    "window_df": window_df,
                    "full_df": full_df,
                    "tail_low": tail_low,
                    "tail_high": tail_high,
                    "elapsed": elapsed,
                    "method": method_used,
                    "total_copies": total_copies,
                    "pmf_offset": pmf_off,
                    "pmf_length": len(pmf_arr)
                }
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.last_results = None
    
    # Show results
    if st.session_state.last_results:
        res = st.session_state.last_results
        window_df = res["window_df"]
        
        st.success(f"✓ Computed in {res['elapsed']*1000:.1f} ms using {res['method']}")
        
        most_likely = window_df.loc[window_df['Probability'].idxmax(), 'Charge']
        peak_prob = window_df['Probability'].max()
        central_mass = 1.0 - res["tail_low"] - res["tail_high"]
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("🎯 Most Likely", f"{most_likely:+.0f}")
        with m2:
            st.metric("📈 Peak Prob", f"{peak_prob:.1%}")
        with m3:
            st.metric("📊 Central Mass", f"{central_mass:.1%}")
        with m4:
            st.metric("🧬 Copies", res["total_copies"])
        
        st.markdown("---")
        
        # Distribution chart with interpretation on the side
        chart_col, interp_col = st.columns([3, 1])
        
        with chart_col:
            st.markdown("### 📈 Distribution (Charges -5 to +5)")
            st.caption("Per challenge requirements: showing main charge range. See below for full distribution.")
            
            colors = [get_charge_color(c) for c in window_df['Charge']]
            
            fig = make_subplots(rows=2, cols=1, row_heights=[0.6, 0.4], vertical_spacing=0.12,
                               subplot_titles=('Probability Distribution', 'Cumulative Distribution'))
            
            fig.add_trace(go.Bar(x=window_df['Charge'], y=window_df['Probability'], marker_color=colors,
                                hovertemplate='Charge: %{x:+d}<br>P: %{y:.4f}<extra></extra>'), row=1, col=1)
            
            cumulative = np.cumsum(window_df['Probability'].values)
            fig.add_trace(go.Scatter(x=window_df['Charge'].values, y=cumulative, mode='lines+markers',
                                    line=dict(color='#1f77b4', width=2), marker=dict(size=5),
                                    hovertemplate='P(≤%{x:+d}): %{y:.3f}<extra></extra>'), row=2, col=1)
            
            fig.add_hline(y=0.5, line_dash="dash", line_color="gray", row=2, col=1)
            fig.update_layout(height=450, showlegend=False, template='plotly_white', margin=dict(t=30, b=30))
            fig.update_xaxes(title_text="Charge State", row=2, col=1)
            fig.update_yaxes(title_text="Probability", row=1, col=1)
            fig.update_yaxes(title_text="Cumulative P", row=2, col=1)
            st.plotly_chart(fig, use_container_width=True)
            
            # Color legend
            st.markdown("""
            <div style="font-size: 0.8rem; color: #666;">
            <b>Color Key:</b> 
            <span style="color: #d62728;">■</span> Very Negative (< -2) |
            <span style="color: #ff7f0e;">■</span> Negative (-2 to -1) |
            <span style="color: #2ca02c;">■</span> Neutral (0) |
            <span style="color: #1f77b4;">■</span> Positive (+1 to +2) |
            <span style="color: #9467bd;">■</span> Very Positive (> +2)
            </div>
            """, unsafe_allow_html=True)
        
        with interp_col:
            st.markdown("### 🔍 Summary")
            st.markdown(f"""
            **Most likely charge:**  
            **{most_likely:+d}** ({peak_prob:.1%})
            
            ---
            
            **Mass in [-5, +5]:**  
            {central_mass:.1%}
            
            **Left tail** (< -5):  
            {res['tail_low']:.2%}
            
            **Right tail** (> +5):  
            {res['tail_high']:.2%}
            
            ---
            
            **Method:**  
            {res['method']}
            
            **Time:**  
            {res['elapsed']*1000:.1f} ms
            """)
            
            with st.expander("📋 Data (-5 to +5)"):
                st.dataframe(window_df, hide_index=True, height=180)
        
        # Full distribution section (expandable)
        st.markdown("---")
        with st.expander("📊 View Full Distribution (Beyond -5 to +5)", expanded=False):
            full_df = res.get("full_df")
            if full_df is not None and len(full_df) > 0:
                st.markdown(f"**Full range:** {int(full_df['Charge'].min()):+d} to {int(full_df['Charge'].max()):+d}")
                
                # Full distribution chart
                full_colors = [get_charge_color(c) for c in full_df['Charge']]
                
                fig_full = go.Figure()
                fig_full.add_trace(go.Bar(
                    x=full_df['Charge'], 
                    y=full_df['Probability'], 
                    marker_color=full_colors,
                    hovertemplate='Charge: %{x:+d}<br>P: %{y:.6f}<extra></extra>'
                ))
                fig_full.update_layout(
                    height=300, 
                    template='plotly_white',
                    xaxis_title="Charge State",
                    yaxis_title="Probability",
                    margin=dict(t=20, b=40)
                )
                st.plotly_chart(fig_full, use_container_width=True)
                
                # Data table
                col_data1, col_data2 = st.columns(2)
                with col_data1:
                    st.markdown("**Probability Table:**")
                    # Format for display
                    display_df = full_df.copy()
                    display_df['Probability'] = display_df['Probability'].apply(lambda x: f"{x:.6f}")
                    st.dataframe(display_df, hide_index=True, height=250)
                with col_data2:
                    # Download option
                    csv_data = full_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Full Distribution (CSV)",
                        data=csv_data,
                        file_name="charge_distribution_full.csv",
                        mime="text/csv"
                    )
                    st.markdown(f"""
                    **Statistics:**
                    - Total charge states: {len(full_df)}
                    - Min charge: {int(full_df['Charge'].min()):+d}
                    - Max charge: {int(full_df['Charge'].max()):+d}
                    - Total probability: {full_df['Probability'].sum():.6f}
                    """)
            else:
                st.info("Full distribution data not available.")
                
    else:
        st.info("👆 Click **Compute Distribution** to calculate results")

# ============ TAB: VALIDATE ============
with tab_validate:
    st.markdown("### ✅ Validation & Benchmarking")
    
    total_copies = int(st.session_state.df['Copies'].sum()) if 'Copies' in st.session_state.df.columns else len(st.session_state.df)
    
    # Thresholds
    ENUM_LIMIT = 12  # Enumeration feasible only for small datasets
    
    # Determine which benchmark to use
    if total_copies <= ENUM_LIMIT:
        benchmark_method = "enumeration"
        benchmark_name = "Exact Enumeration"
        benchmark_note = f"✅ Small dataset ({total_copies} copies) - using enumeration as ground truth"
        can_enumerate = True
    else:
        benchmark_method = "yergeev"
        benchmark_name = "Yergeev Convolution"
        benchmark_note = f"📊 Large dataset ({total_copies} copies) - enumeration infeasible (5^{total_copies} combinations)"
        can_enumerate = False
    
    with st.expander("ℹ️ Why These Benchmarks?"):
        st.markdown(f"""
        **Current Dataset:** {total_copies} total copies
        
        | Method | Complexity | Feasibility |
        |--------|-----------|-------------|
        | **Enumeration** | 5^n = 5^{total_copies} | {'✅ Feasible' if can_enumerate else '❌ Impossible'} |
        | **Yergeev** | O(n²) | ✅ Always fast |
        | **FFT** | O(n log n) | ✅ Always fast |
        | **Gaussian** | O(n) | ✅ Instant (approx) |
        
        {'**Using Enumeration** as benchmark - this explores ALL possible charge combinations and gives absolute ground truth.' if can_enumerate else f'**Using Yergeev** as benchmark - enumeration would need 5^{total_copies} ≈ 10^{int(total_copies * 0.7)} operations!'}
        """)
    
    # Show dataset info
    info_cols = st.columns(3)
    with info_cols[0]:
        st.metric("Total Copies", total_copies)
    with info_cols[1]:
        st.metric("Benchmark", benchmark_name.split()[0])
    with info_cols[2]:
        if can_enumerate:
            st.success("✓ Enum feasible")
        else:
            st.info("Yergeev benchmark")
    
    st.caption(benchmark_note)
    
    # Algorithm selection
    st.markdown("#### 🧪 Methods to Test")
    cmp_col1, cmp_col2, cmp_col3, cmp_col4 = st.columns(4)
    with cmp_col1:
        compare_yergeev = st.checkbox("Yergeev", value=True, key="cmp_yergeev")
    with cmp_col2:
        compare_fft = st.checkbox("FFT", value=True, key="cmp_fft")
    with cmp_col3:
        compare_gaussian = st.checkbox("Gaussian", value=True, key="cmp_gaussian")
    with cmp_col4:
        # Only show enumeration option if feasible
        if can_enumerate:
            compare_enum = st.checkbox("Enumeration", value=True, key="cmp_enum", 
                                       help="Ground truth - tests all combinations")
        else:
            compare_enum = False
            st.caption("Enum: N/A")
    
    if st.button("🔍 Run Benchmark", key="btn_validate", type="primary"):
        with st.spinner("Running benchmark..."):
            try:
                df_val = st.session_state.df.copy()
                prob_cols = [col for col in df_val.columns if col.startswith("P(")]
                
                # Normalize probabilities
                for idx, row in df_val.iterrows():
                    probs = row[prob_cols].astype(float).fillna(0.0)
                    s = probs.sum()
                    if s > 0:
                        df_val.loc[idx, prob_cols] = (probs / s).values
                
                results = {}
                benchmark_result = None
                
                # Run benchmark first
                if benchmark_method == "enumeration" and can_enumerate:
                    t0 = time.time()
                    pmf_b, off_b, status = enumerate_charge_combinations(df_val)
                    time_b = time.time() - t0
                    if pmf_b is not None and status == "exact":
                        benchmark_result = {'pmf': pmf_b, 'offset': off_b, 'time': time_b}
                        results['📌 Enumeration (Ground Truth)'] = benchmark_result
                    else:
                        # Fallback to Yergeev
                        t0 = time.time()
                        pmf_b, off_b = yergeev_overall_charge_distribution(df_val)
                        time_b = time.time() - t0
                        benchmark_result = {'pmf': pmf_b, 'offset': off_b, 'time': time_b}
                        results['📌 Yergeev (Benchmark)'] = benchmark_result
                else:
                    t0 = time.time()
                    pmf_b, off_b = yergeev_overall_charge_distribution(df_val)
                    time_b = time.time() - t0
                    benchmark_result = {'pmf': pmf_b, 'offset': off_b, 'time': time_b}
                    results['📌 Yergeev (Benchmark)'] = benchmark_result
                
                # Yergeev (if selected and not already benchmark)
                if compare_yergeev and '📌 Yergeev (Benchmark)' not in results:
                    t0 = time.time()
                    pmf_y, off_y = yergeev_overall_charge_distribution(df_val)
                    time_y = time.time() - t0
                    results['Yergeev'] = {'pmf': pmf_y, 'offset': off_y, 'time': time_y}
                
                # Enumeration (if selected and feasible, and not already benchmark)
                if compare_enum and can_enumerate and '📌 Enumeration' not in str(results.keys()):
                    t0 = time.time()
                    pmf_e, off_e, status = enumerate_charge_combinations(df_val)
                    time_e = time.time() - t0
                    if pmf_e is not None:
                        results['Enumeration'] = {'pmf': pmf_e, 'offset': off_e, 'time': time_e}
                
                # FFT
                if compare_fft and ADVANCED_ALGORITHMS_AVAILABLE:
                    from advanced_algorithms import fft_accelerated_charge_distribution
                    pmf_fft, off_fft, time_fft = fft_accelerated_charge_distribution(df_val)
                    results['FFT'] = {'pmf': pmf_fft, 'offset': off_fft, 'time': time_fft}
                
                # Gaussian
                if compare_gaussian and ADVANCED_ALGORITHMS_AVAILABLE:
                    from advanced_algorithms import gaussian_approximation_charge_distribution
                    pmf_g, off_g, time_g = gaussian_approximation_charge_distribution(df_val)
                    results['Gaussian'] = {'pmf': pmf_g, 'offset': off_g, 'time': time_g}
                
                # Display results in two columns
                st.markdown("---")
                res_col1, res_col2 = st.columns([1, 1])
                
                with res_col1:
                    st.markdown("#### ⏱️ Performance")
                    perf_data = []
                    for name, data in results.items():
                        if data['time'] < 0.001:
                            time_str = f"{data['time']*1000000:.1f} μs"
                        elif data['time'] < 1:
                            time_str = f"{data['time']*1000:.1f} ms"
                        else:
                            time_str = f"{data['time']:.2f} s"
                        display_name = name.replace('📌 ', '').split(' (')[0]
                        perf_data.append({'Method': display_name, 'Time': time_str})
                    st.dataframe(pd.DataFrame(perf_data), hide_index=True)
                
                with res_col2:
                    st.markdown("#### 📊 Accuracy")
                    
                    # Get benchmark window
                    win_b, _, _ = window_distribution(benchmark_result['pmf'], benchmark_result['offset'], -5, +5)
                    
                    comparison_data = []
                    for name, data in results.items():
                        display_name = name.replace('📌 ', '').split(' (')[0]
                        
                        if '📌' in name:
                            comparison_data.append({'Method': display_name, 'Max Diff': '-', 'Status': '📌 BENCHMARK'})
                            continue
                        
                        win_other, _, _ = window_distribution(data['pmf'], data['offset'], -5, +5)
                        max_diff = 0.0
                        if len(win_b) == len(win_other):
                            max_diff = np.max(np.abs(win_b['Probability'].values - win_other['Probability'].values))
                        
                        if max_diff < 1e-10:
                            status = '🎯 PERFECT'
                        elif max_diff < 1e-6:
                            status = '✅ Exact'
                        elif max_diff < 0.01:
                            status = '⚠️ ~Approx'
                        else:
                            status = '❌ Differs'
                        
                        comparison_data.append({'Method': display_name, 'Max Diff': f'{max_diff:.2e}', 'Status': status})
                    
                    st.dataframe(pd.DataFrame(comparison_data), hide_index=True)
                
                # Summary
                non_benchmark = [d for d in comparison_data if 'BENCHMARK' not in d['Status']]
                if non_benchmark:
                    all_perfect = all('PERFECT' in d['Status'] or 'Exact' in d['Status'] for d in non_benchmark)
                    if all_perfect:
                        st.success("🎉 All exact methods match benchmark perfectly!")
                    else:
                        gaussian_diff = [d for d in non_benchmark if 'Gaussian' in d['Method']]
                        if gaussian_diff and 'Approx' in gaussian_diff[0]['Status']:
                            st.info("ℹ️ Gaussian is an approximation (expected small difference)")
                
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                with st.expander("Error details"):
                    st.code(traceback.format_exc())
