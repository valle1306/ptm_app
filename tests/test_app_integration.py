"""Quick integration test to verify the fix works in the app"""
import sys
import pandas as pd
import numpy as np
from ptm_charge_input_v2 import (
    yergeev_overall_charge_distribution,
    enumerate_charge_combinations,
    window_distribution
)

# Create a simple test dataset
data = {
    'Site_ID': ['Site_1', 'Site_2', 'Site_3'],
    'Copies': [1, 1, 1],
    'P(-2)': [0.0, 0.0, 0.1],
    'P(-1)': [0.5, 0.2, 0.3],
    'P(0)': [0.5, 0.6, 0.4],
    'P(+1)': [0.0, 0.2, 0.1],
    'P(+2)': [0.0, 0.0, 0.1]
}
df = pd.DataFrame(data)

print("Testing Yergeev vs Enumeration Integration:")
print("=" * 60)

# Test Yergeev
pmf_y, off_y = yergeev_overall_charge_distribution(df)
window_y, _, _ = window_distribution(pmf_y, off_y, -5, 5)

# Test Enumeration
pmf_e, off_e, method = enumerate_charge_combinations(df)
window_e, _, _ = window_distribution(pmf_e, off_e, -5, 5)

print(f"\nYergeev:    offset={off_y}, length={len(pmf_y)}")
print(f"Enumeration: offset={off_e}, length={len(pmf_e)} (method: {method})")

if off_y == off_e and len(pmf_y) == len(pmf_e):
    print("\n[SUCCESS] Arrays have matching structure!")
    
    # Check if probabilities match
    diff = np.abs(window_y['Probability'].values - window_e['Probability'].values)
    max_diff = diff.max()
    mean_diff = diff.mean()
    
    print(f"Max difference: {max_diff:.2e}")
    print(f"Mean difference: {mean_diff:.2e}")
    
    if max_diff < 1e-6:
        print("\n[SUCCESS] Validation methods are working correctly!")
        sys.exit(0)
    else:
        print(f"\n[ERROR] Large difference detected: {max_diff}")
        sys.exit(1)
else:
    print(f"\n[ERROR] Array structure mismatch!")
    print(f"  Yergeev: offset={off_y}, len={len(pmf_y)}")
    print(f"  Enumeration: offset={off_e}, len={len(pmf_e)}")
    sys.exit(1)
