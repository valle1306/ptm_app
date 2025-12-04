"""
Performance analysis and algorithm comparison for PTM charge distribution calculation

Goals:
1. Understand Yergeev's computational complexity
2. Identify bottlenecks for large numbers of sites
3. Evaluate alternative algorithms (FFT, approximations, etc.)
4. Propose better algorithm that can handle 100+ sites efficiently
"""

import numpy as np
import pandas as pd
import time
import sys
from ptm_charge_input_v2 import (
    yergeev_overall_charge_distribution,
    enumerate_charge_combinations
)

def generate_test_dataset(n_sites, charge_range=(-2, 2)):
    """Generate a synthetic dataset with n_sites"""
    min_c, max_c = charge_range
    data = []
    np.random.seed(42)
    
    for i in range(n_sites):
        site_id = f"Site_{i+1}"
        copies = 1  # Could vary from 1-10
        
        # Random probability distribution
        n_states = max_c - min_c + 1
        probs = np.random.dirichlet(np.ones(n_states))
        
        data.append([site_id, copies] + list(probs))
    
    cols = ["Site_ID", "Copies"] + [
        f"P({c:+d})" if c != 0 else "P(0)" 
        for c in range(min_c, max_c + 1)
    ]
    return pd.DataFrame(data, columns=cols)

