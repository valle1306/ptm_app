"""
Test script to validate the accuracy of Yergeev vs Enumeration on small datasets.
This script directly tests the core functions without Streamlit.
"""

import numpy as np
import pandas as pd
from ptm_charge_input_v2 import (
    yergeev_overall_charge_distribution,
    enumerate_charge_combinations,
    window_distribution
)

def test_small_dataset():
    """Test with a small 3-site dataset where enumeration should work perfectly."""
    
    print("=" * 70)
    print("TEST 1: 3-Site Dataset (Should match perfectly)")
    print("=" * 70)
    
    # Create a small 3-site dataset - NORMALIZED
    df = pd.DataFrame([
        ["Site_1", 1, 0.0, 0.5, 0.5, 0.0, 0.0],
        ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ["Site_3", 1, 0.1, 0.3, 0.4, 0.1, 0.1],
    ], columns=["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"])
    
    print("\nDataset:")
    print(df)
    
    # Test Yergeev
    print("\n--- Yergeev's Method ---")
    pmf_y, off_y = yergeev_overall_charge_distribution(df)
    window_y, tail_y_low, tail_y_high = window_distribution(pmf_y, off_y, -5, 5)
    print(f"Time: calculated")
    print(f"Result offset: {off_y}")
    print(f"Result length: {len(pmf_y)}")
    print("\nWindow Distribution:")
    print(window_y)
    
    # Test Enumeration
    print("\n--- Enumeration Method ---")
    pmf_e, off_e, method = enumerate_charge_combinations(df)
    print(f"Method used: {method}")
    if pmf_e is not None:
        window_e, tail_e_low, tail_e_high = window_distribution(pmf_e, off_e, -5, 5)
        print(f"Result offset: {off_e}")
        print(f"Result length: {len(pmf_e)}")
        print("\nWindow Distribution:")
        print(window_e)
        
        # Compare using WINDOW data (not raw arrays) - this is what matters!
        print("\n--- COMPARISON (using window distributions) ---")
        # Windows should match exactly since they're from the same window range
        comparison = pd.DataFrame({
            "Charge": window_y["Charge"],
            "Yergeev": window_y["Probability"],
            "Enumeration": window_e["Probability"],
            "Difference": np.abs(window_y["Probability"].values - window_e["Probability"].values)
        })
        print(comparison)
        max_window_diff = comparison["Difference"].max()
        if max_window_diff < 1e-9:
            print("\n[PERFECT MATCH!]")
        elif max_window_diff < 1e-6:
            print("\n[EXCELLENT MATCH!]")
        elif max_window_diff < 1e-3:
            print("\n[GOOD MATCH - minor numerical differences]")
        else:
            print(f"\n[WARNING] LARGE DIFFERENCE: {max_window_diff:.2e}")
    else:
        print("Enumeration failed or returned None")

