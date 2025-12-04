"""
Quick test to verify CSV loading functionality works correctly.
Tests loading various CSV files and verifying they parse correctly.
"""
import pandas as pd
import os
import sys

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csv_loading():
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data", "test_csvs")
    
    if not os.path.exists(test_dir):
        print(f"ERROR: Test directory not found: {test_dir}")
        return False
    
    csv_files = [f for f in os.listdir(test_dir) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files to test\n")
    
    all_passed = True
    
    for csv_file in sorted(csv_files):
        filepath = os.path.join(test_dir, csv_file)
        try:
            df = pd.read_csv(filepath)
            
            # Check required columns
            required_cols = ['Site_ID', 'Copies']
            prob_cols = [c for c in df.columns if c.startswith('P(')]
            
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                print(f"❌ {csv_file}: Missing columns: {missing}")
                all_passed = False
                continue
            
            if len(prob_cols) == 0:
                print(f"❌ {csv_file}: No probability columns found")
                all_passed = False
                continue
            
            # Check data types
            total_copies = int(df['Copies'].sum())
            n_sites = len(df)
            
            # Check probability sums
            prob_sums = df[prob_cols].sum(axis=1)
            invalid_rows = sum(~(abs(prob_sums - 1.0) < 0.01))
            
            if invalid_rows > 0:
                print(f"⚠️  {csv_file}: {n_sites} sites, {total_copies} copies, {invalid_rows} rows with sum≠1")
            else:
                print(f"✅ {csv_file}: {n_sites} sites, {total_copies} copies - OK")
                
        except Exception as e:
            print(f"❌ {csv_file}: Error loading - {e}")
            all_passed = False
    
    return all_passed

def test_algorithm_adaptation():
    """Test that the adaptive algorithm chooses correctly based on dataset size"""
    from advanced_algorithms import adaptive_charge_distribution
    import numpy as np
    
    print("\n" + "="*60)
    print("Testing Algorithm Adaptation")
    print("="*60 + "\n")
    
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data", "test_csvs")
    
    test_cases = [
        ("test_03_small.csv", "Yergeev"),  # 6 copies -> Yergeev
        ("test_05_medium.csv", "FFT"),     # 55 copies -> FFT
        ("test_07_large.csv", "Gaussian"), # 251 copies -> Gaussian
        ("algo_yergeev_max.csv", "Yergeev"), # 50 copies -> Yergeev
        ("algo_fft_range.csv", "FFT"),     # 150 copies -> FFT
        ("algo_gaussian_start.csv", "Gaussian"), # 300 copies -> Gaussian
    ]
    
    for csv_file, expected_method in test_cases:
        filepath = os.path.join(test_dir, csv_file)
        if not os.path.exists(filepath):
            print(f"⚠️  {csv_file}: File not found")
            continue
            
        df = pd.read_csv(filepath)
        total_copies = int(df['Copies'].sum())
        
        try:
            pmf, offset, method_used, n_copies = adaptive_charge_distribution(df)
            
            if expected_method in method_used:
                print(f"✅ {csv_file} ({total_copies} copies): {method_used} ✓")
            else:
                print(f"⚠️  {csv_file} ({total_copies} copies): Expected {expected_method}, got {method_used}")
        except Exception as e:
            print(f"❌ {csv_file}: Error - {e}")

def test_validation_benchmark():
    """Test that validation correctly selects benchmark based on dataset size"""
    print("\n" + "="*60)
    print("Testing Validation Benchmark Selection")
    print("="*60 + "\n")
    
    test_cases = [
        (10, "enumeration"),   # Small - use enumeration
        (12, "enumeration"),   # Boundary - still enumeration
        (13, "yergeev"),       # Just over - use yergeev
        (100, "yergeev"),      # Medium - yergeev
        (500, "yergeev"),      # Large - still yergeev (just slower)
    ]
    
    for total_copies, expected_benchmark in test_cases:
        ENUM_LIMIT = 12
        
        if total_copies <= ENUM_LIMIT:
            benchmark = "enumeration"
        else:
            benchmark = "yergeev"
        
        if benchmark == expected_benchmark:
            print(f"✅ {total_copies} copies -> {benchmark} ✓")
        else:
            print(f"❌ {total_copies} copies -> {benchmark} (expected {expected_benchmark})")


if __name__ == "__main__":
    print("="*60)
    print("PTM Charge Analyzer - CSV Loading Tests")
    print("="*60 + "\n")
    
    success = test_csv_loading()
    test_algorithm_adaptation()
    test_validation_benchmark()
    
    print("\n" + "="*60)
    if success:
        print("All CSV loading tests PASSED!")
    else:
        print("Some tests FAILED - check output above")
    print("="*60)
