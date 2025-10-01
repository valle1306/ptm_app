# PTM Charge Variant Input Application

A user-friendly computational tool that efficiently and accurately estimates the distribution of charge variants would enable rapid, in silico assessment of potential charge heterogeneity.

## Features

### Data Input Options
1. **Manual Entry**: Add PTM sites one by one using the interactive table editor
2. **CSV Upload**: Upload existing PTM data from CSV files 
3. **Template Generation**: Generate N=100 site template for testing large datasets

### Input Format
The application expects data with the following columns:
- `Site_ID`: Identifier for each PTM site
- `Copies`: Number of copies per site (integer ≥ 1)
- `P(-2)`, `P(-1)`, `P(0)`, `P(+1)`, `P(+2)`: Probability values for each charge state

**Important**: Probability values for each row must sum to 1.0 (within tolerance).

### Computation
- Calculates overall protein charge distribution using convolution
- Supports multiple copies per site
- Handles large datasets (tested with N=100+ sites)
- Provides windowed output (±5 charges) and full distribution

## Usage

### Running the Application
```bash
streamlit run ptm_charge_input.py
```

### Using CSV Upload
1. Prepare a CSV file with the required columns
2. Use the file upload widget in the sidebar
3. Click "Load uploaded data" to import your data
4. Validate that all probability rows sum to 1.0
5. Compute the charge distribution

### Sample Data
A sample CSV file (`sample_ptm_n100.csv`) with 100 PTM sites is provided for testing.

## File Structure
```
ptm_app/
├── ptm_charge_input.py      # Main Streamlit application
├── sample_ptm_n100.csv      # Sample data (N=100 sites)
└── README.md                # This file
```

## Dependencies
- streamlit
- pandas
- numpy
- openpyxl (for Excel export)

## Testing with Large Datasets
The application has been optimized for large datasets. The N=100 template and sample CSV demonstrate performance with substantial data loads.
