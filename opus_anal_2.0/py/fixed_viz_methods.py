def _plot_distribution(self, ax, df, col, colors):
    """Plot distribution histogram with KDE overlay"""
    if col not in df.columns or df[col].isna().all():
        ax.text(0.5, 0.5, f"No {col} data", ha='center', va='center')
        return
    
    data = df[col].dropna()
    
    # Histogram with KDE
    sns.histplot(data=df, x=col, kde=True, ax=ax, 
                 color=colors['primary'], alpha=0.7, bins=20)
    
    # Add statistics
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
    
    # Create twin axis for count
    ax2 = ax.twinx()
    
    # Plot count as bars
    ax.bar(yearly_stats.index, yearly_stats['count'], 
           alpha=0.3, color=colors['secondary'], label='Count')
    
    # Plot mean with error bars
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
    
    # Combine legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

def _plot_correlation_heatmap(self, ax, df, primary_col):
    """Plot correlation heatmap for numeric columns"""
    # Select numeric columns
    numeric_cols = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().sum() > 10:
            numeric_cols.append(col)
    
    if len(numeric_cols) < 2:
        ax.text(0.5, 0.5, "Insufficient numeric data for correlation", 
                ha='center', va='center')
        return
    
    # Calculate correlation
    corr_matrix = df[numeric_cols].corr()
    
    # Create mask for upper triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Plot heatmap
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                cmap='coolwarm', center=0, vmin=-1, vmax=1,
                ax=ax, cbar_kws={'label': 'Correlation'})
    
    ax.set_title('Correlation Matrix')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax.get_yticklabels(), rotation=0)

def _plot_indicator_correlation(self, ax, df, indicator, primary_col, colors):
    """Plot scatter plot with regression line for indicator vs primary metric"""
    if indicator not in df.columns or primary_col not in df.columns:
        ax.text(0.5, 0.5, f"Missing data for {indicator}", 
                ha='center', va='center')
        return
    
    # Remove NaN values
    plot_df = df[[indicator, primary_col]].dropna()
    
    if len(plot_df) < 3:
        ax.text(0.5, 0.5, f"Insufficient data for {indicator}", 
                ha='center', va='center')
        return
    
    # Create scatter plot with regression
    sns.regplot(data=plot_df, x=indicator, y=primary_col,
                ax=ax, scatter_kws={'alpha': 0.6, 's': 30},
                line_kws={'color': 'red', 'linewidth': 2})
    
    # Calculate correlation
    corr = plot_df[indicator].corr(plot_df[primary_col])
    
    ax.set_title(f'{primary_col} vs {indicator}\n(r = {corr:.3f})')
    ax.set_xlabel(indicator)
    ax.set_ylabel(primary_col)
    ax.grid(True, alpha=0.3)

def _plot_detailed_correlation(self, ax, corr_matrix, primary_col):
    """Plot detailed correlation matrix with annotations"""
    # Create annotated heatmap
    sns.heatmap(corr_matrix, annot=True, fmt='.2f',
                cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                ax=ax, square=True, linewidths=0.5,
                cbar_kws={'label': 'Correlation Coefficient'})
    
    # Highlight primary column
    if primary_col in corr_matrix.columns:
        col_idx = list(corr_matrix.columns).index(primary_col)
        ax.add_patch(plt.Rectangle((col_idx, 0), 1, len(corr_matrix),
                                  fill=False, edgecolor='green', lw=3))
        ax.add_patch(plt.Rectangle((0, col_idx), len(corr_matrix), 1,
                                  fill=False, edgecolor='green', lw=3))
    
    ax.set_title('Detailed Correlation Analysis')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax.get_yticklabels(), rotation=0)

def _prepare_recovery_data(self, available_cols):
    """Prepare recovery data for plotting"""
    # Map period names to days for sorting
    period_days = {
        '1D (%)': 1, '2D (%)': 2, '3D (%)': 3,
        '1W (%)': 7, '1M (%)': 30, '3M (%)': 90,
        '6M (%)': 180, '1Y (%)': 365, '3Y (%)': 1095
    }
    
    # Sort columns by days
    sorted_cols = sorted(available_cols, 
                        key=lambda x: period_days.get(x, float('inf')))
    
    # Create labels without percentage signs
    x_labels = [col.replace(' (%)', '') for col in sorted_cols]
    
    # Create tick positions
    x_ticks = list(range(len(sorted_cols)))
    
    return sorted_cols, x_labels, x_ticks