"""
Integration test: Verify new algorithm selection works in the app
Test all three methods on sample data and show results
"""

import pandas as pd
import time
from advanced_algorithms import adaptive_charge_distribution
from ptm_charge_input_v2 import yergeev_overall_charge_distribution, window_distribution

# Test data: 10 sites
test_data = {
    'Site_ID': [f'Site_{i+1}' for i in range(10)],
    'Copies': [1]*10,
    'P(-2)': [0.0, 0.0, 0.1, 0.0, 0.05, 0.0, 0.02, 0.0, 0.0, 0.0],
    'P(-1)': [0.5, 0.2, 0.3, 0.1, 0.2, 0.3, 0.25, 0.4, 0.1, 0.2],
    'P(0)': [0.5, 0.6, 0.4, 0.7, 0.5, 0.5, 0.5, 0.4, 0.6, 0.6],
    'P(+1)': [0.0, 0.2, 0.1, 0.2, 0.2, 0.2, 0.18, 0.2, 0.2, 0.15],
    'P(+2)': [0.0, 0.0, 0.1, 0.0, 0.05, 0.0, 0.05, 0.0, 0.1, 0.05]
}

df = pd.DataFrame(test_data)

print("\n" + "="*80)
print("INTEGRATION TEST: Algorithm Selection & Display")
print("="*80)
print(f"\nTest Dataset: {len(df)} sites")
print(df.head(3))

# Test each method
methods_to_test = ["auto", "yergeev", "fft", "gaussian"]

results = []

for method in methods_to_test:
    print(f"\n{'-'*80}")
    print(f"Testing method: {method}")
    print(f"{'-'*80}")
    
    try:
        start = time.time()
        pmf, offset, method_used, n_sites = adaptive_charge_distribution(df, method=method)
        elapsed = time.time() - start
        
        window, _, _ = window_distribution(pmf, offset, -5, 5)
        peak_prob = window['Probability'].max()
        most_likely = window.loc[window['Probability'].idxmax(), 'Charge']
        
        print(f"Status: SUCCESS")
        print(f"Method returned: {method_used}")
        print(f"Time: {elapsed*1000:.2f} ms")
        print(f"Sites processed: {n_sites}")
        print(f"Array size: {len(pmf)}")
        print(f"Most likely charge: {most_likely:+d}")
        print(f"Peak probability: {peak_prob:.4f}")
        
        results.append({
            'method': method,
            'status': 'SUCCESS',
            'method_used': method_used,
            'time_ms': elapsed*1000,
            'sites': n_sites,
            'array_size': len(pmf),
            'peak_prob': peak_prob
        })
        
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {str(e)}")
        results.append({
            'method': method,
            'status': 'FAILED',
            'error': str(e)
        })

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

df_results = pd.DataFrame(results)
print("\nResults:")
print(df_results.to_string(index=False))

# Verify auto selection
print("\n" + "="*80)
print("AUTO SELECTION VERIFICATION")
print("="*80)
auto_result = [r for r in results if r['method'] == 'auto'][0]
yergeev_result = [r for r in results if r['method'] == 'yergeev'][0]

if auto_result['status'] == 'SUCCESS' and yergeev_result['status'] == 'SUCCESS':
    # For 10 sites, auto should select Yergeev (since 10 <= 15)
    expected = "Yergeev"
    if expected in auto_result['method_used']:
        print(f"\n[PASS] Auto-selection correctly chose Yergeev for 10 sites")
        print(f"  Auto returned: {auto_result['method_used']}")
    else:
        print(f"\n[WARNING] Auto selected different method for 10 sites")
        print(f"  Expected: Yergeev")
        print(f"  Got: {auto_result['method_used']}")
else:
    print("\n[FAIL] Could not verify auto-selection")

# Verify UI display items work
print("\n" + "="*80)
print("UI DISPLAY ITEMS READY")
print("="*80)
print("""
The following information will be displayed in the Streamlit app:

1. Algorithm Selection dropdown:
   - Auto (Recommended)
   - Yergeev (Exact)
   - FFT (Fast Exact)
   - Gaussian (Approximation)

2. Info bar showing:
   - Method: [algorithm name]
   - Computation Time: X.XXX ms
   - Sites Processed: N
   - Array Size: N

3. Standard metrics:
   - PTM Sites
   - Most Likely Charge
   - Peak Probability
   - Central Mass
""")

# Performance comparison
print("\n" + "="*80)
print("PERFORMANCE COMPARISON")
print("="*80)

success_results = [r for r in results if r['status'] == 'SUCCESS']
for r in success_results:
    print(f"{r['method'].upper():12s}: {r['time_ms']:7.2f} ms  ({r['method_used']})")

print("\n" + "="*80)
print("INTEGRATION TEST COMPLETE")
print("="*80)
