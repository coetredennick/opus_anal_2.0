# data_detector.py
import pandas as pd
import os
from typing import Dict, List, Tuple, Optional
import re

from config import ( # Assuming these are defined in config.py
    DATE_COL, REQUIRED_COLS_BASE, DROP_PRIMARY_COL, GAIN_PRIMARY_COL,
    REQUIRED_COLUMNS_DROP, REQUIRED_COLUMNS_GAIN, OPTIONAL_COLUMNS
)


class DataTypeDetector:
    @staticmethod
    def detect_data_type_from_columns(columns: List[str]) -> str:
        has_drop_col = DROP_PRIMARY_COL in columns
        has_gain_col = GAIN_PRIMARY_COL in columns

        if has_drop_col and has_gain_col:
            return 'drops' 
        elif has_drop_col:
            return 'drops'
        elif has_gain_col:
            return 'gains'
        else:
            return 'unknown'

    @staticmethod
    def validate_csv_structure(file_path: str, df: Optional[pd.DataFrame] = None) -> Dict[str, any]: #
        results = {
            'file_path': file_path,
            'filename': os.path.basename(file_path), #
            'valid': False, #
            'data_type': 'unknown', #
            'issues': [], #
            'present_cols': [],
            'missing_req_cols': [],
            'missing_opt_cols': [],
        }

        try:
            if df is None:
                try:
                    df_sample = pd.read_csv(file_path, nrows=5) #
                except pd.errors.EmptyDataError:
                    results['issues'].append("File is empty or not a valid CSV.")
                    return results
                except Exception as e:
                    results['issues'].append(f"Error reading CSV: {str(e)}")
                    return results
            else:
                df_sample = df.head() 

            results['present_cols'] = list(df_sample.columns)
            
            detected_type = DataTypeDetector.detect_data_type_from_columns(results['present_cols'])
            results['data_type'] = detected_type #

            if detected_type == 'unknown': #
                results['issues'].append(f"Could not determine data type: Missing '{DROP_PRIMARY_COL}' or '{GAIN_PRIMARY_COL}'.") #
                required_cols_check = REQUIRED_COLS_BASE
            elif detected_type == 'drops':
                required_cols_check = REQUIRED_COLUMNS_DROP
            else: 
                required_cols_check = REQUIRED_COLUMNS_GAIN

            missing_required = [col for col in required_cols_check if col not in results['present_cols']]
            if missing_required:
                results['issues'].append(f"Missing required columns for {detected_type} data: {', '.join(missing_required)}") #
                results['missing_req_cols'] = missing_required
            
            if DATE_COL in results['present_cols']: #
                try:
                    # Attempt to parse the date column to check for validity
                    # For performance on large files, this check on a sample is okay for UI feedback
                    # More robust parsing happens in DataProcessor on the full dataset
                    if not df_sample[DATE_COL].empty:
                         pd.to_datetime(df_sample[DATE_COL], errors='raise')
                except Exception:
                    results['issues'].append(f"Column '{DATE_COL}' does not appear to contain valid dates (YYYY-MM-DD recommended).") #
            
            missing_optional = [col for col in OPTIONAL_COLUMNS if col not in results['present_cols']] #
            results['missing_opt_cols'] = missing_optional #
            if missing_optional and not missing_required: 
                 results['issues'].append(f"Missing optional columns: {', '.join(missing_optional[:3])}{'...' if len(missing_optional) > 3 else ''}. This is not an error.") #


            if not results['issues'] or all("optional columns" in issue for issue in results['issues']):
                if not missing_required:
                    results['valid'] = True #

        except Exception as e:
            results['issues'].append(f"An unexpected error occurred during validation: {str(e)}")
            results['valid'] = False #
            
        return results

    @staticmethod
    def extract_index_symbols(filename: str) -> List[str]: #
        known_symbols_map = {
            "GSPC": "^GSPC", "SPX": "^GSPC", "SP500": "^GSPC",
            "DJI": "^DJI", "DOWJONES": "^DJI",
            "IXIC": "^IXIC", "NASDAQ": "^IXIC",
            "RUT": "^RUT", "RUSSELL2000": "^RUT"
        }
        
        filename_upper = filename.upper()
        found_symbols = set()

        caret_symbols = re.findall(r'\^([A-Z0-9_.-]+)|([A-Z0-9_.-]+)\^', filename)
        for sym_tuple in caret_symbols:
            for sym in sym_tuple:
                if sym:
                    found_symbols.add(f"^{sym}" if not sym.startswith('^') else sym)

        for keyword, symbol_ticker in known_symbols_map.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', filename_upper):
                found_symbols.add(symbol_ticker)
        
        if found_symbols:
            return sorted(list(found_symbols))

        parts = re.split(r'[_.\- ]+', os.path.splitext(filename)[0])
        potential = [part for part in parts if part.isalpha() and len(part) > 1 and part.upper() not in ['CSV', 'DATA', 'DROPS', 'GAINS', 'ANALYSIS', 'INDEX']]
        
        if potential:
            return sorted(list(set(p.upper() for p in potential))) 

        return []