def test_medium_dataset():
    """Test with a 5-site dataset."""
    
    print("\n" + "=" * 70)
    print("TEST 2: 5-Site Dataset")
    print("=" * 70)
    
    df = pd.DataFrame([
        ["Site_1", 1, 0.0, 0.5, 0.5, 0.0, 0.0],
        ["Site_2", 1, 0.0, 0.2, 0.6, 0.2, 0.0],
        ["Site_3", 1, 0.1, 0.3, 0.4, 0.1, 0.1],
        ["Site_4", 1, 0.2, 0.3, 0.3, 0.2, 0.0],
        ["Site_5", 1, 0.0, 0.4, 0.4, 0.2, 0.0],
    ], columns=["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"])
    
    print("\nDataset:")
    print(df)
    
    # Test Yergeev
    print("\n--- Yergeev's Method ---")
    pmf_y, off_y = yergeev_overall_charge_distribution(df)
    window_y, _, _ = window_distribution(pmf_y, off_y, -5, 5)
    print("Yergeev result (window):")
    print(window_y)
    
    # Test Enumeration
    print("\n--- Enumeration Method ---")
    pmf_e, off_e, method = enumerate_charge_combinations(df)
    print(f"Method used: {method}")
    if pmf_e is not None:
        window_e, _, _ = window_distribution(pmf_e, off_e, -5, 5)
        print("Enumeration result (window):")
        print(window_e)
        
        # Compare
        print("\n--- COMPARISON (using window distributions) ---")
        comparison = pd.DataFrame({
            "Charge": window_y["Charge"],
            "Yergeev": window_y["Probability"],
            "Enumeration": window_e["Probability"],
            "Difference": np.abs(window_y["Probability"].values - window_e["Probability"].values)
        })
        print(comparison)
        max_window_diff = comparison["Difference"].max()
        rmse = np.sqrt(np.mean(comparison["Difference"].values**2))
        print(f"\nMax Difference: {max_window_diff:.2e}")
        print(f"RMSE: {rmse:.2e}")
        if max_window_diff < 1e-9:
            print("[PERFECT MATCH!]")
        elif max_window_diff < 1e-6:
            print("[EXCELLENT MATCH!]")
        elif max_window_diff < 1e-3:
            print("[GOOD MATCH]")
        else:
            print(f"[WARNING] LARGE DIFFERENCE")
    else:
        print("Enumeration unavailable")

def test_100_site_dataset():
    """Test with a 100-site dataset (should require sampling in enumeration)."""
    
    print("\n" + "=" * 70)
    print("TEST 3: 100-Site Dataset (Enumeration will sample)")
    print("=" * 70)
    
    # Generate varied dataset
    data = []
    for i in range(1, 101):
        site_id = f"Site_{i}"
        copies = 1
        # Vary the probabilities to create different distributions
        if i % 4 == 0:
            probs = [0.0, 0.8, 0.1, 0.1, 0.0]  # Mostly neutral
        elif i % 4 == 1:
            probs = [0.0, 0.2, 0.6, 0.2, 0.0]  # Neutral with some variance
        elif i % 4 == 2:
            probs = [0.0, 0.3, 0.4, 0.3, 0.0]  # Symmetric
        else:
            probs = [0.1, 0.3, 0.3, 0.2, 0.1]  # More varied (sums to 1.0)
        data.append([site_id, copies] + probs)
    
    df = pd.DataFrame(data, columns=["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"])
    
    print(f"Dataset: {len(df)} sites")
    print("First 5 sites:")
    print(df.head())
    
    # Test Yergeev
    print("\n--- Yergeev's Method ---")
    pmf_y, off_y = yergeev_overall_charge_distribution(df)
    window_y, _, _ = window_distribution(pmf_y, off_y, -5, 5)
    print(f"Full dataset result:")
    print(f"  Offset: {off_y}")
    print(f"  Array length: {len(pmf_y)}")
    print(f"  Most likely charge: {window_y.loc[window_y['Probability'].idxmax(), 'Charge']}")
    print(f"  Peak probability: {window_y['Probability'].max():.4f}")
    
    # Test Enumeration
    print("\n--- Enumeration Method ---")
    pmf_e, off_e, method = enumerate_charge_combinations(df)
    print(f"Method used: {method}")
    if pmf_e is not None:
        window_e, _, _ = window_distribution(pmf_e, off_e, -5, 5)
        print(f"  Offset: {off_e}")
        print(f"  Array length: {len(pmf_e)}")
        print(f"  Most likely charge: {window_e.loc[window_e['Probability'].idxmax(), 'Charge']}")
        print(f"  Peak probability: {window_e['Probability'].max():.4f}")
        
        if method == "sampled":
            print("\n[NOTE] Enumeration used sampling (not full enumeration)")
            print("       This means results are on a SUBSET of sites")
            print("       Cannot directly compare to full 100-site Yergeev result!")
    else:
        print("Enumeration unavailable for 100-site dataset (too large)")
        print("[OK] This is expected and correct behavior!")

if __name__ == "__main__":
    test_small_dataset()
    test_medium_dataset()
    test_100_site_dataset()
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
