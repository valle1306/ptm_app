import io
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="PTM Charge Input", layout="wide")

current_min = st.session_state.get('min_charge', -2)
current_max = st.session_state.get('max_charge', 2)
charge_range = f"{current_min:+d}…{current_max:+d}" if current_min < 0 else f"0…{current_max:+d}"
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
    
    st.info("Pro tip: Start with templates, then modify probabilities based on your experimental data.")

# -------------------------------
# Data-entry (Task 1 & 2)
# -------------------------------
# Function to generate column names for any charge range
def generate_charge_columns(min_charge, max_charge):
    """Generate column names for a given charge range."""
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

# Helper utilities
def index_for_charge(charge, min_charge):
    """Return column index (0-based) for a given integer charge value relative to min_charge."""
    return int(charge - min_charge)

def neutral_index_for_range(min_charge, max_charge):
    """Return the index corresponding to the charge closest to 0 within [min_charge, max_charge].
    If 0 is present, that index is returned. Otherwise the index for the charge with smallest
    absolute value is returned (e.g. for -7..-1 this returns index for -1).
    """
    # If 0 in range use it
    if min_charge <= 0 <= max_charge:
        return index_for_charge(0, min_charge)
    # Otherwise choose charge closest to zero
    candidate = min(range(min_charge, max_charge + 1), key=lambda x: abs(x))
    return index_for_charge(candidate, min_charge)

# Function to auto-detect charge system from existing data
def auto_detect_charge_system(df):
    """Auto-detect the charge system from DataFrame columns."""
    if df is None or len(df) == 0:
        return "5-state", -2, 2
    
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    if not prob_cols:
        return "5-state", -2, 2
    
    charges = []
    for col in prob_cols:
        charge_str = col[2:-1]  # Extract charge from P(charge) format
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
    range_size = max_charge - min_charge + 1
    
    # Generate system name
    system_name = f"{range_size}-state"
    return system_name, min_charge, max_charge

# Initialize charge system
if "charge_system" not in st.session_state:
    st.session_state.charge_system = "5-state"
    st.session_state.min_charge = -2
    st.session_state.max_charge = 2

# Generate default columns based on current charge system
if hasattr(st.session_state, 'min_charge') and hasattr(st.session_state, 'max_charge'):
    DEFAULT_COLS = generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge)
