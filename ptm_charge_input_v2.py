import io
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="PTM Charge Analyzer", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🧬"
)

# Custom CSS for better styling and probability highlighting
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton>button {
        border-radius: 5px;
    }
    div[data-testid="stExpander"] {
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    /* Highlight probability columns */
    [data-testid="column"] [data-testid="stDataFrameResizable"] table th {
        background-color: #e3f2fd !important;
    }
    /* Make metrics more colorful */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with logo, about, and credits
with st.sidebar:
    st.markdown("# 🧬 PTM Analyzer")
    st.markdown("### Post-Translational Modification Charge Distribution Calculator")
    st.markdown("---")
    
    st.markdown("**ℹ️ About**")
    st.markdown("""
    Calculate overall charge distributions for proteins with multiple PTM sites 
    using probability generating functions.
    """)
    
    st.markdown("---")
    
    st.markdown("**👥 Credits**")
    st.markdown("""
    **Developed by:**  
    Valerie Le & Alex Goferman  
    MSDS Program, Rutgers University
    
    **Version:** 2.0 | October 2025
    """)
    
    st.markdown("---")
    st.caption("💡 Use the tabs above to navigate")

# Function to generate column names for any charge range
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

def auto_detect_charge_system(df):
    if df is None or len(df) == 0:
        return "5-state", -2, 2
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    if not prob_cols:
        return "5-state", -2, 2
    charges = []
    for col in prob_cols:
        charge_str = col[2:-1]
        try:
            if charge_str.startswith('+'):
                charges.append(int(charge_str[1:]))
            elif charge_str.startswith('-'):
                charges.append(-int(charge_str[1:]))
            else:
                charges.append(int(charge_str))
        except ValueError:
            continue
    if not charges:
        return "5-state", -2, 2
    min_charge = min(charges)
    max_charge = max(charges)
    system_name = f"{max_charge-min_charge+1}-state"
    return system_name, min_charge, max_charge

if "charge_system" not in st.session_state:
    st.session_state.charge_system = "5-state"
    st.session_state.min_charge = -2
    st.session_state.max_charge = 2

if hasattr(st.session_state, 'min_charge') and hasattr(st.session_state, 'max_charge'):
    DEFAULT_COLS = generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge)
else:
    DEFAULT_COLS = generate_charge_columns(-2, 2)
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        [
            ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
            ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ],
        columns=DEFAULT_COLS,
    )

# Main app tabs
current_min = st.session_state.get('min_charge', -2)
current_max = st.session_state.get('max_charge', 2)
charge_range = f"{current_min:+d}…{current_max:+d}" if current_min < 0 else f"0…{current_max:+d}"

st.title(f"🧬 PTM Charge Distribution Analyzer")
st.caption(f"Calculate protein charge distributions with multiple PTM sites | **Active range:** {charge_range}")

tabs = st.tabs(["🏠 Welcome", "📝 Design Input", "📊 Compute & Visualize"])

# Helper function for charge system update
def update_charge_system(new_system, new_min_charge, new_max_charge):
    if (new_system != st.session_state.charge_system or 
        new_min_charge != getattr(st.session_state, 'min_charge', -2) or 
        new_max_charge != getattr(st.session_state, 'max_charge', 2)):
        st.session_state.charge_system = new_system
        st.session_state.min_charge = new_min_charge
        st.session_state.max_charge = new_max_charge
        DEFAULT_COLS = generate_charge_columns(new_min_charge, new_max_charge)
        example_probs_1 = [0.0] * (new_max_charge - new_min_charge + 1)
        example_probs_2 = [0.0] * (new_max_charge - new_min_charge + 1)
        neutral_index = neutral_index_for_range(new_min_charge, new_max_charge)
        example_probs_1[neutral_index] = 1.0
        if new_max_charge >= 1 and new_min_charge <= -1:
            example_probs_2[neutral_index] = 0.6
            if index_for_charge(-1, new_min_charge) >= 0 and index_for_charge(-1, new_min_charge) < len(example_probs_2):
                example_probs_2[index_for_charge(-1, new_min_charge)] = 0.2
            if index_for_charge(1, new_min_charge) >= 0 and index_for_charge(1, new_min_charge) < len(example_probs_2):
                example_probs_2[index_for_charge(1, new_min_charge)] = 0.2
        else:
            example_probs_2[neutral_index] = 1.0
        st.session_state.df = pd.DataFrame([
            ["Site_1", 1] + example_probs_1,
            ["Site_2", 1] + example_probs_2,
        ], columns=DEFAULT_COLS)
        st.rerun()

