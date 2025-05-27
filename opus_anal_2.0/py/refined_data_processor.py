"""
Data Processor - Handles data cleaning, processing, and statistics generation
"""

import pandas as pd
import numpy as np
from tkinter import messagebox
from typing import Optional, List, Dict, Tuple
from config import DATE_COL, MARKET_INDICATORS, RECOVERY_PERIODS
from functools import lru_cache  # Added for caching improvements


class DataProcessor:
    """Handles data cleaning and processing operations"""
    
    # Cache for performance
    _numeric_columns_cache = {}
    
    @staticmethod
    @lru_cache(maxsize=32)
    def _get_numeric_columns(df_hash, columns_tuple):
        """Cached method to get numeric columns"""
        columns = list(columns_tuple)
        numeric_cols = []
        for col in columns:
            if col.endswith('(%)') or col in ['VIX', 'RSI', 'ATR', 'Volume']:
                numeric_cols.append(col)
        return numeric_cols

    @staticmethod
    def get_numeric_columns(df):
        """Get numeric columns with caching"""
        df_hash = hash(tuple(df.columns) + (len(df),))
        columns_tuple = tuple(df.columns)
        return DataProcessor._get_numeric_columns(df_hash, columns_tuple)
    
    @staticmethod
    def clean_data(df: pd.DataFrame, data_type: str) -> Optional[pd.DataFrame]:
        """
        Clean and validate data
        
        Args:
            df: Raw dataframe
            data_type: 'drops' or 'gains'
            
        Returns:
            Cleaned dataframe or None if validation fails
        """
        try:
            cleaned_df = df.copy()
            primary_col = 'Gain (%)' if data_type == 'gains' else 'Drop (%)'
            
            # Validate required columns
            required_cols = [DATE_COL, primary_col]
            missing_cols = [col for col in required_cols if col not in cleaned_df.columns]
            
            if missing_cols:
                messagebox.showerror(
                    "Data Error", 
                    f"Required columns missing: {', '.join(missing_cols)}"
                )
                return None
            
            # Clean date column
            cleaned_df = DataProcessor._clean_date_column(cleaned_df)
            if cleaned_df is None or cleaned_df.empty:
                return None
            
            # Convert numeric columns
            cleaned_df = DataProcessor._convert_numeric_columns(cleaned_df, primary_col)
            
            # Validate primary column has data
            if cleaned_df[primary_col].isnull().all():
                messagebox.showerror(
                    "Data Error", 
                    f"'{primary_col}' contains no valid numeric data."
                )
                return None
            
            # Remove rows with invalid primary values
            cleaned_df = cleaned_df.dropna(subset=[primary_col])
            
            if cleaned_df.empty:
                messagebox.showwarning(
                    "Warning", 
                    "No valid data rows remaining after cleaning."
                )
                return None
            
            # Sort by date
            cleaned_df = cleaned_df.sort_values(by=DATE_COL).reset_index(drop=True)
            
            # Add derived columns if they don't exist
            cleaned_df = DataProcessor._add_derived_columns(cleaned_df, data_type)
            
            return cleaned_df

        except Exception as e:
            messagebox.showerror(
                "Data Cleaning Error", 
                f"Error cleaning data:\n{str(e)}"
            )
            return None

    @staticmethod
    def _clean_date_column(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Clean and validate date column"""
        try:
            # Try multiple date formats
            date_formats = [None, '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
            
            for fmt in date_formats:
                try:
                    if fmt:
                        df[DATE_COL] = pd.to_datetime(df[DATE_COL], format=fmt, errors='coerce')
                    else:
                        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors='coerce')
                    
                    # Check if we got valid dates
                    valid_dates = df[DATE_COL].notna().sum()
                    if valid_dates > 0:
                        break
                except:
                    continue
            
            # Remove rows with invalid dates
            df = df.dropna(subset=[DATE_COL])
            
            if df.empty:
                messagebox.showwarning(
                    "Data Warning", 
                    "No valid date entries found. Check date format (YYYY-MM-DD recommended)."
                )
                return None
                
            return df
            
        except Exception as e:
            messagebox.showerror("Date Error", f"Error processing dates: {str(e)}")
            return None

    @staticmethod
    def _convert_numeric_columns(df: pd.DataFrame, primary_col: str) -> pd.DataFrame:
        """Convert numeric columns to appropriate types"""
        # Define all possible numeric columns
        numeric_cols = [primary_col] + MARKET_INDICATORS + RECOVERY_PERIODS + ['Volume', 'Total Avg (%)']
        
        for col in numeric_cols:
            if col in df.columns:
                # Handle percentage strings (e.g., "3.45%" -> 3.45)
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace('%', '').str.strip()
                
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df

    @staticmethod
    def _add_derived_columns(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Add useful derived columns"""
        primary_col = 'Gain (%)' if data_type == 'gains' else 'Drop (%)'
        
        # Add year and month for grouping
        df['Year'] = df[DATE_COL].dt.year
        df['Month'] = df[DATE_COL].dt.month
        df['Quarter'] = df[DATE_COL].dt.quarter
        
        # Add magnitude category
        magnitudes = df[primary_col].abs()
        df['Magnitude Category'] = pd.cut(
            magnitudes,
            bins=[0, 1, 2, 3, 5, 100],
            labels=['< 1%', '1-2%', '2-3%', '3-5%', '> 5%']
        )
        
        # Calculate average recovery if we have recovery columns
        recovery_cols = [col for col in RECOVERY_PERIODS if col in df.columns]
        if recovery_cols:
            df['Avg Recovery'] = df[recovery_cols].mean(axis=1)
        
        return df

    @staticmethod
    def generate_summary_stats(df: Optional[pd.DataFrame], analysis_mode: str) -> str:
        """
        Generate comprehensive summary statistics for current data
        
        Args:
            df: Dataframe to analyze
            analysis_mode: 'gains' or 'drops'
            
        Returns:
            Formatted statistics string
        """
        if df is None or df.empty:
            return "No data available for statistics."

        primary_col = 'Gain (%)' if analysis_mode == 'gains' else 'Drop (%)'
        event_name = "Gain" if analysis_mode == "gains" else "Drop"
        
        stats = []
        
        # Date range
        date_range = f"{df[DATE_COL].min().strftime('%Y-%m-%d')} to {df[DATE_COL].max().strftime('%Y-%m-%d')}"
        stats.append(f"Date Range: {date_range}")
        stats.append("")
        
        # Primary metric statistics
        stats.extend(DataProcessor._get_primary_stats(df, primary_col, event_name))
        
        # Recovery statistics
        stats.extend(DataProcessor._get_recovery_stats(df))
        
        # Market conditions statistics
        stats.extend(DataProcessor._get_market_condition_stats(df))
        
        return "\n".join(stats)

    @staticmethod
    def _get_primary_stats(df: pd.DataFrame, primary_col: str, event_name: str) -> List[str]:
        """Get primary metric statistics"""
        stats = []
        
        if primary_col in df.columns and df[primary_col].notna().any():
            data = df[primary_col].dropna()
            
            stats.append(f"{event_name} Statistics:")
            stats.append(f"  Count: {len(data)} events")
            stats.append(f"  Mean: {data.mean():.2f}% (σ = {data.std():.2f}%)")
            stats.append(f"  Median: {data.median():.2f}%")
            stats.append(f"  Range: {data.min():.2f}% to {data.max():.2f}%")
            
            # Percentiles
            percentiles = [10, 25, 75, 90]
            pct_values = [data.quantile(p/100) for p in percentiles]
            pct_str = ", ".join([f"{p}th: {v:.2f}%" for p, v in zip(percentiles, pct_values)])
            stats.append(f"  Percentiles: {pct_str}")
            
            # Frequency by magnitude
            if 'Magnitude Category' in df.columns:
                stats.append("")
                stats.append("  By Magnitude:")
                for cat in df['Magnitude Category'].cat.categories:
                    count = (df['Magnitude Category'] == cat).sum()
                    pct = count / len(df) * 100
                    stats.append(f"    {cat}: {count} events ({pct:.1f}%)")
        
        return stats

    @staticmethod
    def _get_recovery_stats(df: pd.DataFrame) -> List[str]:
        """Get recovery period statistics"""
        stats = []
        stats.append("")
        stats.append("Recovery Analysis:")
        
        recovery_data = []
        for period in RECOVERY_PERIODS:
            if period in df.columns and df[period].notna().any():
                period_data = df[period].dropna()
                if len(period_data) > 0:
                    recovery_data.append({
                        'period': period.replace(' (%)', ''),
                        'mean': period_data.mean(),
                        'median': period_data.median(),
                        'success_rate': (period_data > 0).mean() * 100,
                        'count': len(period_data)
                    })
        
        if recovery_data:
            # Sort by period order
            period_order = ['1D', '2D', '3D', '1W', '1M', '3M', '6M', '1Y', '3Y']
            recovery_data.sort(key=lambda x: period_order.index(x['period']) 
                              if x['period'] in period_order else 999)
            
            for data in recovery_data:
                stats.append(
                    f"  {data['period']}: "
                    f"μ={data['mean']:.2f}%, "
                    f"Success={data['success_rate']:.1f}% "
                    f"(n={data['count']})"
                )
        else:
            stats.append("  No recovery data available")
        
        return stats

    @staticmethod
    def _get_market_condition_stats(df: pd.DataFrame) -> List[str]:
        """Get market condition statistics"""
        stats = []
        stats.append("")
        stats.append("Market Conditions:")
        
        has_conditions = False
        for indicator in MARKET_INDICATORS:
            if indicator in df.columns and df[indicator].notna().any():
                has_conditions = True
                data = df[indicator].dropna()
                stats.append(
                    f"  {indicator}: "
                    f"μ={data.mean():.1f}, "
                    f"σ={data.std():.1f}, "
                    f"Range=[{data.min():.1f}, {data.max():.1f}]"
                )
        
        if not has_conditions:
            stats.append("  No market condition data available")
        
        return stats

    @staticmethod
    def calculate_correlations(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Calculate correlation matrix for specified columns"""
        available_cols = [col for col in columns if col in df.columns]
        
        if len(available_cols) < 2:
            return pd.DataFrame()
        
        return df[available_cols].corr()

    @staticmethod
    def get_event_details(df: pd.DataFrame, index: int) -> Dict[str, any]:
        """Get detailed information for a specific event"""
        if index < 0 or index >= len(df):
            return {}
        
        row = df.iloc[index]
        details = {}
        
        # Basic info
        for col in df.columns:
            value = row[col]
            if pd.notna(value):
                if isinstance(value, (int, float)):
                    details[col] = f"{value:.2f}" if col.endswith('(%)') else str(value)
                elif isinstance(value, pd.Timestamp):
                    details[col] = value.strftime('%Y-%m-%d')
                else:
                    details[col] = str(value)
        
        return details