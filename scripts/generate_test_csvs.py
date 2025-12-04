"""
Generate multiple test CSV files with varying sizes to test algorithm adaptation
and CSV loading functionality.

Creates test cases:
1. Minimal: 1 site, 1 copy
2. Tiny: 3 sites, 1 copy each (3 total)
3. Small: 5 sites, 1-2 copies (7 total) - enumeration feasible
4. Medium-Small: 10 sites, 1-2 copies (15 total) - yergeev range
5. Medium: 20 sites, 2-3 copies (50 total) - yergeev/FFT boundary
6. Medium-Large: 50 sites, 2-3 copies (120 total) - FFT range
7. Large: 100 sites, 2-3 copies (250 total) - Gaussian range
8. Very Large: 200 sites, 2-5 copies (600 total) - Gaussian
9. Extreme: 500 sites, 1-10 copies (2500+ total) - Stress test
10. Single high copies: 1 site, 100 copies - Edge case

Also creates edge cases:
- All neutral (P(0)=1.0)
- All negative (high P(-2))
- All positive (high P(+2))
- Uniform distribution
- Skewed distribution
"""

import pandas as pd
import numpy as np
import os

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "test_csvs")
os.makedirs(output_dir, exist_ok=True)

def generate_csv(name, n_sites, copy_range, prob_type="varied"):
    """
    Generate a test CSV file with specified parameters.
    
    Args:
        name: Output filename (without .csv)
        n_sites: Number of PTM sites
        copy_range: Tuple of (min_copies, max_copies) or single int
        prob_type: "neutral", "negative", "positive", "uniform", "varied", "random"
    """
    if isinstance(copy_range, int):
        copy_range = (copy_range, copy_range)
    
    rows = []
    for i in range(1, n_sites + 1):
        copies = np.random.randint(copy_range[0], copy_range[1] + 1)
        
        # Generate probabilities based on type
        if prob_type == "neutral":
            probs = [0.0, 0.0, 1.0, 0.0, 0.0]  # P(-2), P(-1), P(0), P(+1), P(+2)
        elif prob_type == "negative":
            probs = [0.3, 0.4, 0.2, 0.1, 0.0]
        elif prob_type == "positive":
            probs = [0.0, 0.1, 0.2, 0.4, 0.3]
        elif prob_type == "uniform":
            probs = [0.2, 0.2, 0.2, 0.2, 0.2]
        elif prob_type == "random":
            probs = np.random.random(5)
            probs = probs / probs.sum()
            probs = probs.tolist()
        else:  # varied - mix of patterns
            pattern = i % 5
            if pattern == 0:
                probs = [0.0, 0.0, 1.0, 0.0, 0.0]  # neutral
            elif pattern == 1:
                probs = [0.0, 0.2, 0.6, 0.2, 0.0]  # centered
            elif pattern == 2:
                probs = [0.1, 0.2, 0.4, 0.2, 0.1]  # symmetric spread
            elif pattern == 3:
                probs = [0.0, 0.3, 0.5, 0.15, 0.05]  # slight negative
            else:
                probs = [0.05, 0.15, 0.5, 0.3, 0.0]  # slight positive
        
        rows.append([f"Site_{i}", copies] + probs)
    
    columns = ["Site_ID", "Copies", "P(-2)", "P(-1)", "P(0)", "P(+1)", "P(+2)"]
    df = pd.DataFrame(rows, columns=columns)
    
    # Calculate total copies
    total_copies = df['Copies'].sum()
    
    filepath = os.path.join(output_dir, f"{name}.csv")
    df.to_csv(filepath, index=False)
    print(f"Created: {name}.csv ({n_sites} sites, {total_copies} total copies)")
    return filepath


def main():
    np.random.seed(42)  # For reproducibility
    
    print("=" * 60)
    print("Generating test CSV files for PTM Charge Analyzer")
    print("=" * 60)
    print()
    
    # Standard test cases (varying sizes)
    print("=== Size Variations ===")
    generate_csv("test_01_minimal", n_sites=1, copy_range=1)
    generate_csv("test_02_tiny", n_sites=3, copy_range=1)
    generate_csv("test_03_small", n_sites=5, copy_range=(1, 2))
    generate_csv("test_04_medium_small", n_sites=10, copy_range=(1, 2))
    generate_csv("test_05_medium", n_sites=20, copy_range=(2, 3))
    generate_csv("test_06_medium_large", n_sites=50, copy_range=(2, 3))
    generate_csv("test_07_large", n_sites=100, copy_range=(2, 3))
    generate_csv("test_08_very_large", n_sites=200, copy_range=(2, 5))
    generate_csv("test_09_extreme", n_sites=500, copy_range=(1, 10))
    
    print()
    print("=== Edge Cases ===")
    # Edge cases
    generate_csv("edge_single_high_copies", n_sites=1, copy_range=100)
    generate_csv("edge_many_single_copies", n_sites=200, copy_range=1)
    
    print()
    print("=== Probability Distributions ===")
    # Different probability distributions
    generate_csv("prob_all_neutral", n_sites=20, copy_range=(1, 3), prob_type="neutral")
    generate_csv("prob_all_negative", n_sites=20, copy_range=(1, 3), prob_type="negative")
    generate_csv("prob_all_positive", n_sites=20, copy_range=(1, 3), prob_type="positive")
    generate_csv("prob_uniform", n_sites=20, copy_range=(1, 3), prob_type="uniform")
    generate_csv("prob_random", n_sites=20, copy_range=(1, 3), prob_type="random")
    
    print()
    print("=== Enumeration Threshold Tests ===")
    # Specifically around enumeration threshold (12 copies)
    generate_csv("enum_boundary_10copies", n_sites=10, copy_range=1)
    generate_csv("enum_boundary_12copies", n_sites=12, copy_range=1)
    generate_csv("enum_boundary_13copies", n_sites=13, copy_range=1)
    generate_csv("enum_boundary_15copies", n_sites=15, copy_range=1)
    
    print()
    print("=== Algorithm Threshold Tests ===")
    # Around algorithm switching thresholds
    generate_csv("algo_yergeev_max", n_sites=25, copy_range=2)  # ~50 copies
    generate_csv("algo_fft_range", n_sites=50, copy_range=3)    # ~150 copies
    generate_csv("algo_gaussian_start", n_sites=100, copy_range=3)  # ~300 copies
    
    print()
    print("=" * 60)
    print(f"All test files created in: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
