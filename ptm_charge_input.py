import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PTM Charge Input", layout="wide")

st.title("PTM Charge Variant Input (−2…+2)")
st.caption("Enter any number of PTM sites, copies per site, and charge probabilities. Row sums must equal 1.")

# ---- Defaults ----
DEFAULT_COLS = ["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        [
            ["Site_1", 1, 0.0, 0.0, 1.0, 0.0, 0.0],
            ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ],
        columns=DEFAULT_COLS,
    )

# ---- Sidebar controls ----
with st.sidebar:
    st.header("Table Controls")
    add_rows = st.number_input("Add blank rows", min_value=0, max_value=50, value=0, step=1)
    if st.button("Insert"):
        new = pd.DataFrame([["", 1, 0, 0, 1, 0, 0] for _ in range(add_rows)], columns=DEFAULT_COLS)
        st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)

    st.markdown("---")
    st.header("Download")
    fname_base = st.text_input("Base filename (no extension)", value="ptm_input")
    tol = float(st.text_input("Row-sum tolerance", value="1e-6"))

# ---- Editable table ----
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

# ---- Validation ----
prob_cols = ["P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
edited["Prob_Sum"] = edited[prob_cols].sum(axis=1)
edited["Valid_Row"] = np.isclose(edited["Prob_Sum"], 1.0, atol=tol)

bad_rows = edited.index[~edited["Valid_Row"]].tolist()
if len(bad_rows) == 0:
    st.success("All rows valid (sums = 1 within tolerance).")
else:
    st.warning(f"{len(bad_rows)} row(s) have probability sums != 1 (±{tol}).")

# ---- Preview & Export ----
st.subheader("Preview (with validation)")
st.dataframe(edited, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    csv_bytes = edited[DEFAULT_COLS].to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_bytes, file_name=f"{fname_base}.csv", mime="text/csv", disabled=len(bad_rows)>0)

with col2:
    xlsx_buf = io.BytesIO()
    with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
        edited[DEFAULT_COLS].to_excel(writer, index=False, sheet_name="PTM_Input")
    st.download_button("Download Excel (.xlsx)", data=xlsx_buf.getvalue(),
                       file_name=f"{fname_base}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       disabled=len(bad_rows)>0)

st.caption("Tip: keep `Copies` as integers ≥ 1. You can extend to 11 charge states later (−5…+5).")