else:
    DEFAULT_COLS = generate_charge_columns(-2, 2)  # fallback
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
    
    # Charge system selector with more options
    st.subheader("Charge System")
    
    # Enhanced charge system options
    charge_options = {
        "3-state (-1 to +1)": ("3-state", -1, 1),
        "5-state (-2 to +2)": ("5-state", -2, 2), 
        "7-state (-3 to +3)": ("7-state", -3, 3),
        "9-state (-4 to +4)": ("9-state", -4, 4),
        "11-state (-5 to +5)": ("11-state", -5, 5),
        "15-state (-7 to +7)": ("15-state", -7, 7),
        "Auto-detect from data": ("auto", None, None)
    }
    
    # Default selection based on current state
    current_display = "5-state (-2 to +2)"  # default
    for display_name, (system_name, _, _) in charge_options.items():
        if system_name == st.session_state.charge_system:
            current_display = display_name
            break
    
    charge_system_selection = st.selectbox(
        "Select charge range:",
        list(charge_options.keys()),
        index=list(charge_options.keys()).index(current_display),
        key="charge_system_selector",
        help="Choose charge range or auto-detect from your data. Larger ranges support more extreme PTM scenarios."
    )
    
    selected_system, min_charge, max_charge = charge_options[charge_system_selection]
    
    # Handle auto-detection or system change
    if selected_system == "auto":
        # Auto-detect from current data
        detected_system, detected_min, detected_max = auto_detect_charge_system(st.session_state.df)
        new_system = detected_system
        new_min_charge = detected_min
        new_max_charge = detected_max
        st.info(f"🔍 Auto-detected: {new_system} ({new_min_charge} to {new_max_charge})")
    else:
        new_system = selected_system
        new_min_charge = min_charge
        new_max_charge = max_charge
    
    # Update charge system if changed
    if (new_system != st.session_state.charge_system or 
        new_min_charge != getattr(st.session_state, 'min_charge', -2) or 
        new_max_charge != getattr(st.session_state, 'max_charge', 2)):
        
        st.session_state.charge_system = new_system
        st.session_state.min_charge = new_min_charge
        st.session_state.max_charge = new_max_charge
        
        # Generate new default columns
        DEFAULT_COLS = generate_charge_columns(new_min_charge, new_max_charge)
        
        # Reset dataframe when switching systems (only if not auto-detecting)
        if selected_system != "auto":
            # Create neutral and slightly charged examples
            example_probs_1 = [0.0] * (new_max_charge - new_min_charge + 1)
            example_probs_2 = [0.0] * (new_max_charge - new_min_charge + 1)
            
            # Set neutral (charge 0) to 1.0 for first site
            neutral_index = neutral_index_for_range(new_min_charge, new_max_charge)
            example_probs_1[neutral_index] = 1.0
            
            # Set balanced distribution for second site
            if new_max_charge >= 1 and new_min_charge <= -1:
                example_probs_2[neutral_index] = 0.6  # P(0) = 0.6
                # set nearest neighbors only if they exist in the range
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
    
    # Update DEFAULT_COLS for current session
    DEFAULT_COLS = generate_charge_columns(st.session_state.min_charge, st.session_state.max_charge)
    
    st.markdown("---")

    # Table display size (users can adjust height for easier editing)
    table_height = st.number_input("Table height (px)", min_value=200, max_value=1200, value=500, step=50, key="table_height")

    # Compact quick actions: N=100 generator + Insert N blank rows
    st.subheader("Quick Start")
    quick_left, quick_right = st.columns([2, 1])

    with quick_left:
        if st.button("Generate N=100 template", key="generate_n100_template"):
            template_data = []
            current_min = st.session_state.min_charge
            current_max = st.session_state.max_charge
            charge_range = current_max - current_min + 1
            neutral_index = neutral_index_for_range(current_min, current_max)

            for i in range(1, 101):
                site_id = f"Site_{i}"
                copies = 1
                probs = [0.0] * charge_range

                if i % 4 == 0:  # Neutral dominant
                    probs[neutral_index] = 0.8  # center
                    idx_minus1 = index_for_charge(-1, current_min)
                    idx_plus1 = index_for_charge(1, current_min)
                    if 0 <= idx_minus1 < charge_range:
                        probs[idx_minus1] = 0.1
                    if 0 <= idx_plus1 < charge_range:
                        probs[idx_plus1] = 0.1

                elif i % 4 == 1:  # Slightly positive bias
                    probs[neutral_index] = 0.6  # center
                    idx_p1 = index_for_charge(1, current_min)
                    idx_p2 = index_for_charge(2, current_min)
                    if 0 <= idx_p1 < charge_range:
                        probs[idx_p1] = 0.3
                    if 0 <= idx_p2 < charge_range:
                        probs[idx_p2] = 0.1
                    else:
                        probs[neutral_index] += 0.1

                elif i % 4 == 2:  # Slightly negative bias
                    probs[neutral_index] = 0.6  # center
                    idx_m1 = index_for_charge(-1, current_min)
                    idx_m2 = index_for_charge(-2, current_min)
                    if 0 <= idx_m1 < charge_range:
                        probs[idx_m1] = 0.3
                    if 0 <= idx_m2 < charge_range:
                        probs[idx_m2] = 0.1
                    else:
                        probs[neutral_index] += 0.1

                else:  # Balanced
                    probs[neutral_index] = 0.5  # P(0)
                    remaining_prob = 0.5
                    for offset in range(1, min(3, neutral_index + 1, charge_range - neutral_index)):
                        prob_each = remaining_prob / (2 * min(2, offset))
                        if neutral_index - offset >= 0:
                            probs[neutral_index - offset] = prob_each
                        if neutral_index + offset < charge_range:
                            probs[neutral_index + offset] = prob_each
                        remaining_prob -= 2 * prob_each
                        if remaining_prob <= 0:
                            break
                    probs[neutral_index] += remaining_prob

                template_data.append([site_id, copies] + probs)

            template_df = pd.DataFrame(template_data, columns=DEFAULT_COLS)
            st.session_state.df = template_df
            st.success("✅ Generated N=100 template with varied probability patterns")
            st.rerun()

    with quick_right:
        add_rows = st.number_input("Insert blank rows", min_value=0, max_value=100, value=0, step=1, key="add_rows_compact")
        if st.button("Insert", key="insert_blank_rows"):
            current_min = st.session_state.get('min_charge', -2)
            current_max = st.session_state.get('max_charge', 2)
            charge_range = current_max - current_min + 1
            neutral_index = neutral_index_for_range(current_min, current_max)

            blank_probs = [0.0] * charge_range
            blank_probs[neutral_index] = 1.0

            new_rows = []
            for _ in range(add_rows):
                new_rows.append(["", 1] + blank_probs)

            new = pd.DataFrame(new_rows, columns=DEFAULT_COLS)
            st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
            st.success(f"Added {add_rows} blank rows")

    # Templates & advanced options (collapsed)
    with st.expander("Templates & advanced", expanded=False):
        template_type = st.selectbox(
            "Template type",
            ["Neutral sites only", "Acidic sites (negative)", "Basic sites (positive)", "Mixed population"],
            key="template_selector"
        )
        n_sites = st.number_input("Number of sites:", min_value=1, max_value=200, value=10, key="template_n_sites")
        if st.button("Generate custom template", key="generate_custom_template"):
            template_data = []
            current_min = st.session_state.min_charge
            current_max = st.session_state.max_charge
            charge_range = current_max - current_min + 1
            neutral_index = -current_min  # Index for charge 0

            for i in range(1, n_sites + 1):
                site_id = f"Site_{i}"
                copies = 1
                probs = [0.0] * charge_range

                if template_type == "Neutral sites only":
                    probs[neutral_index] = 1.0
                elif template_type == "Acidic sites (negative)":
                    if current_min <= -2:
                        probs[0] = 0.2
                        if 0 <= index_for_charge(-1, current_min) < charge_range:
                            probs[index_for_charge(-1, current_min)] = 0.6
                        probs[neutral_index] = 0.2
                    else:
                        if current_min <= -1:
                            idx_m1 = index_for_charge(-1, current_min)
                            if 0 <= idx_m1 < charge_range:
                                probs[idx_m1] = 0.8
                            probs[neutral_index] = 0.2
                        else:
                            probs[neutral_index] = 1.0
                elif template_type == "Basic sites (positive)":
                    if current_max >= 2:
                        idx_p2 = index_for_charge(2, current_min)
                        idx_p1 = index_for_charge(1, current_min)
                        if 0 <= idx_p2 < charge_range:
                            probs[idx_p2] = 0.2
                        if 0 <= idx_p1 < charge_range:
                            probs[idx_p1] = 0.6
                        probs[neutral_index] = 0.2
                    else:
                        if current_max >= 1:
                            idx_p1 = index_for_charge(1, current_min)
                            if 0 <= idx_p1 < charge_range:
                                probs[idx_p1] = 0.8
                            probs[neutral_index] = 0.2
                        else:
                            probs[neutral_index] = 1.0
                else:  # Mixed
                    if i % 3 == 0:
                        if current_min <= -1:
                            probs[neutral_index - 1] = 0.4
                            probs[neutral_index] = 0.5
                            if current_min <= -2:
                                probs[neutral_index - 2] = 0.1
                        else:
                            probs[neutral_index] = 1.0
                    elif i % 3 == 1:
                        if current_max >= 1:
                            probs[neutral_index + 1] = 0.4
                            probs[neutral_index] = 0.5
                            if current_max >= 2:
                                probs[neutral_index + 2] = 0.1
                        else:
                            probs[neutral_index] = 1.0
                    else:
                        probs[neutral_index] = 0.8
                        if current_min <= -1:
                            idx_m1 = index_for_charge(-1, current_min)
                            if 0 <= idx_m1 < charge_range:
                                probs[idx_m1] = 0.1
                        if current_max >= 1:
                            idx_p1 = index_for_charge(1, current_min)
                            if 0 <= idx_p1 < charge_range:
                                probs[idx_p1] = 0.1

                template_data.append([site_id, copies] + probs)

            template_df = pd.DataFrame(template_data, columns=DEFAULT_COLS)
            st.session_state.df = template_df
            st.success(f"✅ Generated {n_sites} {template_type.lower()}")
            st.rerun()

    # Export & downloads (collapsed into one expander for simplicity)
    with st.expander("Export & downloads", expanded=False):
        fname_base = st.text_input("Base filename", value="ptm_input")
        tol = float(st.text_input("Row-sum tolerance", value="1e-6"))

        st.markdown("Download current input or a template from here.")
        try:
            df_for_download = st.session_state.get('df', pd.DataFrame())
            if not df_for_download.empty:
                csv_bytes = df_for_download[DEFAULT_COLS].to_csv(index=False).encode('utf-8')
                st.download_button("Download input CSV", data=csv_bytes, file_name=f"{fname_base}.csv", mime="text/csv")

                xlsx_buf = io.BytesIO()
                with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
                    df_for_download[DEFAULT_COLS].to_excel(writer, index=False, sheet_name="PTM_Input")
                st.download_button("Download input Excel", data=xlsx_buf.getvalue(), file_name=f"{fname_base}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("No input data available to download yet.")
        except Exception:
            st.info("No input data available to download yet.")

tabs = st.tabs(["📝 Input table", "🧮 Compute distribution"])

# Show current dataset and system status
n_sites = len(st.session_state.df)
# Get probability columns from actual DataFrame, not from DEFAULT_COLS
actual_prob_cols = [col for col in st.session_state.df.columns if col.startswith("P(")]
temp_df = st.session_state.df.copy()
if actual_prob_cols:  # Only calculate if there are probability columns
    temp_df["Prob_Sum"] = temp_df[actual_prob_cols].sum(axis=1)
    n_valid = sum(np.isclose(temp_df["Prob_Sum"].fillna(0), 1.0, atol=1e-6))
else:
    n_valid = 0

system_info_col, status_col1, status_col2 = st.columns([2, 3, 1])

with system_info_col:
    system_name = st.session_state.get('charge_system', '5-state')
    min_charge = st.session_state.get('min_charge', -2)
    max_charge = st.session_state.get('max_charge', 2)
    st.info(f"⚙️ Current: **{system_name}** ({min_charge:+d} to {max_charge:+d})")

with status_col1:
    if n_valid == n_sites:
        st.success(f"✅ Dataset ready: {n_sites} PTM sites, all valid")
    else:
        st.warning(f"⚠️ Dataset: {n_sites} PTM sites, {n_valid} valid, {n_sites-n_valid} need fixing")

with status_col2:
    if st.button("🔄 Reset to default", key="reset_data", help="Start over with 2 example sites"):
        # Reset to 5-state system with examples
        st.session_state.charge_system = "5-state"
        st.session_state.min_charge = -2
        st.session_state.max_charge = 2
        
        reset_cols = generate_charge_columns(-2, 2)
        st.session_state.df = pd.DataFrame([
            ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
            ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ], columns=reset_cols)
        st.rerun()

with tabs[0]:

    # Build a compact preview with a simple validation indicator
    prob_cols = [col for col in st.session_state.df.columns if col.startswith("P(")]
    display_df = st.session_state.df.copy()
    if prob_cols:
        display_df["Prob_Sum"] = display_df[prob_cols].sum(axis=1)
        display_df["Status"] = display_df["Prob_Sum"].apply(lambda x: "✅" if np.isclose(x, 1.0, atol=tol) else "❌")
    else:
        display_df["Prob_Sum"] = 0.0
        display_df["Status"] = "❌"

    # Keep preview columns compact: Status, Site_ID, Copies, probabilities, Sum
    base_cols = [col for col in ["Site_ID", "Copies"] if col in display_df.columns]
    prob_display_cols = [col for col in display_df.columns if col.startswith("P(")]
    display_cols = ["Status"] + base_cols + prob_display_cols + ["Prob_Sum"]
    display_df = display_df[display_cols]

    # Editor: keep Status and Prob_Sum read-only
    edited = st.data_editor(
        display_df,
        width='stretch',
        height=table_height,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.TextColumn("Status", width="small", help="✅ = Valid, ❌ = Invalid"),
            **{"Site_ID": st.column_config.TextColumn("Site_ID") if "Site_ID" in display_df.columns else {},
               "Copies": st.column_config.NumberColumn("Copies", min_value=1, step=1) if "Copies" in display_df.columns else {}},
            **{col: st.column_config.NumberColumn(col, min_value=0.0, max_value=1.0, step=0.001, format="%.3f") 
               for col in prob_display_cols},
            "Prob_Sum": st.column_config.NumberColumn("Sum", format="%.3f", help="Sum of probability columns")
        },
        hide_index=True,
        disabled=["Status", "Prob_Sum"]
    )

    # Persist edits back to session state (exclude Status and Prob_Sum)
    editable_cols = [col for col in display_df.columns if col not in ("Status", "Prob_Sum")]
    st.session_state.df = edited[editable_cols].copy()

    # Note: validation/status is already shown at the top of the page (to avoid duplication
    # we don't repeat the green confirmation here). Downloads remain available in the sidebar
    # 'Downloads' expander.

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
# Interactive Plotting Functions
# -------------------------------
def create_charge_distribution_plot(window_df, tail_low=0, tail_high=0, total_sites=0):
    """Create interactive bar chart of charge distribution."""
    
    # Create the main bar chart
    fig = go.Figure()
    
    # Determine colors based on charge values
    colors = []
    for charge in window_df['Charge']:
        if charge < -2:
            colors.append('#d62728')  # Red for highly negative
        elif charge < 0:
            colors.append('#ff7f0e')  # Orange for negative
        elif charge == 0:
            colors.append('#2ca02c')  # Green for neutral
        elif charge <= 2:
            colors.append('#1f77b4')  # Blue for positive
        else:
            colors.append('#9467bd')  # Purple for highly positive
    
    # Add main distribution bars
    fig.add_trace(go.Bar(
        x=window_df['Charge'],
        y=window_df['Probability'],
        marker_color=colors,
        name='Probability',
        hovertemplate='<b>Charge: %{x:+d}</b><br>' +
                     'Probability: %{y:.4f}<br>' +
                     'Percentage: %{customdata:.1%}<br>' +
                     '<extra></extra>',
        customdata=window_df['Probability']
    ))
    
    # Add tail mass annotations if significant
    if tail_low > 0.001:
        fig.add_annotation(
            x=window_df['Charge'].min() - 0.5,
            y=max(window_df['Probability']) * 0.8,
            text=f"◀ Tail mass: {tail_low:.1%}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            font=dict(color="red", size=12)
        )
    
    if tail_high > 0.001:
        fig.add_annotation(
            x=window_df['Charge'].max() + 0.5,
            y=max(window_df['Probability']) * 0.8,
            text=f"Tail mass: {tail_high:.1%} ▶",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            font=dict(color="red", size=12)
        )
    
    # Styling
    fig.update_layout(
        title=f'PTM Charge Distribution ({total_sites} sites)',
        xaxis_title='Net Charge',
        yaxis_title='Probability',
        showlegend=False,
        template='plotly_white',
        height=500,
        hovermode='x unified'
    )
    
    # Format axes
    fig.update_xaxis(
        tickmode='linear',
        tick0=window_df['Charge'].min(),
        dtick=1,
        title_font_size=14
    )
    fig.update_yaxis(
        tickformat='.3f',
        title_font_size=14
    )
    
    return fig