def benchmark_yergeev(n_sites_list):
    """Benchmark Yergeev's method across different numbers of sites"""
    results = []
    
    for n_sites in n_sites_list:
        print(f"\nBenchmarking Yergeev with {n_sites} sites...", end=" ", flush=True)
        
        df = generate_test_dataset(n_sites)
        
        # Time the computation
        start = time.time()
        try:
            pmf, offset = yergeev_overall_charge_distribution(df)
            elapsed = time.time() - start
            array_size = len(pmf)
            
            print(f"OK")
            results.append({
                "n_sites": n_sites,
                "time_sec": elapsed,
                "array_size": array_size,
                "theoretical_max": n_sites * 2,  # For charge range -2 to +2
                "status": "success"
            })
            print(f"  Time: {elapsed:.4f}s | Array size: {array_size} | Theoretical max: {n_sites*4+1}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"FAILED: {str(e)[:50]}")
            results.append({
                "n_sites": n_sites,
                "time_sec": elapsed,
                "array_size": None,
                "theoretical_max": n_sites * 2,
                "status": f"failed: {str(e)[:30]}"
            })
    
    return pd.DataFrame(results)

def theoretical_analysis():
    """Analyze theoretical complexity of Yergeev"""
    print("\n" + "="*70)
    print("THEORETICAL COMPLEXITY ANALYSIS")
    print("="*70)
    
    print("""
Yergeev's Method (Iterative Convolution):
------------------------------------------

Algorithm:
  1. Start with delta function at charge 0: [1.0]
  2. For each site, convolve its PMF with the accumulated result
  3. For each copy of a site, repeat the convolution
  
Time Complexity Analysis:
  - Each convolution: O(n * m) where n, m are array sizes
  - Array size growth: After site i, array size ~ (4*i + 1) for charge range [-2, +2]
    (since each site can add ±2 to the charge range)
  - N sites: Total operations ~ Sum(i=1 to N) (4*i * 4*i) = Sum(16*i^2) = O(N^3)
  
Memory:
  - Array size grows linearly: O(N) for N sites
  - Final array size = 4*N + 1 for 5-state system (-2 to +2)

Space Complexity: O(N)
Time Complexity: O(N^3) - CUBIC! This becomes very slow for large N

Example:
  - 10 sites:  ~1,600 operations, ~41 array elements
  - 50 sites:  ~40,000 operations, ~201 array elements
  - 100 sites: ~160,000 operations, ~401 array elements
  - 1000 sites: ~16,000,000 operations, ~4,001 array elements

Bottleneck: Convolution operation with growing arrays
    """)

def propose_alternatives():
    """Propose better algorithms"""
    print("\n" + "="*70)
    print("ALTERNATIVE ALGORITHMS TO CONSIDER")
    print("="*70)
    
    print("""
1. FFT-BASED CONVOLUTION (Better for large arrays)
   ================================================
   
   Theory: Instead of direct convolution O(N^2), use FFT O(N log N)
   
   Process:
   - Convert PMF to log-space to avoid overflow
   - Use FFT to multiply distributions in frequency domain
   - Convert back to probability space
   
   Time Complexity: O(N^2 log N) instead of O(N^3)
   Space Complexity: O(N)
   
   Advantage: ~10-100x faster for large N
   Challenge: Numerical stability with FFT, floating-point precision
   
   For 100 sites:
   - Direct: ~160,000 operations
   - FFT: ~160,000 * log(400) approx 1.28M operations (but with smaller constant!)

2. GAUSSIAN APPROXIMATION (Fast, ~accurate for large N)
   =====================================================
   
   Theory: For many independent sites, CLT says charge distribution -> Normal
   
   Process:
   - Calculate mean and variance from individual site probabilities
   - Approximate as Gaussian: P(z) = (1/sqrt(2*pi*sigma^2)) * exp(-(z-mu)^2/(2*sigma^2))
   
   Time Complexity: O(N) - just compute mean and variance!
   Space Complexity: O(N) for array discretization
   
   Accuracy: Excellent for 50+ sites, minor errors for <20 sites
   
   Advantages:
   - Extremely fast (linear time)
   - Simple to implement
   - Natural for large site counts
   
   Disadvantages:
   - Smooths out multimodality if sites have very different distributions
   - Slightly less accurate for small N
   
   For 100 sites:
   - Time: ~100 arithmetic operations vs ~160,000
   - Error: ~1-5% max difference vs Yergeev

3. SPARSE/RECURSIVE CONVOLUTION (Memory efficient)
   ================================================
   
   Theory: Only track significant probability values, skip zeros
   
   Process:
   - Represent PMF as sparse dictionary {charge: probability}
   - Multiply only non-zero entries during convolution
   - Threshold small values to maintain sparsity
   
   Time Complexity: O(N * K^2) where K = avg non-zero entries
   Space Complexity: O(N * K) where K << 4N (typically)
   
   Advantage: Good if distributions are sparse (few likely charges)
   Disadvantage: Can still be slow if distributions are dense

4. DYNAMIC PROGRAMMING (Careful optimization)
   ===========================================
   
   Theory: Similar to Yergeev but with memoization and early pruning
   
   Process:
   - Cache intermediate results for repeated computations
   - Prune probabilities below threshold early
   - Group similar distributions
   
   Time Complexity: O(N^2 * K) with smart caching
   Space Complexity: O(N * K)
   
   Advantage: Can beat Yergeev for repeated calculations
   Disadvantage: Memory overhead

5. HYBRID APPROACH (Best of all worlds)
   ====================================
   
   Strategy:
   - For N <= 20: Use exact Yergeev (most accurate)
   - For 20 < N <= 100: Use FFT-accelerated Yergeev
   - For N > 100: Use Gaussian approximation or FFT
   - Always validate against Yergeev on sample
   
   This gives:
   - Accuracy for small datasets
   - Speed for medium datasets
   - Practicality for large datasets
    """)

def recommendation():
    """Provide recommendation"""
    print("\n" + "="*70)
    print("RECOMMENDATION FOR YOUR APPLICATION")
    print("="*70)
    
    print("""
PROPOSED SOLUTION: HYBRID FFT + GAUSSIAN APPROACH

1. Keep Yergeev as the gold standard (for validation)
2. Add FFT-accelerated Yergeev:
   - Use numpy.fft for convolution
   - Should be 10-20x faster than direct convolution
   - Same accuracy as Yergeev
   - Good for up to ~200-500 sites
   
3. Add Gaussian approximation:
   - For large N (>100 sites)
   - Extremely fast, good accuracy
   - Use for stress testing, quick estimates
   
4. Auto-switch algorithm based on site count:
   ```python
   if n_sites <= 15:
       use Yergeev (validation target)
   elif n_sites <= 100:
       use FFT-accelerated Yergeev (fast but exact)
   else:
       use Gaussian approximation (practical for large N)
   ```

5. Always show which method was used
6. For validation: Yergeev is always the baseline

Next Steps:
-----------
1. Implement FFT-accelerated convolution
2. Implement Gaussian approximation
3. Benchmark all three methods
4. Add to app with auto-selection
5. Test thoroughly with validation tab
    """)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PTM CHARGE DISTRIBUTION: ALGORITHM ANALYSIS & BENCHMARKING")
    print("="*70)
    
    # Theoretical analysis
    theoretical_analysis()
    
    # Benchmark Yergeev
    print("\n" + "="*70)
    print("EMPIRICAL PERFORMANCE TESTING")
    print("="*70)
    n_sites_to_test = [5, 10, 20, 30, 40, 50, 75, 100]
    results_df = benchmark_yergeev(n_sites_to_test)
    
    print("\nBenchmark Results Summary:")
    print(results_df.to_string(index=False))
    
    # Analyze scaling
    successful = results_df[results_df['status'] == 'success'].copy()
    if len(successful) >= 2:
        print("\nScaling Analysis:")
        for i in range(len(successful)-1):
            n1, t1 = successful.iloc[i][['n_sites', 'time_sec']]
            n2, t2 = successful.iloc[i+1][['n_sites', 'time_sec']]
            ratio_n = n2 / n1
            ratio_t = t2 / t1
            print(f"  {int(n1):3d} -> {int(n2):3d} sites: {ratio_n:.1f}x sites -> {ratio_t:.1f}x time")
    
    # Propose alternatives
    propose_alternatives()
    
    # Recommendation
    recommendation()
