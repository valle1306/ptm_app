import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PTM Charge Input", layout="wide")

st.title("PTM Charge Variant Input (−2…+2)")
st.caption("Enter any number of PTM sites, copies per site, and charge probabilities. Row sums must equal 1. Then compute the overall charge distribution.")

# -------------------------------
# Data-entry (Task 1 & 2)
# -------------------------------
DEFAULT_COLS = ["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        [
            ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
            ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ],
        columns=DEFAULT_COLS,
    )

with st.sidebar:
    st.header("Table Controls")
    add_rows = st.number_input("Add blank rows", min_value=0, max_value=50, value=0, step=1)
    if st.button("Insert"):
        new = pd.DataFrame([["", 1, 0, 0, 1, 0, 0] for _ in range(add_rows)], columns=DEFAULT_COLS)
        st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)

    st.markdown("---")
    st.header("Download (input)")
    fname_base = st.text_input("Base filename (no extension)", value="ptm_input")
    tol = float(st.text_input("Row-sum tolerance", value="1e-6"))

tabs = st.tabs(["📝 Input table", "🧮 Compute distribution"])

with tabs[0]:
    edited = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Site_ID": st.column_config.TextColumn("Site_ID"),
            "Copies": st.column_config.NumberColumn("Copies", min_value=1, step=1),
            "P(-2)": st.column_config.NumberColumn("P(-2)", min_value=0.0),
            "P(-1)": st.column_config.NumberColumn("P(-1)", min_value=0.0),
            "P(0)":  st.column_config.NumberColumn("P(0)",  min_value=0.0),
            "P(+1)": st.column_config.NumberColumn("P(+1)", min_value=0.0),
            "P(+2)": st.column_config.NumberColumn("P(+2)", min_value=0.0),
        },
        hide_index=True,
    )
    st.session_state.df = edited.copy()

    # Validation
    prob_cols = ["P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
    edited["Prob_Sum"] = edited[prob_cols].sum(axis=1)
    edited["Valid_Row"] = np.isclose(edited["Prob_Sum"], 1.0, atol=tol)

    bad_rows = edited.index[~edited["Valid_Row"]].tolist()
    if len(bad_rows) == 0:
        st.success("All rows valid (sums = 1 within tolerance).")
    else:
        st.warning(f"{len(bad_rows)} row(s) have probability sums != 1 (±{tol}).")

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
    df: DataFrame with columns Site_ID, Copies, P(-2),...,P(+2).
    Returns: (pmf_arr, offset) normalized.
    """
    prob_cols = ["P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]

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

        # Row PMF spans charges -2..+2 -> offset = -2
        base_arr, base_off = pmf_with_offset(probs, -2)

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
    run_btn = st.button("Compute distribution now")

    # Use the latest edited table
    df = st.session_state.df.copy()

    # Validate first
    prob_cols = ["P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
    df["Prob_Sum"] = df[prob_cols].sum(axis=1)
    all_valid = np.all(np.isclose(df["Prob_Sum"].fillna(0), 1.0, atol=tol))
    if not all_valid:
        st.error("Fix input rows so each probability row sums to 1 before computing.")
    elif run_btn:
        try:
            pmf_arr, pmf_off = overall_charge_distribution(df)
            window_df, tail_low, tail_high = window_distribution(pmf_arr, pmf_off, -5, +5)

            st.success("Computed successfully.")
            st.markdown(f"**Support:** charges from {pmf_off} to {pmf_off + len(pmf_arr) - 1}")
            st.markdown(f"**Tail mass below −5:** {tail_low:.6g} &nbsp;&nbsp; | &nbsp;&nbsp; **Tail mass above +5:** {tail_high:.6g}")
            st.markdown(f"**Mass in [−5, +5]:** {(1.0 - tail_low - tail_high):.6g}")

            st.dataframe(window_df, use_container_width=True)

            # Downloads for the windowed distribution and full distribution
            c1, c2 = st.columns(2)
            with c1:
                csv_bytes = window_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download window [−5…+5] as CSV", data=csv_bytes,
                                   file_name="overall_charge_window.csv", mime="text/csv")
            with c2:
                # Full distribution to Excel
                full_df = pd.DataFrame({
                    "Charge": np.arange(pmf_off, pmf_off + len(pmf_arr)),
                    "Probability": pmf_arr
                })
                xlsx_buf = io.BytesIO()
                with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
                    full_df.to_excel(writer, index=False, sheet_name="Full_Distribution")
                st.download_button("Download full distribution (.xlsx)", data=xlsx_buf.getvalue(),
                                   file_name="overall_charge_full.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"Computation failed: {e}")

st.caption("Tip: You can later extend input columns to 11 states (−5…+5). The computation tab will still work — just adjust the base PMF and offset.")
