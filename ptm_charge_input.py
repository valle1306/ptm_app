import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PTM Charge Input", layout="wide")

charge_range = "−2…+2" if st.session_state.get('charge_system', '5-state') == "5-state" else "−5…+5"
st.title(f"PTM Charge Variant Input ({charge_range})")
st.caption("Enter any number of PTM sites, copies per site, and charge probabilities. Row sums must equal 1. Then compute the overall charge distribution.")

# Help section
with st.expander("📚 How to use this tool", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 What this tool does
        - Calculates the overall charge distribution of proteins with PTM sites
        - Each PTM site can have different charge probabilities
        - Combines multiple sites to predict total protein charge
        
        ### 📝 Input format
        - **Site_ID**: Name your PTM site (e.g., "Ser123", "Thr45")
        - **Copies**: How many copies of this site type (usually 1)
        - **P(-2) to P(+2)**: Probability of each charge state (must sum to 1.0)
        """)
    
    with col2:
        st.markdown("""
        ### 💡 Example scenarios
        **Unmodified site:**
        - P(0) = 1.0, all others = 0.0
        
        **Phosphorylation site (partial):**
        - P(-2) = 0.3 (phosphorylated)
        - P(0) = 0.7 (unmodified)
        
        **Acetylation site:**
        - P(+1) = 0.4 (acetylated, positive)
        - P(0) = 0.6 (unmodified)
        
        ### 🔬 Interpretation
        - Window [-5, +5]: Most biologically relevant charges
        - Tail masses: Extreme charges (usually very low probability)
        """)
    
    st.info("💡 **Pro tip**: Start with templates, then modify probabilities based on your experimental data!")

# -------------------------------
# Data-entry (Task 1 & 2)
# -------------------------------
# Support both 5-state and 11-state charge systems
DEFAULT_COLS_5 = ["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
DEFAULT_COLS_11 = ["Site_ID", "Copies", "P(-5)", "P(-4)", "P(-3)", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)", "P(+3)", "P(+4)", "P(+5)"]

# Auto-detect charge system based on session state or use 5-state as default
if "charge_system" not in st.session_state:
    st.session_state.charge_system = "5-state"  # Default to 5-state

DEFAULT_COLS = DEFAULT_COLS_5 if st.session_state.charge_system == "5-state" else DEFAULT_COLS_11
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        [
            ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
            ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ],
        columns=DEFAULT_COLS,
    )

with st.sidebar:
    st.header("Data Input Options")
    
    # Charge system selector
    st.subheader("⚙️ Charge System")
    charge_system = st.radio(
        "Select charge range:",
        ["5-state (-2 to +2)", "11-state (-5 to +5)"],
        index=0 if st.session_state.charge_system == "5-state" else 1,
        key="charge_system_selector",
        help="5-state: Standard PTM analysis | 11-state: Extended range for stress testing"
    )
    
    # Update charge system and columns
    new_system = "5-state" if "5-state" in charge_system else "11-state"
    if new_system != st.session_state.charge_system:
        st.session_state.charge_system = new_system
        DEFAULT_COLS = DEFAULT_COLS_5 if new_system == "5-state" else DEFAULT_COLS_11
        
        # Reset dataframe when switching systems
        if new_system == "5-state":
            st.session_state.df = pd.DataFrame([
                ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
                ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
            ], columns=DEFAULT_COLS_5)
        else:
            st.session_state.df = pd.DataFrame([
                ["Site_1", 1, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ["Site_2", 1, 0.0, 0.0, 0.0, 0.0, 0.2, 0.6, 0.2, 0.0, 0.0, 0.0, 0.0],
            ], columns=DEFAULT_COLS_11)
        st.rerun()
    
    DEFAULT_COLS = DEFAULT_COLS_5 if st.session_state.charge_system == "5-state" else DEFAULT_COLS_11
    
    # File upload section
    st.subheader("📁 Upload CSV File")
    uploaded_file = st.file_uploader(
        "Upload existing PTM data (CSV format)", 
        type=['csv'],
        help=f"CSV should have columns for {st.session_state.charge_system} system",
        key="csv_uploader"
    )
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            
            # Validate columns
            required_cols = set(DEFAULT_COLS)
            uploaded_cols = set(uploaded_df.columns)
            
            if required_cols.issubset(uploaded_cols):
                # Auto-detect charge system from uploaded file
                if len(uploaded_cols.intersection(set(DEFAULT_COLS_11))) > len(uploaded_cols.intersection(set(DEFAULT_COLS_5))):
                    detected_system = "11-state"
                    st.session_state.charge_system = "11-state"
                    DEFAULT_COLS = DEFAULT_COLS_11
                    st.info("🔍 Detected 11-state charge system from uploaded file")
                else:
                    detected_system = "5-state"
                    st.info("🔍 Detected 5-state charge system from uploaded file")
                
                # Ensure numeric columns are properly typed
                numeric_cols = ["Copies"] + [col for col in DEFAULT_COLS if col.startswith("P(")]
                for col in numeric_cols:
                    if col in uploaded_df.columns:
                        uploaded_df[col] = pd.to_numeric(uploaded_df[col], errors='coerce')
                
                # Show preview first
                st.info(f"Preview: {len(uploaded_df)} rows found")
                st.dataframe(uploaded_df.head(), use_container_width=True)
                
                # Two options: button click or automatic loading
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Load uploaded data", key="load_csv_data"):
                        st.session_state.df = uploaded_df[DEFAULT_COLS].copy()
                        st.success(f"✅ Loaded {len(uploaded_df)} rows from {uploaded_file.name}")
                        st.rerun()
                
                with col_b:
                    # Auto-load option
                    if st.checkbox("Auto-load when file changes", key="auto_load_csv"):
                        # Create a unique key based on file content to detect changes
                        file_hash = hash(str(uploaded_df.values.tobytes()))
                        if f"last_file_hash" not in st.session_state or st.session_state.last_file_hash != file_hash:
                            st.session_state.df = uploaded_df[DEFAULT_COLS].copy()
                            st.session_state.last_file_hash = file_hash
                            st.success(f"🔄 Auto-loaded {len(uploaded_df)} rows from {uploaded_file.name}")
                            st.rerun()
                    
            else:
                missing_cols = required_cols - uploaded_cols
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                st.info("Required columns: " + ", ".join(DEFAULT_COLS))
                
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
            st.error("Please check that your CSV file is properly formatted.")
    
    st.markdown("---")
    st.subheader("📝 Manual Entry Controls")
    add_rows = st.number_input("Add blank rows", min_value=0, max_value=100, value=0, step=1)
    if st.button("Insert", key="insert_blank_rows"):
        new = pd.DataFrame([["", 1, 0, 0, 1, 0, 0] for _ in range(add_rows)], columns=DEFAULT_COLS)
        st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
        st.success(f"Added {add_rows} blank rows")

    # Quick templates section
    st.subheader("🚀 Quick Start Templates")
    
    template_col1, template_col2 = st.columns(2)
    
    with template_col1:
        if st.button("📊 Generate N=100 template", key="generate_n100_template"):
            template_data = []
            for i in range(1, 101):
                site_id = f"Site_{i}"
                copies = 1
                
                if i % 4 == 0:  # Neutral dominant
                    probs = [0.0, 0.1, 0.8, 0.1, 0.0]
                elif i % 4 == 1:  # Slightly positive bias
                    probs = [0.0, 0.0, 0.6, 0.3, 0.1]
                elif i % 4 == 2:  # Slightly negative bias
                    probs = [0.1, 0.3, 0.6, 0.0, 0.0]
                else:  # Balanced
                    probs = [0.05, 0.2, 0.5, 0.2, 0.05]
                
                template_data.append([site_id, copies] + probs)
            
            template_df = pd.DataFrame(template_data, columns=DEFAULT_COLS)
            st.session_state.df = template_df
            st.success("✅ Generated N=100 template with varied probability patterns")
            st.rerun()
    
    with template_col2:
        template_type = st.selectbox(
            "Common site types:",
            ["Neutral sites only", "Acidic sites (negative)", "Basic sites (positive)", "Mixed population"],
            key="template_selector"
        )
        
        n_sites = st.number_input("Number of sites:", min_value=1, max_value=200, value=10, key="template_n_sites")
        
        if st.button("Generate custom template", key="generate_custom_template"):
            template_data = []
            for i in range(1, n_sites + 1):
                site_id = f"Site_{i}"
                copies = 1
                
                if st.session_state.charge_system == "5-state":
                    if template_type == "Neutral sites only":
                        probs = [0.0, 0.0, 1.0, 0.0, 0.0]  # All neutral
                    elif template_type == "Acidic sites (negative)":
                        probs = [0.2, 0.6, 0.2, 0.0, 0.0]  # Negative bias
                    elif template_type == "Basic sites (positive)":
                        probs = [0.0, 0.0, 0.2, 0.6, 0.2]  # Positive bias
                    else:  # Mixed population
                        if i % 3 == 0:
                            probs = [0.1, 0.4, 0.5, 0.0, 0.0]  # Acidic
                        elif i % 3 == 1:
                            probs = [0.0, 0.0, 0.5, 0.4, 0.1]  # Basic
                        else:
                            probs = [0.0, 0.1, 0.8, 0.1, 0.0]  # Neutral
                else:  # 11-state system
                    if template_type == "Neutral sites only":
                        probs = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # All neutral
                    elif template_type == "Acidic sites (negative)":
                        probs = [0.1, 0.2, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0]  # Negative bias
                    elif template_type == "Basic sites (positive)":
                        probs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.2, 0.3, 0.2, 0.1]  # Positive bias
                    else:  # Mixed population
                        if i % 3 == 0:
                            probs = [0.05, 0.1, 0.2, 0.3, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0]  # Acidic
                        elif i % 3 == 1:
                            probs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.25, 0.3, 0.2, 0.1, 0.05]  # Basic
                        else:
                            probs = [0.0, 0.0, 0.05, 0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.0, 0.0]  # Neutral
                
                template_data.append([site_id, copies] + probs)
            
            template_df = pd.DataFrame(template_data, columns=DEFAULT_COLS)
            st.session_state.df = template_df
            st.success(f"✅ Generated {n_sites} {template_type.lower()}")
            st.rerun()

    st.markdown("---")
    st.header("Download (input)")
    fname_base = st.text_input("Base filename (no extension)", value="ptm_input")
    tol = float(st.text_input("Row-sum tolerance", value="1e-6"))

tabs = st.tabs(["📝 Input table", "🧮 Compute distribution"])

# Show current dataset status with health check
n_sites = len(st.session_state.df)
prob_cols = [col for col in DEFAULT_COLS if col.startswith("P(")]
temp_df = st.session_state.df.copy()
temp_df["Prob_Sum"] = temp_df[prob_cols].sum(axis=1)
n_valid = sum(np.isclose(temp_df["Prob_Sum"].fillna(0), 1.0, atol=1e-6))

status_col1, status_col2 = st.columns([3, 1])
with status_col1:
    if n_valid == n_sites:
        st.success(f"✅ Dataset ready: {n_sites} PTM sites, all valid")
    else:
        st.warning(f"⚠️ Dataset: {n_sites} PTM sites, {n_valid} valid, {n_sites-n_valid} need fixing")

with status_col2:
    if st.button("🔄 Reset to default", key="reset_data", help="Start over with 2 example sites"):
        if st.session_state.charge_system == "5-state":
            st.session_state.df = pd.DataFrame([
                ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
                ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
            ], columns=DEFAULT_COLS_5)
        else:
            st.session_state.df = pd.DataFrame([
                ["Site_1", 1, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ["Site_2", 1, 0.0, 0.0, 0.0, 0.0, 0.2, 0.6, 0.2, 0.0, 0.0, 0.0, 0.0],
            ], columns=DEFAULT_COLS_11)
        st.rerun()

with tabs[0]:
    # Calculate validation info
    prob_cols = [col for col in DEFAULT_COLS if col.startswith("P(")]
    display_df = st.session_state.df.copy()
    display_df["Prob_Sum"] = display_df[prob_cols].sum(axis=1)
    display_df["Status"] = display_df["Prob_Sum"].apply(
        lambda x: "✅" if np.isclose(x, 1.0, atol=tol) else "❌"
    )
    
    # Reorder columns to show Status first for visibility
    display_cols = ["Status"] + DEFAULT_COLS + ["Prob_Sum"]
    display_df = display_df[display_cols]
    
    edited = st.data_editor(
        display_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.TextColumn("✓", width="small", help="✅ = Valid row, ❌ = Invalid row"),
            **{"Site_ID": st.column_config.TextColumn("Site_ID"),
               "Copies": st.column_config.NumberColumn("Copies", min_value=1, step=1)},
            **{col: st.column_config.NumberColumn(col, min_value=0.0, max_value=1.0, step=0.001, format="%.3f") 
               for col in DEFAULT_COLS if col.startswith("P(")},
            "Prob_Sum": st.column_config.NumberColumn("Sum", format="%.3f", help="Sum of all probability columns")
        },
        hide_index=True,
        disabled=["Status", "Prob_Sum"]  # Make status and sum read-only
    )
    
    # Extract only the editable columns back to session state
    st.session_state.df = edited[DEFAULT_COLS].copy()

    # Validation with helpful guidance and enhanced display
    current_df = st.session_state.df.copy()
    current_df["Prob_Sum"] = current_df[prob_cols].sum(axis=1)
    current_df["Valid_Row"] = np.isclose(current_df["Prob_Sum"], 1.0, atol=tol)

    bad_rows = current_df.index[~current_df["Valid_Row"]].tolist()
    if len(bad_rows) == 0:
        st.success("✅ All rows valid (probability sums = 1 within tolerance).")
    else:
        st.error(f"⚠️ {len(bad_rows)} row(s) have probability sums ≠ 1 (tolerance: ±{tol})")
        st.info("🔍 **Invalid rows show ❌ in the Status column** - look for the red X marks in the first column")
        
        with st.expander("🔧 Need help fixing probability rows?", expanded=True):
            st.markdown("""
            **Each row's probabilities must sum to exactly 1.0**
            
            **Visual cues in the table above:**
            - ✅ **Valid rows**: Green checkmark in Status column
            - ❌ **Invalid rows**: Red X in Status column
            - **Sum column**: Shows the actual sum of probabilities
            
            **Common issues:**
            - Probabilities sum to more than 1 (e.g., 0.3 + 0.4 + 0.5 = 1.2) ❌
            - Probabilities sum to less than 1 (e.g., 0.2 + 0.3 + 0.3 = 0.8) ❌
            
            **Quick fixes:**
            - Use decimals that add to 1: `0.1 + 0.2 + 0.4 + 0.2 + 0.1 = 1.0` ✅
            - For neutral sites: set P(0) = 1.0, others = 0.0 ✅
            - For charged sites: distribute probabilities (e.g., P(-1)=0.3, P(0)=0.7) ✅
            """)
            
            # Show which specific rows are problematic with their actual sums
            if len(bad_rows) <= 10:  # Only show if not too many
                problem_rows = current_df.loc[bad_rows, ["Site_ID"] + prob_cols + ["Prob_Sum"]].copy()
                problem_rows["Error"] = problem_rows["Prob_Sum"] - 1.0
                st.markdown("**❌ Problematic rows (from table above):**")
                st.dataframe(
                    problem_rows.style.format({"Prob_Sum": "{:.3f}", "Error": "{:+.3f}"}),
                    use_container_width=True
                )

    st.subheader("Preview (with validation)")
    st.dataframe(edited, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        csv_bytes = edited[DEFAULT_COLS].to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV (input)", data=csv_bytes, file_name=f"{fname_base}.csv",
                           mime="text/csv", disabled=len(bad_rows)>0)

    with col2:
        xlsx_buf = io.BytesIO()
        with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
            edited[DEFAULT_COLS].to_excel(writer, index=False, sheet_name="PTM_Input")
        st.download_button("Download Excel (.xlsx, input)", data=xlsx_buf.getvalue(),
                           file_name=f"{fname_base}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           disabled=len(bad_rows)>0)

# -------------------------------
# Helpers for Task 3 (PGF/PMF math)
# -------------------------------
def pmf_with_offset(probs, min_charge):
    """
    Build (array, offset) representation.
    probs: 1D numpy array of probabilities over consecutive integer charges.
    min_charge: integer value corresponding to index 0.
    Returns: (arr, offset) where offset = min_charge
    """
    arr = np.asarray(probs, dtype=float)
    arr = np.clip(arr, 0.0, 1.0)
    s = arr.sum()
    if s > 0:  # normalize robustly
        arr = arr / s
    return arr, int(min_charge)

def convolve(a_arr, a_off, b_arr, b_off):
    """Convolution for arrays with offsets. Returns (c_arr, c_off)."""
    c_arr = np.convolve(a_arr, b_arr)
    c_off = a_off + b_off
    return c_arr, c_off

def poly_pow(arr, off, n):
    """Exponentiation by squaring for PMF arrays with offsets."""
    if n == 0:
        return np.array([1.0]), 0  # neutral element (charge 0 with prob 1)
    if n == 1:
        return arr.copy(), off
    # fast power
    if n % 2 == 0:
        half_arr, half_off = poly_pow(arr, off, n // 2)
        return convolve(half_arr, half_off, half_arr, half_off)
    else:
        minus1_arr, minus1_off = poly_pow(arr, off, n - 1)
        return convolve(minus1_arr, minus1_off, arr, off)

def overall_charge_distribution(df, tol=1e-9):
    """
    df: DataFrame with columns Site_ID, Copies, P(charge_states).
    Returns: (pmf_arr, offset) normalized.
    Supports both 5-state (-2 to +2) and 11-state (-5 to +5) charge systems.
    """
    # Auto-detect charge system from dataframe columns
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    
    # Determine charge range from column names
    charges = []
    for col in prob_cols:
        charge_str = col[2:-1]  # Extract charge from P(charge) format
        if charge_str.startswith('+'):
            charges.append(int(charge_str[1:]))
        elif charge_str.startswith('-'):
            charges.append(-int(charge_str[1:]))
        else:
            charges.append(int(charge_str))
    
    min_charge = min(charges)
    max_charge = max(charges)

    # Start with delta at 0 charge
    total_arr, total_off = np.array([1.0]), 0

    for _, row in df.iterrows():
        # Skip empty rows or invalid ones
        if pd.isna(row.get("Copies")):
            continue
        copies = int(row["Copies"])
        if copies <= 0:
            continue

        probs = row[prob_cols].astype(float).fillna(0.0).to_numpy()
        # Only proceed if row sums ~ 1
        if not np.isclose(probs.sum(), 1.0, atol=1e-6):
            raise ValueError("Found a row with probabilities not summing to 1. Fix input first.")

        # Row PMF spans the detected charge range
        base_arr, base_off = pmf_with_offset(probs, min_charge)

        # Raise to 'copies'
        site_arr, site_off = poly_pow(base_arr, base_off, copies)

        # Convolve into total
        total_arr, total_off = convolve(total_arr, total_off, site_arr, site_off)

    # Normalize (floating drift)
    s = total_arr.sum()
    if s > 0:
        total_arr = total_arr / s

    # Prune tiny numerical noise
    total_arr[total_arr < tol] = 0.0
    # Re-normalize after pruning
    s2 = total_arr.sum()
    if s2 > 0:
        total_arr = total_arr / s2

    return total_arr, total_off

def window_distribution(arr, off, low=-5, high=+5):
    """Extract window [low, high] and tail masses."""
    charges = np.arange(off, off + len(arr))
    mask = (charges >= low) & (charges <= high)
    window = pd.DataFrame({
        "Charge": charges[mask],
        "Probability": arr[mask]
    })
    tail_low = arr[charges < low].sum()
    tail_high = arr[charges > high].sum()
    return window, float(tail_low), float(tail_high)

# -------------------------------
# Task 3 UI
# -------------------------------
with tabs[1]:
    st.subheader("Compute overall protein charge distribution")
    run_btn = st.button("Compute distribution now", key="compute_distribution")

    # Use the latest edited table
    df = st.session_state.df.copy()

    # Validate first
    prob_cols = [col for col in DEFAULT_COLS if col.startswith("P(")]
    df["Prob_Sum"] = df[prob_cols].sum(axis=1)
    all_valid = np.all(np.isclose(df["Prob_Sum"].fillna(0), 1.0, atol=tol))
    if not all_valid:
        st.error("Fix input rows so each probability row sums to 1 before computing.")
    elif run_btn:
        try:
            pmf_arr, pmf_off = overall_charge_distribution(df)
            window_df, tail_low, tail_high = window_distribution(pmf_arr, pmf_off, -5, +5)

            st.success("🎉 Computation completed successfully!")
            
            # Results interpretation
            total_sites = len(df[df['Copies'].notna() & (df['Copies'] > 0)])
            most_likely_charge = window_df.loc[window_df['Probability'].idxmax(), 'Charge']
            max_probability = window_df['Probability'].max()
            
            # Summary metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("PTM Sites", total_sites)
            with col2:
                st.metric("Most Likely Charge", f"{most_likely_charge:+.0f}")
            with col3:
                st.metric("Peak Probability", f"{max_probability:.1%}")
            with col4:
                central_mass = 1.0 - tail_low - tail_high
                st.metric("Mass in [-5,+5]", f"{central_mass:.1%}")
            
            # Technical details in expander
            with st.expander("🔬 Technical Details", expanded=False):
                st.markdown(f"**Full support range:** {pmf_off} to {pmf_off + len(pmf_arr) - 1}")
                st.markdown(f"**Tail mass below −5:** {tail_low:.6g} ({tail_low:.1%})")
                st.markdown(f"**Tail mass above +5:** {tail_high:.6g} ({tail_high:.1%})")
                if total_sites >= 50:
                    st.info("ℹ️ With many PTM sites, most probability mass is in the tails due to the Central Limit Theorem")
            
            # Results interpretation guide
            with st.expander("📊 How to interpret these results", expanded=False):
                if central_mass > 0.5:
                    st.success("🎯 **Good news!** Most probability (>50%) is in the biologically relevant range [-5, +5]")
                else:
                    st.info("📈 **Note:** Most probability is in the tail regions. This is normal for proteins with many PTM sites.")
                
                if abs(most_likely_charge) <= 2:
                    st.markdown("✅ **Most likely charge is moderate** - protein likely behaves predictably")
                else:
                    st.markdown("⚡ **Most likely charge is significant** - protein may have altered behavior")
            
            st.dataframe(window_df, use_container_width=True)

            # Enhanced downloads with metadata
            st.subheader("📥 Download Results")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                csv_bytes = window_df.to_csv(index=False).encode("utf-8")
                st.download_button("📊 Window [-5,+5] CSV", data=csv_bytes,
                                   file_name=f"ptm_charge_window_{total_sites}sites.csv", 
                                   mime="text/csv",
                                   help="Biologically relevant charge range")
            
            with c2:
                # Enhanced Excel with multiple sheets
                full_df = pd.DataFrame({
                    "Charge": np.arange(pmf_off, pmf_off + len(pmf_arr)),
                    "Probability": pmf_arr
                })
                
                # Create summary sheet
                import datetime
                summary_df = pd.DataFrame({
                    "Parameter": ["Analysis Date", "Total PTM Sites", "Most Likely Charge", 
                                 "Peak Probability", "Mass in [-5,+5]", "Tail Mass (<-5)", "Tail Mass (>+5)"],
                    "Value": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                             total_sites, most_likely_charge, f"{max_probability:.4f}",
                             f"{central_mass:.4f}", f"{tail_low:.6f}", f"{tail_high:.6f}"]
                })
                
                xlsx_buf = io.BytesIO()
                with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Summary")
                    window_df.to_excel(writer, index=False, sheet_name="Window_Distribution")
                    full_df.to_excel(writer, index=False, sheet_name="Full_Distribution")
                    df[DEFAULT_COLS].to_excel(writer, index=False, sheet_name="Input_Data")
                
                st.download_button("📋 Complete Report (Excel)", data=xlsx_buf.getvalue(),
                                   file_name=f"ptm_analysis_report_{total_sites}sites.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   help="Full analysis with input data, results, and summary")
            
            with c3:
                # Quick summary for copying
                summary_text = f"""PTM Charge Analysis Summary
Sites: {total_sites}
Most Likely Charge: {most_likely_charge:+.0f}
Peak Probability: {max_probability:.1%}
Mass in [-5,+5]: {central_mass:.1%}
Analysis Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}"""
                
                st.download_button("📝 Summary Text", data=summary_text.encode(),
                                   file_name=f"ptm_summary_{total_sites}sites.txt",
                                   mime="text/plain",
                                   help="Quick summary for lab notebooks")
        except Exception as e:
            st.error(f"Computation failed: {e}")

st.caption("Tip: You can later extend input columns to 11 states (−5…+5). The computation tab will still work — just adjust the base PMF and offset.")
