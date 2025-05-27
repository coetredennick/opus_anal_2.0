"""
Enhanced Visualizations - Complete visualization methods with all features from example_app.py
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
import pandas as pd
import numpy as np
from tkinter import messagebox
from typing import Optional, List, Dict, Any
from datetime import datetime
from functools import wraps

from config import RECOVERY_PERIODS, MARKET_INDICATORS, COLORS, DATE_COL

# Error handling decorator

def handle_plot_errors(plot_name):
    """Decorator to handle errors in plotting functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                import traceback
                print(f"Plot error in {plot_name}: {e}")
                traceback.print_exc()
                self.fig.clear()
                ax = self.fig.add_subplot(111)
                ax.text(0.5, 0.5, f"Error in {plot_name}:\n{str(e)}",
                       ha='center', va='center', fontsize=12, 
                       color='red', wrap=True,
                       bbox=dict(boxstyle="round,pad=0.5", 
                                facecolor="mistyrose", alpha=0.8))
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                self.canvas.draw()
        return wrapper
    return decorator

class EnhancedVisualizations:
    """Enhanced visualization methods for the market analyzer"""
    
    def __init__(self, fig: Figure, canvas: FigureCanvasTkAgg):
        self.fig = fig
        self.canvas = canvas
        self._setup_style()
    
    def _setup_style(self) -> None:
        """Setup visualization style preferences"""
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams.update({
            'figure.facecolor': '#f0f0f0',
            'axes.facecolor': '#ffffff',
            'axes.edgecolor': '#cccccc',
            'grid.color': '#e0e0e0',
            'grid.alpha': 0.3,
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14,
            'figure.titleweight': 'bold'
        })
    
    def show_empty_plot(self, message: str = "No data to display") -> None:
        """Show empty plot with message"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, wrap=True,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dee2e6", alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()

    @handle_plot_errors("timeline visualization")
    def show_timeline(self, filtered_df: Optional[pd.DataFrame], analysis_mode: str, date_col: str = DATE_COL) -> None:
        self.fig.clear()
        if filtered_df is None or filtered_df.empty:
            self.show_empty_plot("No events available for timeline visualization")
            return
        colors = COLORS[analysis_mode]
        primary_col = 'Gain (%)' if analysis_mode == 'gains' else 'Drop (%)'
        df_plot = filtered_df.sort_values(by=date_col).copy()
        ax = self.fig.add_subplot(111)
        # Scatter plot of events over time
        if primary_col in df_plot.columns:
            sizes = np.abs(df_plot[primary_col]) * 30
            scatter = ax.scatter(df_plot[date_col], df_plot[primary_col],
                                 c=df_plot[primary_col], cmap='RdYlGn' if analysis_mode == 'gains' else 'RdYlBu_r',
                                 s=sizes, alpha=0.6, edgecolors='darkgray', linewidth=0.5)
            ax.set_ylabel(primary_col)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="2%", pad=0.1)
            cbar = self.fig.colorbar(scatter, cax=cax)
            cbar.set_label(f'{primary_col} Magnitude (%)', rotation=270, labelpad=20)
        else:
            ax.text(0.5, 0.5, f"No {primary_col} data", ha='center', va='center')
        ax.set_xlabel('Date')
        self._format_date_axis(ax, df_plot[date_col])
        self.fig.suptitle(f'Market {"Gains" if analysis_mode == "gains" else "Drops"} Timeline', fontsize=14, fontweight='bold')
        self.canvas.draw()

    @handle_plot_errors("statistics visualization")
    def show_statistics(self, filtered_df: Optional[pd.DataFrame], analysis_mode: str) -> None:
        self.fig.clear()
        if filtered_df is None or filtered_df.empty:
            self.show_empty_plot("No events available for statistical analysis")
            return
        colors = COLORS[analysis_mode]
        primary_col = 'Gain (%)' if analysis_mode == 'gains' else 'Drop (%)'
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
        # 1. Distribution
        ax1 = self.fig.add_subplot(gs[0, 0])
        self._plot_distribution(ax1, filtered_df, primary_col, colors)
        # 2. Temporal Analysis
        ax2 = self.fig.add_subplot(gs[0, 1])
        self._plot_temporal_analysis(ax2, filtered_df, primary_col, colors)
        # 3. Recovery Distribution (if available)
        ax3 = self.fig.add_subplot(gs[1, 0])
        available_recovery = [col for col in RECOVERY_PERIODS if col in filtered_df.columns and filtered_df[col].notna().any()]
        if available_recovery:
            sorted_cols, x_labels, x_ticks = self._prepare_recovery_data(available_recovery)
            recovery_data = filtered_df[sorted_cols]
            sns.boxplot(data=recovery_data, ax=ax3, palette='viridis', fliersize=2)
            ax3.set_xticklabels(x_labels, rotation=45, ha='right')
            ax3.set_title('Recovery Distribution')
            ax3.set_ylabel('Recovery (%)')
            ax3.grid(True, axis='y', alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No recovery data', ha='center', va='center')
        # 4. Summary text
        ax4 = self.fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        summary = f"Summary Statistics\n{'='*20}\n"
        summary += f"Total Events: {len(filtered_df)}\n"
        data = filtered_df[primary_col].dropna()
        summary += f"Mean {primary_col}: {data.mean():.2f}%\n"
        summary += f"Std Dev: {data.std():.2f}%\n"
        summary += f"Min: {data.min():.2f}%\n"
        summary += f"Max: {data.max():.2f}%\n"
        if 'VIX' in filtered_df.columns and filtered_df['VIX'].notna().any():
            summary += f"\nAvg VIX: {filtered_df['VIX'].mean():.2f}"
        if 'RSI' in filtered_df.columns and filtered_df['RSI'].notna().any():
            summary += f"\nAvg RSI: {filtered_df['RSI'].mean():.2f}"
        ax4.text(0.1, 0.9, summary, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        self.fig.suptitle(f'Statistical Analysis - {analysis_mode.capitalize()}', fontsize=14, fontweight='bold')
        self.canvas.draw()

    @handle_plot_errors("correlation analysis")
    def show_correlation_analysis(self, filtered_df: Optional[pd.DataFrame], analysis_mode: str) -> None:
        self.fig.clear()
        if filtered_df is None or filtered_df.empty:
            self.show_empty_plot("No events available for correlation analysis")
            return
        primary_col = 'Gain (%)' if analysis_mode == 'gains' else 'Drop (%)'
        ax = self.fig.add_subplot(111)
        self._plot_correlation_heatmap(ax, filtered_df, primary_col)
        self.fig.suptitle(f'Correlation Analysis - {analysis_mode.capitalize()}', fontsize=14, fontweight='bold')
        self.canvas.draw()

    @handle_plot_errors("recovery paths visualization")
    def show_recovery_paths(self, filtered_df: Optional[pd.DataFrame], analysis_mode: str) -> None:
        self.fig.clear()
        if filtered_df is None or filtered_df.empty:
            self.show_empty_plot("No events selected for recovery analysis.")
            return
        available_recovery = [col for col in RECOVERY_PERIODS if col in filtered_df.columns and filtered_df[col].notna().any()]
        if not available_recovery:
            self.show_empty_plot("No valid recovery data available for selected events.")
            return
        sorted_cols, x_labels, x_ticks = self._prepare_recovery_data(available_recovery)
        recovery_data = filtered_df[sorted_cols]
        gs = self.fig.add_gridspec(2, 2, height_ratios=[3, 2], width_ratios=[3, 2], hspace=0.4, wspace=0.3, top=0.9, bottom=0.15, left=0.1, right=0.95)
        # Plot 1: Individual & Average Recovery Paths
        ax1 = self.fig.add_subplot(gs[0, 0])
        for idx in range(len(recovery_data)):
            values = recovery_data.iloc[idx].values
            ax1.plot(x_ticks, values, color='grey', alpha=0.15, linewidth=1)
        mean_recovery = recovery_data.mean()
        std_recovery = recovery_data.std()
        ax1.plot(x_ticks, mean_recovery, 'royalblue', marker='o', markersize=5, linewidth=2, label='Average Recovery')
        ax1.fill_between(x_ticks, mean_recovery - std_recovery, mean_recovery + std_recovery, color='lightblue', alpha=0.4, label='Avg ± 1 Std Dev')
        ax1.set_xticks(x_ticks)
        ax1.set_xticklabels(x_labels, rotation=45, ha='right')
        ax1.set_ylabel('Recovery (%)')
        ax1.set_title('Recovery Paths')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(fontsize=8)
        ax1.axhline(0, color='k', linestyle=':', linewidth=1, alpha=0.5)
        # Plot 2: Recovery Distribution (Box Plot)
        ax2 = self.fig.add_subplot(gs[0, 1])
        sns.boxplot(data=recovery_data, ax=ax2, palette='viridis', fliersize=2)
        ax2.set_xticklabels(x_labels, rotation=45, ha='right')
        ax2.set_ylabel('Recovery (%) Distribution')
        ax2.set_title('Distribution per Period')
        ax2.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax2.axhline(0, color='k', linestyle=':', linewidth=1, alpha=0.5)
        # Plot 3: Success Rate (Bar Plot)
        ax3 = self.fig.add_subplot(gs[1, :])
        success_rates = (recovery_data > 0).mean() * 100
        bars = sns.barplot(x=x_labels, y=success_rates.values, ax=ax3, palette='Greens_d')
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_title('Positive Recovery Rate by Period')
        ax3.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax3.set_ylim(0, 105)
        for bar in bars.patches:
            ax3.annotate(f'{bar.get_height():.1f}%',
                       xy=(bar.get_x() + bar.get_width()/2., bar.get_height()),
                       xytext=(0, 3),
                       textcoords='offset points',
                       ha='center',
                       va='bottom',
                       fontsize=8)
        self.fig.suptitle('Post-Event Recovery Analysis', fontsize=14, fontweight='bold')
        self.canvas.draw()

    @handle_plot_errors("probability analysis")
    def show_probability_analysis(self, filtered_df: Optional[pd.DataFrame], analysis_mode: str) -> None:
        self.fig.clear()
        self.show_empty_plot("Probability analysis visualization not yet implemented in this version.")
        # You can implement this using your own probability/statistical helpers as needed.

    # Helper methods for enhanced visualizations
    def _plot_distribution(self, ax, df, col, colors):
        """Plot distribution histogram with KDE overlay"""
        if col not in df.columns or df[col].isna().all():
            ax.text(0.5, 0.5, f"No {col} data", ha='center', va='center')
            return
        data = df[col].dropna()
        sns.histplot(data=df, x=col, kde=True, ax=ax, 
                     color=colors['primary'], alpha=0.7, bins=20)
        mean_val = data.mean()
        median_val = data.median()
        ax.axvline(mean_val, color='red', linestyle='--', 
                   label=f'Mean: {mean_val:.2f}%', alpha=0.8)
        ax.axvline(median_val, color='green', linestyle='--', 
                   label=f'Median: {median_val:.2f}%', alpha=0.8)
        ax.set_title(f'{col} Distribution')
        ax.set_xlabel(col)
        ax.set_ylabel('Count')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_temporal_analysis(self, ax, df, col, colors):
        """Plot temporal analysis - events over time"""
        if 'Year' not in df.columns:
            df['Year'] = pd.to_datetime(df['Date']).dt.year
        yearly_stats = df.groupby('Year')[col].agg(['count', 'mean', 'std'])
        ax2 = ax.twinx()
        ax.bar(yearly_stats.index, yearly_stats['count'], 
               alpha=0.3, color=colors['secondary'], label='Count')
        ax2.errorbar(yearly_stats.index, yearly_stats['mean'], 
                     yerr=yearly_stats['std'], 
                     color=colors['primary'], marker='o', 
                     capsize=5, label='Mean ± Std')
        ax.set_xlabel('Year')
        ax.set_ylabel('Event Count', color=colors['secondary'])
        ax2.set_ylabel(f'Mean {col}', color=colors['primary'])
        ax.tick_params(axis='y', labelcolor=colors['secondary'])
        ax2.tick_params(axis='y', labelcolor=colors['primary'])
        ax.set_title('Temporal Analysis')
        ax.grid(True, alpha=0.3)
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    def _plot_correlation_heatmap(self, ax, df, primary_col):
        """Plot correlation heatmap for numeric columns"""
        numeric_cols = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().sum() > 10:
                numeric_cols.append(col)
        if len(numeric_cols) < 2:
            ax.text(0.5, 0.5, "Insufficient numeric data for correlation", 
                    ha='center', va='center')
            return
        corr_matrix = df[numeric_cols].corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                    cmap='coolwarm', center=0, vmin=-1, vmax=1,
                    ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Correlation Matrix')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), rotation=0)

    def _prepare_recovery_data(self, available_cols):
        """Prepare recovery data for plotting"""
        period_days = {
            '1D (%)': 1, '2D (%)': 2, '3D (%)': 3,
            '1W (%)': 7, '1M (%)': 30, '3M (%)': 90,
            '6M (%)': 180, '1Y (%)': 365, '3Y (%)': 1095
        }
        sorted_cols = sorted(available_cols, 
                            key=lambda x: period_days.get(x, float('inf')))
        x_labels = [col.replace(' (%)', '') for col in sorted_cols]
        x_ticks = list(range(len(sorted_cols)))
        return sorted_cols, x_labels, x_ticks

    def _format_date_axis(self, ax: plt.Axes, dates: pd.Series) -> None:
        """Format date axis based on date range"""
        date_range = dates.max() - dates.min()
        
        if date_range > pd.Timedelta(days=3*365):
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))
        elif date_range > pd.Timedelta(days=180):
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        else:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    def _handle_plot_error(self, context: str, exception: Exception) -> None:
        """Handle plotting errors gracefully"""
        import traceback
        print(f"Plot error in {context}: {exception}")
        traceback.print_exc()
        
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, f"Error creating {context} plot:\n{str(exception)[:100]}...",
               ha='center', va='center', fontsize=10, color='red',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffe6e6", alpha=0.8))
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()