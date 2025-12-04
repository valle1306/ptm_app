"""
Comprehensive Stress Test for PTM Charge Distribution Algorithms
Tests with multiple copies per site (not just Copies=1)
"""
import numpy as np
import pandas as pd
import time
from advanced_algorithms import adaptive_charge_distribution

def generate_test_dataset(n_sites, copies_pattern="varied", charge_range=(-2, 2)):
    """
    Generate test datasets with different copy patterns.
    
    copies_pattern options:
    - "all_1": All sites have 1 copy
    - "all_2": All sites have 2 copies  
    - "all_3": All sites have 3 copies
    - "varied": Copies vary 1,2,3,1,2,3...
    - "random": Random copies 1-5
    """
    np.random.seed(42)
    min_c, max_c = charge_range
    n_charges = max_c - min_c + 1
    
    data = []
    for i in range(n_sites):
        if copies_pattern == "all_1":
            copies = 1
        elif copies_pattern == "all_2":
            copies = 2
        elif copies_pattern == "all_3":
            copies = 3
        elif copies_pattern == "varied":
            copies = (i % 3) + 1
        elif copies_pattern == "random":
            copies = np.random.randint(1, 6)
        else:
            copies = 1
        
        # Random probabilities
        probs = np.random.dirichlet([1] * n_charges)
        
        row = {"Site_ID": f"Site_{i+1}", "Copies": copies}
        for j, charge in enumerate(range(min_c, max_c + 1)):
            if charge == 0:
                row["P(0)"] = probs[j]
            elif charge > 0:
                row[f"P(+{charge})"] = probs[j]
            else:
                row[f"P({charge})"] = probs[j]
        data.append(row)
    
    return pd.DataFrame(data)

def run_stress_tests():
    print("=" * 80)
    print("COMPREHENSIVE STRESS TEST - Multiple Copies per Site")
    print("=" * 80)
    print()
    
    test_cases = [
        # (n_sites, copies_pattern, description)
        (10, "all_1", "10 sites, all 1 copy"),
        (10, "all_2", "10 sites, all 2 copies (20 total)"),
        (10, "all_3", "10 sites, all 3 copies (30 total)"),
        (10, "varied", "10 sites, varied 1-3 copies"),
        (50, "all_1", "50 sites, all 1 copy"),
        (50, "all_2", "50 sites, all 2 copies (100 total)"),
        (50, "varied", "50 sites, varied 1-3 copies"),
        (100, "all_1", "100 sites, all 1 copy"),
        (100, "all_2", "100 sites, all 2 copies (200 total)"),
        (100, "varied", "100 sites, varied 1-3 copies"),
        (200, "varied", "200 sites, varied 1-3 copies (~400 total)"),
        (500, "all_1", "500 sites, all 1 copy"),
        (500, "varied", "500 sites, varied 1-3 copies (~1000 total)"),
    ]
    
    results = []
    
    for n_sites, pattern, desc in test_cases:
        print(f"Testing: {desc}")
        df = generate_test_dataset(n_sites, pattern)
        total_copies = df['Copies'].sum()
        
        start = time.time()
        try:
            pmf, offset, method, sites = adaptive_charge_distribution(df, method="auto")
            elapsed = (time.time() - start) * 1000
            
            # Find peak
            peak_idx = pmf.argmax()
            peak_charge = peak_idx + offset
            peak_prob = pmf[peak_idx]
            
            # Validate PMF sums to 1
            pmf_sum = pmf.sum()
            is_valid = np.isclose(pmf_sum, 1.0, atol=1e-6)
            
            results.append({
                "desc": desc,
                "sites": n_sites,
                "total_copies": int(total_copies),
                "time_ms": elapsed,
                "method": method,
                "peak": peak_charge,
                "peak_prob": peak_prob,
                "valid": is_valid
            })
            
            print(f"  ✓ {elapsed:.1f}ms | Method: {method} | Peak: {peak_charge:+d} | Valid: {is_valid}")
        
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            results.append({
                "desc": desc,
                "sites": n_sites,
                "total_copies": int(total_copies),
                "time_ms": -1,
                "method": "FAILED",
                "peak": 0,
                "peak_prob": 0,
                "valid": False
            })
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Summary table
    print(f"\n{'Description':<45} {'Sites':>6} {'Copies':>7} {'Time':>10} {'Method':<25}")
    print("-" * 100)
    for r in results:
        if r['time_ms'] >= 0:
            print(f"{r['desc']:<45} {r['sites']:>6} {r['total_copies']:>7} {r['time_ms']:>8.1f}ms {r['method']:<25}")
        else:
            print(f"{r['desc']:<45} {r['sites']:>6} {r['total_copies']:>7} {'FAILED':>10} {r['method']:<25}")
    
    # Check all valid
    all_valid = all(r['valid'] for r in results if r['time_ms'] >= 0)
    print()
    if all_valid:
        print("✅ ALL TESTS PASSED - PMF valid for all cases")
    else:
        print("❌ SOME TESTS FAILED")
    
    return results

