import pandas as pd
import glob
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
APP = os.path.join(ROOT, 'app', 'ptm_charge_input.py')

from ptm_helpers import generate_charge_columns, index_for_charge, neutral_index_for_range, auto_detect_charge_system

print('Loaded helpers:', True, True, True)

# Run autodetect on all CSVs in data/
DATA_DIR = os.path.join(ROOT, 'data')
for csv in sorted(glob.glob(os.path.join(DATA_DIR, '*.csv'))):
    print('\n== Testing', os.path.basename(csv), '==')
    try:
        df = pd.read_csv(csv)
        system, mn, mx = auto_detect_charge_system(df)
        print('Detected system:', system, mn, mx)
        # build columns
        cols = generate_charge_columns(mn, mx)
        print('Expected cols sample:', cols[:6], '... total', len(cols))
        # check index_for_charge and neutral index
        ni = neutral_index_for_range(mn, mx)
        print('Neutral index:', ni)
    except Exception as e:
        print('ERROR:', e)