def create_cumulative_distribution_plot(window_df, tail_low=0, tail_high=0):
    """Create cumulative probability distribution plot."""
    
    # Calculate cumulative probabilities
    charges = window_df['Charge'].values
    probs = window_df['Probability'].values
    
    # Include tail masses
    full_charges = np.concatenate([[-99], charges, [99]])  # Dummy values for tails
    full_probs = np.concatenate([[0], probs, [0]])
    
    # Add tail masses to first and last positions
    full_probs[0] = tail_low
    full_probs[-1] = tail_high
    
    # Calculate cumulative sum
    cumulative = np.cumsum(full_probs)
    
    fig = go.Figure()
    
    # Main cumulative curve (excluding dummy endpoints)
    fig.add_trace(go.Scatter(
        x=charges,
        y=cumulative[1:-1],  # Exclude dummy endpoints
        mode='lines+markers',
        name='Cumulative Probability',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Up to charge %{x:+d}</b><br>' +
                     'Cumulative probability: %{y:.3f}<br>' +
                     '<extra></extra>'
    ))
    
    # Add reference lines
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                  annotation_text="Median (50%)", annotation_position="bottom right")
    fig.add_hline(y=0.9, line_dash="dot", line_color="orange", 
                  annotation_text="90%", annotation_position="bottom right")
    
    fig.update_layout(
        title='Cumulative Charge Distribution',
        xaxis_title='Net Charge',
        yaxis_title='Cumulative Probability',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    fig.update_xaxis(
        tickmode='linear',
        tick0=charges.min(),
        dtick=1
    )
    fig.update_yaxis(
        tickformat='.2f',
        range=[0, 1]
    )
    
    return fig

def create_combined_plots(window_df, tail_low=0, tail_high=0, total_sites=0):
    """Create a combined plot with both distribution and cumulative views."""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Probability Distribution', 'Cumulative Distribution'),
        vertical_spacing=0.12,
        row_heights=[0.6, 0.4]
    )
    
    # Distribution plot (top)
    colors = []
    for charge in window_df['Charge']:
        if charge < -2:
            colors.append('#d62728')  # Red for highly negative
        elif charge < 0:
            colors.append('#ff7f0e')  # Orange for negative
        elif charge == 0:
            colors.append('#2ca02c')  # Green for neutral
        elif charge <= 2:
            colors.append('#1f77b4')  # Blue for positive
        else:
            colors.append('#9467bd')  # Purple for highly positive
    
    fig.add_trace(
        go.Bar(
            x=window_df['Charge'],
            y=window_df['Probability'],
            marker_color=colors,
            name='Probability',
            hovertemplate='<b>Charge: %{x:+d}</b><br>' +
                         'Probability: %{y:.4f}<br>' +
                         'Percentage: %{customdata:.1%}<br>' +
                         '<extra></extra>',
            customdata=window_df['Probability']
        ),
        row=1, col=1
    )
    
    # Cumulative plot (bottom)
    charges = window_df['Charge'].values
    probs = window_df['Probability'].values
    cumulative = np.cumsum(probs)
    
    fig.add_trace(
        go.Scatter(
            x=charges,
            y=cumulative,
            mode='lines+markers',
            name='Cumulative',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=4),
            hovertemplate='<b>Up to charge %{x:+d}</b><br>' +
                         'Cumulative: %{y:.3f}<br>' +
                         '<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title_text=f'PTM Charge Analysis ({total_sites} sites)',
        showlegend=False,
        template='plotly_white',
        height=700
    )
    
    # Update axes
    fig.update_xaxes(
        tickmode='linear',
        tick0=window_df['Charge'].min(),
        dtick=1,
        title_text='Net Charge',
        row=2, col=1
    )
    fig.update_yaxes(title_text='Probability', row=1, col=1)
    fig.update_yaxes(title_text='Cumulative Probability', tickformat='.2f', row=2, col=1)
    
    return fig