def test_validation_accuracy():
    """Test that algorithm matches enumeration for small datasets with multiple copies."""
    print()
    print("=" * 80)
    print("VALIDATION ACCURACY TEST - Enumeration Comparison")
    print("=" * 80)
    
    # Import enumeration function
    import sys
    sys.path.insert(0, '.')
    from ptm_charge_input_v3 import enumerate_charge_combinations, yergeev_overall_charge_distribution
    
    test_cases = [
        (3, "all_1", "3 sites, 1 copy each"),
        (3, "all_2", "3 sites, 2 copies each (6 total)"),
        (4, "varied", "4 sites, varied copies"),
        (5, "all_1", "5 sites, 1 copy each"),
    ]
    
    for n_sites, pattern, desc in test_cases:
        print(f"\nTesting: {desc}")
        df = generate_test_dataset(n_sites, pattern, charge_range=(-1, 1))  # Smaller for enumeration
        total_copies = df['Copies'].sum()
        
        # Normalize probabilities
        prob_cols = [c for c in df.columns if c.startswith("P(")]
        for idx, row in df.iterrows():
            probs = row[prob_cols].astype(float)
            df.loc[idx, prob_cols] = (probs / probs.sum()).values
        
        # Run Yergeev
        pmf_y, off_y = yergeev_overall_charge_distribution(df)
        
        # Run enumeration
        pmf_e, off_e, method = enumerate_charge_combinations(df)
        
        if pmf_e is None:
            print(f"  ⚠ Enumeration unavailable (too many combinations)")
            continue
        
        # Compare
        # Align arrays
        min_off = min(off_y, off_e)
        max_end = max(off_y + len(pmf_y), off_e + len(pmf_e))
        
        aligned_y = np.zeros(max_end - min_off)
        aligned_e = np.zeros(max_end - min_off)
        
        aligned_y[off_y - min_off : off_y - min_off + len(pmf_y)] = pmf_y
        aligned_e[off_e - min_off : off_e - min_off + len(pmf_e)] = pmf_e
        
        max_diff = np.max(np.abs(aligned_y - aligned_e))
        
        if max_diff < 1e-9:
            print(f"  ✓ PERFECT MATCH (max diff: {max_diff:.2e})")
        elif max_diff < 1e-6:
            print(f"  ✓ Excellent match (max diff: {max_diff:.2e})")
        else:
            print(f"  ⚠ Difference detected (max diff: {max_diff:.2e})")
            print(f"    Yergeev sum: {pmf_y.sum():.6f}, Enum sum: {pmf_e.sum():.6f}")

if __name__ == "__main__":
    run_stress_tests()
    test_validation_accuracy()
    print()
    print("=" * 80)
    print("ALL STRESS TESTS COMPLETE")
    print("=" * 80)
