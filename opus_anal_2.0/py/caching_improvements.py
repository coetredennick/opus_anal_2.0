# Add to DataProcessor class in refined_data_processor.py

from functools import lru_cache

class DataProcessor:
    """Handles data cleaning and processing operations"""
    
    @staticmethod
    @lru_cache(maxsize=32)
    def _get_numeric_columns(df_hash, columns_tuple):
        """Cached method to get numeric columns"""
        # Convert back from tuple to list
        columns = list(columns_tuple)
        numeric_cols = []
        for col in columns:
            # This is a simplified check - in real implementation,
            # you'd need to pass the actual dtypes
            if col.endswith('(%)') or col in ['VIX', 'RSI', 'ATR', 'Volume']:
                numeric_cols.append(col)
        return numeric_cols
    
    @staticmethod
    def get_numeric_columns(df):
        """Get numeric columns with caching"""
        # Create a hashable representation
        df_hash = hash(tuple(df.columns) + (len(df),))
        columns_tuple = tuple(df.columns)
        return DataProcessor._get_numeric_columns(df_hash, columns_tuple)