def create_site_contribution_plot(df):
    """Create a heatmap showing individual site charge probabilities."""
    
    # Get probability columns
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    if not prob_cols:
        return None, False
    
    # Prepare data for heatmap
    site_data = df[["Site_ID"] + prob_cols].copy()
    
    # Limit to first 20 sites for readability
    if len(site_data) > 20:
        site_data = site_data.head(20)
        show_warning = True
    else:
        show_warning = False
    
    # Create heatmap
    fig = px.imshow(
        site_data[prob_cols].values,
        labels=dict(x="Charge State", y="PTM Site", color="Probability"),
        x=prob_cols,
        y=site_data['Site_ID'],
        color_continuous_scale='RdYlBu_r',
        aspect='auto'
    )
    
    fig.update_layout(
        title='Individual Site Charge Probabilities' + (' (First 20 sites shown)' if show_warning else ''),
        height=max(300, len(site_data) * 25),
        template='plotly_white'
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate='<b>Site:</b> %{y}<br>' +
                     '<b>Charge:</b> %{x}<br>' +
                     '<b>Probability:</b> %{z:.3f}<br>' +
                     '<extra></extra>'
    )
    
    return fig, show_warning

# -------------------------------
# Task 3 UI
# -------------------------------
with tabs[1]:
    st.subheader("Compute overall protein charge distribution")
    run_btn = st.button("Compute distribution now", key="compute_distribution")

    # Use the latest edited table
    df = st.session_state.df.copy()

    # Validate first - use actual DataFrame columns
    prob_cols = [col for col in df.columns if col.startswith("P(")]
    if prob_cols:
        df["Prob_Sum"] = df[prob_cols].sum(axis=1)
        all_valid = np.all(np.isclose(df["Prob_Sum"].fillna(0), 1.0, atol=tol))
    else:
        all_valid = False
    if not all_valid:
        st.warning("Some rows have probability sums ≠ 1 — they'll be normalized for computation. Check the preview to fix if desired.")
    if run_btn:
        try:
            # Make a normalized copy of the data for computation so we don't modify the preview
            df_for_compute = df.copy()
            if prob_cols:
                for idx, row in df_for_compute.iterrows():
                    probs = row[prob_cols].astype(float).fillna(0.0)
                    s = probs.sum()
                    if s <= 0:
                        # set neutral probability to 1 if row is all zeros
                        neutral_idx = neutral_index_for_range(st.session_state.get('min_charge', -2), st.session_state.get('max_charge', 2))
                        probs = pd.Series(0.0, index=prob_cols)
                        probs.iloc[neutral_idx] = 1.0
                    else:
                        probs = probs / s
                    df_for_compute.loc[idx, prob_cols] = probs.values

            pmf_arr, pmf_off = overall_charge_distribution(df_for_compute)
            window_df, tail_low, tail_high = window_distribution(pmf_arr, pmf_off, -5, +5)

            st.success("🎉 Computation completed successfully!")
            
            # Quick navigation hint
            st.info("💡 **Quick tip**: Scroll down for interactive plots, or jump to: [📊 Plots](#interactive-charge-distribution) | [📥 Downloads](#download-results-plots)")
            
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
            
            # Separator and visual prominence for plots section
            st.markdown("---")
            
            # Interactive visualizations
            st.header("📊 Interactive Charge Distribution")
            
            # Plot options in a more prominent, always-visible section
            plot_col1, plot_col2, plot_col3 = st.columns(3)
            
            with plot_col1:
                plot_style = st.selectbox(
                    "📊 Plot style:",
                    ["Combined view", "Distribution only", "Cumulative only", "Site contributions"],
                    key="plot_style_selector",
                    help="Choose visualization type - Combined view recommended for full analysis"
                )
            
            with plot_col2:
                show_tails = st.checkbox("Show tail annotations", value=True, key="show_tails",
                                       help="Display probability mass outside [-5,+5] window")
            
            with plot_col3:
                plot_height = st.selectbox(
                    "📏 Plot size:",
                    ["Standard", "Compact", "Large"],
                    key="plot_height_selector",
                    help="Adjust plot height for your screen"
                )
            
            # Advanced options in expander for power users
            with st.expander("⚙️ Advanced Plot Options", expanded=False):
                adv_col1, adv_col2 = st.columns(2)
                
                with adv_col1:
                    # Future: Custom charge window
                    st.info("🚧 Coming soon: Custom charge windows, color themes, export formats")
                
                with adv_col2:
                    # Future: Export options
                    st.info("💡 Tip: Use browser right-click on plots to save as PNG")
            
            # Smart recommendations based on data
            if total_sites > 50:
                st.info("🔬 **Large dataset detected** - Combined view recommended to see both distribution shape and cumulative patterns")
            elif total_sites < 5:
                st.info("🎯 **Small dataset** - Site contributions view shows individual site patterns clearly")
            
            # Generate and display plots based on user selection
            if plot_style == "Combined view":
                combined_fig = create_combined_plots(window_df, tail_low, tail_high, total_sites)
                if plot_height == "Compact":
                    combined_fig.update_layout(height=500)
                elif plot_height == "Large":
                    combined_fig.update_layout(height=900)
                st.plotly_chart(combined_fig, width='stretch', key="combined_plot")
                
            elif plot_style == "Distribution only":
                dist_fig = create_charge_distribution_plot(window_df, 
                                                         tail_low if show_tails else 0, 
                                                         tail_high if show_tails else 0, 
                                                         total_sites)
                height_map = {"Compact": 350, "Standard": 500, "Large": 650}
                dist_fig.update_layout(height=height_map[plot_height])
                st.plotly_chart(dist_fig, width='stretch', key="dist_plot")
                
            elif plot_style == "Cumulative only":
                cum_fig = create_cumulative_distribution_plot(window_df, tail_low, tail_high)
                height_map = {"Compact": 300, "Standard": 400, "Large": 550}
                cum_fig.update_layout(height=height_map[plot_height])
                st.plotly_chart(cum_fig, width='stretch', key="cum_plot")
                
            else:  # Site contributions
                site_fig, show_warning = create_site_contribution_plot(df)
                if site_fig is not None:
                    if show_warning:
                        st.info("ℹ️ Showing first 20 sites only for readability. All sites are still included in the overall calculation.")
                    st.plotly_chart(site_fig, width='stretch', key="site_plot")
                else:
                    st.error("Cannot create site contribution plot - no probability data found.")
            
            # Plot insights
            with st.expander("📈 Plot Interpretation Guide", expanded=False):
                st.markdown("""
                **📊 Distribution Plot (Bar Chart):**
                - **Height of bars**: Probability of each charge state
                - **Colors**: Red/Orange (negative), Green (neutral), Blue/Purple (positive)  
                - **Hover**: Detailed probability and percentage information
                - **Shape**: Symmetric = balanced PTMs, Skewed = biased charge pattern
                
                **📈 Cumulative Plot (Line Chart):**
                - **Y-axis**: Probability of having charge ≤ X
                - **Steep rise**: Most probability concentrated in narrow range
                - **Gradual rise**: Probability spread across wide charge range
                - **50% line**: Median charge (half of molecules below this charge)
                
                **🔥 Site Contributions (Heatmap):**
                - **Red areas**: High probability charge states for each site
                - **Blue areas**: Low probability charge states
                - **Vertical patterns**: Sites with similar charge preferences
                - **Horizontal patterns**: Charge states preferred across many sites
                
                **🎯 Key Patterns:**
                - **Sharp peak**: Consistent charge behavior, predictable protein
                - **Broad distribution**: Variable charge behavior, heterogeneous population
                - **Multiple peaks**: Distinct charge populations or PTM patterns
                """)
            
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
            
            st.dataframe(window_df, width='stretch')

            # Enhanced downloads with metadata
            st.subheader("📥 Download Results & Plots")
            
            # Plot downloads in a separate row
            plot_col1, plot_col2, plot_col3 = st.columns(3)
            
            with plot_col1:
                if st.button("💾 Save Distribution Plot", key="save_dist_plot"):
                    dist_fig = create_charge_distribution_plot(window_df, tail_low, tail_high, total_sites)
                    plot_html = dist_fig.to_html(include_plotlyjs='cdn')
                    st.download_button(
                        "📊 Download as HTML",
                        data=plot_html.encode(),
                        file_name=f"ptm_charge_distribution_{total_sites}sites.html",
                        mime="text/html",
                        key="download_dist_html"
                    )
            
            with plot_col2:
                if st.button("📈 Save Cumulative Plot", key="save_cum_plot"):
                    cum_fig = create_cumulative_distribution_plot(window_df, tail_low, tail_high)
                    plot_html = cum_fig.to_html(include_plotlyjs='cdn')
                    st.download_button(
                        "📈 Download as HTML", 
                        data=plot_html.encode(),
                        file_name=f"ptm_cumulative_distribution_{total_sites}sites.html",
                        mime="text/html",
                        key="download_cum_html"
                    )
            
            with plot_col3:
                if st.button("📊📈 Save Combined Plot", key="save_combined_plot"):
                    combined_fig = create_combined_plots(window_df, tail_low, tail_high, total_sites)
                    plot_html = combined_fig.to_html(include_plotlyjs='cdn')
                    st.download_button(
                        "📊📈 Download as HTML",
                        data=plot_html.encode(), 
                        file_name=f"ptm_combined_plots_{total_sites}sites.html",
                        mime="text/html",
                        key="download_combined_html"
                    )
            
            st.markdown("---")
            
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