# Shared helpers (PMF math etc.)
def pmf_with_offset(probs, min_charge):
    arr = np.asarray(probs, dtype=float)
    arr = np.clip(arr, 0.0, 1.0)
    s = arr.sum()
    if s > 0:
        arr = arr / s
    return arr, int(min_charge)

def convolve(a_arr, a_off, b_arr, b_off):
    c_arr = np.convolve(a_arr, b_arr)
    c_off = a_off + b_off
    return c_arr, c_off

def poly_pow(arr, off, n):
    if n == 0:
        return np.array([1.0]), 0
    if n == 1:
        return arr.copy(), off
    if n % 2 == 0:
        half_arr, half_off = poly_pow(arr, off, n // 2)
        return convolve(half_arr, half_off, half_arr, half_off)
    else:
        minus1_arr, minus1_off = poly_pow(arr, off, n - 1)
        return convolve(minus1_arr, minus1_off, arr, off)

def overall_charge_distribution(df, tol=1e-9):
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    charges = []
    for col in prob_cols:
        charge_str = col[2:-1]
        if charge_str.startswith('+'):
            charges.append(int(charge_str[1:]))
        elif charge_str.startswith('-'):
            charges.append(-int(charge_str[1:]))
        else:
            charges.append(int(charge_str))
    min_charge = min(charges)
    max_charge = max(charges)
    total_arr, total_off = np.array([1.0]), 0
    for _, row in df.iterrows():
        if pd.isna(row.get("Copies")):
            continue
        copies = int(row["Copies"])
        if copies <= 0:
            continue
        probs = row[prob_cols].astype(float).fillna(0.0).to_numpy()
        if not np.isclose(probs.sum(), 1.0, atol=1e-6):
            raise ValueError("Found a row with probabilities not summing to 1. Fix input first.")
        base_arr, base_off = pmf_with_offset(probs, min_charge)
        site_arr, site_off = poly_pow(base_arr, base_off, copies)
        total_arr, total_off = convolve(total_arr, total_off, site_arr, site_off)
    s = total_arr.sum()
    if s > 0:
        total_arr = total_arr / s
    total_arr[total_arr < tol] = 0.0
    s2 = total_arr.sum()
    if s2 > 0:
        total_arr = total_arr / s2
    return total_arr, total_off

def window_distribution(arr, off, low=-5, high=+5):
    charges = np.arange(off, off + len(arr))
    mask = (charges >= low) & (charges <= high)
    window = pd.DataFrame({
        "Charge": charges[mask],
        "Probability": arr[mask]
    })
    tail_low = arr[charges < low].sum()
    tail_high = arr[charges > high].sum()
    return window, float(tail_low), float(tail_high)

def create_site_contribution_plot(df):
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    if not prob_cols:
        return None, False
    site_data = df[["Site_ID"] + prob_cols].copy()
    if len(site_data) > 40:
        site_data = site_data.head(40)
        show_warning = True
    else:
        show_warning = False
    fig = px.imshow(
        site_data[prob_cols].values,
        labels=dict(x="Charge State", y="PTM Site", color="Probability"),
        x=prob_cols,
        y=site_data['Site_ID'],
        color_continuous_scale='RdYlBu_r',
        aspect='auto'
    )
    fig.update_layout(
        title='Individual Site Charge Probabilities' + (' (First 40 sites shown)' if show_warning else ''),
        height=max(400, len(site_data) * 20),
        template='plotly_white'
    )
    fig.update_traces(
        hovertemplate='<b>Site:</b> %{y}<br>' +
                     '<b>Charge:</b> %{x}<br>' +
                     '<b>Probability:</b> %{z:.3f}<br>' +
                     '<extra></extra>'
    )
    return fig, show_warning

# -------------------------------
# TAB 0: Welcome / Landing Page
# -------------------------------
with tabs[0]:
    st.markdown("## 👋 Welcome to PTM Charge Distribution Analyzer")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What does this tool do?
        
        This application calculates the **overall charge distribution** of proteins with multiple 
        post-translational modification (PTM) sites. Each PTM site can exist in various charge states 
        with different probabilities, and this tool computes the combined distribution across all sites.
        
        ### 🚀 Quick Start Guide
        
        1. **📝 Design Input Tab**: Enter your PTM sites and their charge probabilities
        2. **📊 Compute Tab**: Calculate and visualize the overall charge distribution
        
        ### ✨ Key Features
        
        - 🎯 Support for **3 to 15 charge states** (from -7 to +7)
        - 📊 **Interactive visualizations** with hover details
        - 🔥 **Site contribution heatmaps** to see individual patterns
        - 📈 **Cumulative distribution functions** for statistical analysis
        - 💾 **Template generation** for quick testing with 100 sites
        """)
    
    with col2:
        st.info("""
        **💡 Pro Tips**
        
        - Use the **Settings bar** in Design tab to change charge ranges
        - **Probability columns** are the heart of this tool - they must sum to 1.0 per row
        - Generate a **100-site template** for testing
        - All plots are **interactive** - hover for details!
        """)
        
        st.success("""
        **🎓 For Scientists**
        
        This tool uses probability generating functions (PGF) and fast convolution 
        to compute exact charge distributions efficiently, even for proteins with 
        100+ PTM sites.
        """)

# -------------------------------
# TAB 1: Design Input
# -------------------------------
with tabs[1]:
    st.markdown("### 📝 Design Your PTM Input")
    
    # Horizontal control bar at the top
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 2, 2, 1])
    
    with ctrl_col1:
        st.markdown("**Charge Range**")
        charge_options = {
            "3-state (-1…+1)": ("3-state", -1, 1),
            "5-state (-2…+2)": ("5-state", -2, 2),
            "7-state (-3…+3)": ("7-state", -3, 3),
            "9-state (-4…+4)": ("9-state", -4, 4),
            "11-state (-5…+5)": ("11-state", -5, 5),
            "15-state (-7…+7)": ("15-state", -7, 7)
        }
        current_display = "5-state (-2…+2)"
        for display_name, (system_name, _, _) in charge_options.items():
            if system_name == st.session_state.charge_system:
                current_display = display_name
                break
        charge_system_selection = st.selectbox(
            "Select range:",
            list(charge_options.keys()),
            index=list(charge_options.keys()).index(current_display),
            key="charge_system_selector_v2",
            label_visibility="collapsed"
        )
        selected_system, min_charge, max_charge = charge_options[charge_system_selection]
        new_system = selected_system
        new_min_charge = min_charge
        new_max_charge = max_charge
        update_charge_system(new_system, new_min_charge, new_max_charge)
    
    with ctrl_col2:
        st.markdown("**Quick Template**")
        if st.button("📋 Generate N=100", key="generate_n100_v2", use_container_width=True):
            template_data = []
            current_min = st.session_state.min_charge
            current_max = st.session_state.max_charge
            charge_range_val = current_max - current_min + 1
            neutral_index = neutral_index_for_range(current_min, current_max)
            for i in range(1, 101):
                site_id = f"Site_{i}"
                copies = 1
                probs = [0.0] * charge_range_val
                if i % 4 == 0:
                    probs[neutral_index] = 0.8
                    idx_minus1 = index_for_charge(-1, current_min)
                    idx_plus1 = index_for_charge(1, current_min)
                    if 0 <= idx_minus1 < charge_range_val:
                        probs[idx_minus1] = 0.1
                    if 0 <= idx_plus1 < charge_range_val:
                        probs[idx_plus1] = 0.1
                elif i % 4 == 1:
                    probs[neutral_index] = 0.6
                    idx_p1 = index_for_charge(1, current_min)
                    idx_p2 = index_for_charge(2, current_min)
                    if 0 <= idx_p1 < charge_range_val:
                        probs[idx_p1] = 0.3
                    if 0 <= idx_p2 < charge_range_val:
                        probs[idx_p2] = 0.1
                    else:
                        probs[neutral_index] += 0.1
                elif i % 4 == 2:
                    probs[neutral_index] = 0.6
                    idx_m1 = index_for_charge(-1, current_min)
                    idx_m2 = index_for_charge(-2, current_min)
                    if 0 <= idx_m1 < charge_range_val:
                        probs[idx_m1] = 0.3
                    if 0 <= idx_m2 < charge_range_val:
                        probs[idx_m2] = 0.1
                    else:
                        probs[neutral_index] += 0.1
                else:
                    probs[neutral_index] = 0.5
                    remaining_prob = 0.5
                    for offset in range(1, min(3, neutral_index + 1, charge_range_val - neutral_index)):
                        prob_each = remaining_prob / (2 * min(2, offset))
                        if neutral_index - offset >= 0:
                            probs[neutral_index - offset] = prob_each
                        if neutral_index + offset < charge_range_val:
                            probs[neutral_index + offset] = prob_each
                        remaining_prob -= 2 * prob_each
                        if remaining_prob <= 0:
                            break
                    probs[neutral_index] += remaining_prob
                template_data.append([site_id, copies] + probs)
            DEFAULT_COLS = generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge)
            template_df = pd.DataFrame(template_data, columns=DEFAULT_COLS)
            st.session_state.df = template_df
            st.rerun()
    
    with ctrl_col3:
        st.markdown("**Dataset Info**")
        n_sites = len(st.session_state.df)
        st.metric("Sites", n_sites, label_visibility="collapsed")
    
    with ctrl_col4:
        st.markdown("**Reset**")
        if st.button("🔄", key="reset_v2", help="Reset to 2 example sites", use_container_width=True):
            DEFAULT_COLS = generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge)
            st.session_state.df = pd.DataFrame([
                ["Site_1", 1] + [0.0] * (st.session_state.max_charge - st.session_state.min_charge + 1),
                ["Site_2", 1] + [0.0] * (st.session_state.max_charge - st.session_state.min_charge + 1),
            ], columns=DEFAULT_COLS)
            neutral_idx = neutral_index_for_range(st.session_state.min_charge, st.session_state.max_charge)
            st.session_state.df.iloc[0, 2 + neutral_idx] = 1.0
            st.session_state.df.iloc[1, 2 + neutral_idx] = 0.6
            if st.session_state.min_charge <= -1:
                st.session_state.df.iloc[1, 2 + index_for_charge(-1, st.session_state.min_charge)] = 0.2
            if st.session_state.max_charge >= 1:
                st.session_state.df.iloc[1, 2 + index_for_charge(1, st.session_state.min_charge)] = 0.2
            st.rerun()
    
    st.markdown("---")
    
    # Show dataset status
    st.markdown("#### 💾 Probability Data Table")
    prob_cols = [col for col in st.session_state.df.columns if col.startswith("P(")]
    temp_df = st.session_state.df.copy()
    if prob_cols:
        temp_df["Prob_Sum"] = temp_df[prob_cols].sum(axis=1)
        n_valid = sum(np.isclose(temp_df["Prob_Sum"].fillna(0), 1.0, atol=1e-6))
    else:
        n_valid = 0
    n_sites = len(st.session_state.df)
    
    if n_valid == n_sites:
        st.success(f"✅ All {n_sites} sites have valid probabilities (sum = 1.0)")
    else:
        st.warning(f"⚠️ {n_sites - n_valid} of {n_sites} sites need adjustment (probabilities must sum to 1.0)")
    
    # Build display with Status and Sum columns
    display_df = st.session_state.df.copy()
    if prob_cols:
        display_df["Prob_Sum"] = display_df[prob_cols].sum(axis=1)
        display_df["Status"] = display_df["Prob_Sum"].apply(lambda x: "✅" if np.isclose(x, 1.0, atol=1e-6) else "❌")
    else:
        display_df["Prob_Sum"] = 0.0
        display_df["Status"] = "❌"

    # Reorder columns: Status first, then base columns, then probabilities, then Sum
    base_cols = [col for col in ["Site_ID", "Copies"] if col in display_df.columns]
    display_cols = ["Status"] + base_cols + prob_cols + ["Prob_Sum"]
    display_df = display_df[display_cols]
    
    # Highlight probability columns
    st.info("💡 **Probability columns** (P(...)) are the core of this tool - ensure each row sums to 1.0!")

    # Editable table with Status and Sum visible but read-only (300px default height)
    edited = st.data_editor(
        display_df,
        use_container_width=True,
        height=300,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.TextColumn("✓", width="small", help="✅ = Valid, ❌ = Invalid"),
            "Site_ID": st.column_config.TextColumn("Site_ID", width="medium"),
            "Copies": st.column_config.NumberColumn("Copies", min_value=1, step=1, width="small"),
            **{col: st.column_config.NumberColumn(
                col, 
                min_value=0.0, 
                max_value=1.0, 
                step=0.01, 
                format="%.3f",
                help="Probability for this charge state"
            ) for col in prob_cols},
            "Prob_Sum": st.column_config.NumberColumn("Sum", format="%.3f", width="small", help="Must equal 1.0")
        },
        hide_index=True,
        disabled=["Status", "Prob_Sum"]
    )

    # Persist edits back (exclude Status and Prob_Sum)
    editable_cols = [col for col in display_df.columns if col not in ("Status", "Prob_Sum")]
    st.session_state.df = edited[editable_cols].copy()

# -------------------------------
# TAB 2: Compute & Visualize
# -------------------------------
with tabs[2]:
    st.markdown("### 📊 Compute & Visualize Distribution")
    
    # Compute button
    run_btn = st.button("▶️ Compute Distribution Now", key="compute_v2", type="primary", use_container_width=False)
    
    df = st.session_state.df.copy()
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    
    # Validation check
    if prob_cols:
        df["Prob_Sum"] = df[prob_cols].sum(axis=1)
        all_valid = np.all(np.isclose(df["Prob_Sum"].fillna(0), 1.0, atol=1e-6))
        if not all_valid:
            st.warning("⚠️ Some rows have probabilities ≠ 1.0 — they'll be auto-normalized for computation")
    else:
        all_valid = False
        st.error("❌ No probability columns found")
    
    if run_btn:
        try:
            df_for_compute = df.copy()
            if prob_cols:
                for idx, row in df_for_compute.iterrows():
                    probs = row[prob_cols].astype(float).fillna(0.0)
                    s = probs.sum()
                    if s <= 0:
                        neutral_idx = neutral_index_for_range(st.session_state.get('min_charge', -2), st.session_state.get('max_charge', 2))
                        probs = pd.Series(0.0, index=prob_cols)
                        probs.iloc[neutral_idx] = 1.0
                    else:
                        probs = probs / s
                    df_for_compute.loc[idx, prob_cols] = probs.values

            pmf_arr, pmf_off = overall_charge_distribution(df_for_compute)
            window_df, tail_low, tail_high = window_distribution(pmf_arr, pmf_off, -5, +5)

            st.success("🎉 Computation completed successfully!")
            
            total_sites = len(df[df['Copies'].notna() & (df['Copies'] > 0)])
            most_likely_charge = window_df.loc[window_df['Probability'].idxmax(), 'Charge']
            max_probability = window_df['Probability'].max()
            central_mass = 1.0 - tail_low - tail_high

            # Colorful metrics in a compact layout
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔬 PTM Sites", total_sites)
            with col2:
                st.metric("⚡ Most Likely Charge", f"{most_likely_charge:+.0f}")
            with col3:
                st.metric("📊 Peak Probability", f"{max_probability:.1%}")
            with col4:
                st.metric("🎯 Central Mass", f"{central_mass:.1%}", help="Probability in [-5,+5] range")

            st.markdown("---")
            
            # Create two columns: plots on left, interpretation on right
            plot_col, guide_col = st.columns([3, 1])
            
            with plot_col:
                st.markdown("### 📊 Interactive Visualizations")
                
                # 1. Combined Distribution + Cumulative Plot
                st.markdown("#### Distribution & Cumulative")
                combined_fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Probability Distribution', 'Cumulative Distribution'),
                    vertical_spacing=0.12,
                    row_heights=[0.6, 0.4]
                )
                
                # Distribution plot (top)
                colors = []
                for charge in window_df['Charge']:
                    if charge < -2:
                        colors.append('#d62728')  # Red
                    elif charge < 0:
                        colors.append('#ff7f0e')  # Orange
                    elif charge == 0:
                        colors.append('#2ca02c')  # Green
                    elif charge <= 2:
                        colors.append('#1f77b4')  # Blue
                    else:
                        colors.append('#9467bd')  # Purple
                
                combined_fig.add_trace(
                    go.Bar(
                        x=window_df['Charge'], 
                        y=window_df['Probability'], 
                        marker_color=colors,
                        name='Probability',
                        hovertemplate='<b>Charge: %{x:+d}</b><br>Probability: %{y:.4f}<extra></extra>'
                    ), 
                    row=1, col=1
                )
                
                # Cumulative plot (bottom)
                cumulative = np.cumsum(window_df['Probability'].values)
                combined_fig.add_trace(
                    go.Scatter(
                        x=window_df['Charge'].values, 
                        y=cumulative, 
                        mode='lines+markers', 
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=6),
                        name='Cumulative',
                        hovertemplate='<b>Up to %{x:+d}</b><br>Cumulative: %{y:.3f}<extra></extra>'
                    ), 
                    row=2, col=1
                )
                
                # Add reference lines to cumulative
                combined_fig.add_hline(y=0.5, line_dash="dash", line_color="gray", row=2, col=1)
                combined_fig.add_hline(y=0.9, line_dash="dot", line_color="orange", row=2, col=1)
                
                combined_fig.update_layout(
                    title_text=f'PTM Charge Analysis ({total_sites} sites)', 
                    showlegend=False, 
                    template='plotly_white', 
                    height=600
                )
                combined_fig.update_xaxes(title_text="Net Charge", row=1, col=1)
                combined_fig.update_xaxes(title_text="Net Charge", row=2, col=1)
                combined_fig.update_yaxes(title_text="Probability", row=1, col=1)
                combined_fig.update_yaxes(title_text="Cumulative Probability", row=2, col=1)
                
                st.plotly_chart(combined_fig, use_container_width=True)
                
                # Results table (compact)
                with st.expander("📋 Detailed probability table"):
                    st.dataframe(window_df, use_container_width=True, height=250)
                    st.caption(f"**Full range:** {pmf_off} to {pmf_off + len(pmf_arr) - 1} | **Tail low:** {tail_low:.1%} | **Tail high:** {tail_high:.1%}")
            
            with guide_col:
                st.markdown("### 📖 Guide")
                with st.expander("📊 Distribution", expanded=True):
                    st.markdown("""
                    **Colors:**
                    - 🔴 Negative
                    - 🟢 Neutral  
                    - 🔵 Positive
                    
                    **Height** = probability
                    """)
                    if abs(most_likely_charge) <= 2:
                        st.success("✅ Moderate")
                    else:
                        st.info("⚡ Significant")
                
                with st.expander("📈 Cumulative", expanded=True):
                    st.markdown("""
                    Shows P(charge ≤ X)
                    
                    - **Steep**: Narrow
                    - **Gradual**: Wide
                    - **50% line**: Median
                    """)
                    if central_mass > 0.5:
                        st.success("🎯 Centered")
                    else:
                        st.info("📈 Extended")
        
        except Exception as e:
            st.error(f"❌ Computation failed: {e}")
            with st.expander("🐛 Error details"):
                st.code(str(e))

# End of app
