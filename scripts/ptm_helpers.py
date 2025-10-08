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
    system_name = f"{max_charge - min_charge + 1}-state"
    return system_name, min_charge, max_charge
