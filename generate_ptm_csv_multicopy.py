import pandas as pd
import numpy as np

n_sites = 1000
min_charge = -2
max_charge = 2
charge_range = max_charge - min_charge + 1

np.random.seed(42)  # For reproducibility

data = []
for i in range(1, n_sites + 1):
    site_id = f"Site_{i}"
    # Assign random copies between 1 and 10
    copies = np.random.randint(1, 11)
    # Generate random probabilities that sum to 1
    probs = np.random.dirichlet(np.ones(charge_range))
    row = [site_id, copies] + list(probs)
    data.append(row)

columns = ["Site_ID", "Copies"] + [f"P({c:+d})" if c != 0 else "P(0)" for c in range(min_charge, max_charge + 1)]
df = pd.DataFrame(data, columns=columns)
df.to_csv("sample_ptm_n1000_multicopy.csv", index=False)
print("sample_ptm_n1000_multicopy.csv generated.")
