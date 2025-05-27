# enhanced_config.py
"""
Enhanced configuration file with improved styling and color schemes
"""

# Window settings
WINDOW_SIZE = "1600x900"
PADDING = 10

# Date column name
DATE_COL = 'Date'

# Column definitions
DROP_PRIMARY_COL = 'Drop (%)'
GAIN_PRIMARY_COL = 'Gain (%)'

REQUIRED_COLS_BASE = [DATE_COL, 'Type', 'Severity']
REQUIRED_COLUMNS_DROP = REQUIRED_COLS_BASE + [DROP_PRIMARY_COL]
REQUIRED_COLUMNS_GAIN = REQUIRED_COLS_BASE + [GAIN_PRIMARY_COL]

# Recovery periods
RECOVERY_PERIODS = [
    '1D (%)', '2D (%)', '3D (%)', '1W (%)', '1M (%)', 
    '3M (%)', '6M (%)', '1Y (%)', '3Y (%)'
]

# Market indicators
MARKET_INDICATORS = ['VIX', 'RSI', 'Volume', 'ATR']

# Optional columns
OPTIONAL_COLUMNS = MARKET_INDICATORS + RECOVERY_PERIODS + ['Total Avg (%)']

# Enhanced color schemes for different analysis modes
COLORS = {
    'drops': {
        'primary': '#e74c3c',      # Red
        'secondary': '#c0392b',    # Dark red
        'accent': '#f39c12',       # Orange
        'success': '#27ae60',      # Green
        'info': '#3498db',         # Blue
        'warning': '#f1c40f',      # Yellow
        'background': '#ecf0f1',   # Light gray
        'text': '#2c3e50'          # Dark blue-gray
    },
    'gains': {
        'primary': '#27ae60',      # Green
        'secondary': '#229954',    # Dark green
        'accent': '#3498db',       # Blue
        'success': '#1abc9c',      # Turquoise
        'info': '#9b59b6',         # Purple
        'warning': '#f39c12',      # Orange
        'background': '#ecf0f1',   # Light gray
        'text': '#2c3e50'          # Dark blue-gray
    }
}

# Plot styling
PLOT_STYLE = {
    'figure.figsize': (12, 8),
    'figure.dpi': 100,
    'figure.facecolor': 'white',
    'figure.edgecolor': 'none',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 1.0,
    'axes.grid': True,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelweight': 'normal',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'legend.frameon': True,
    'legend.fancybox': True,
    'legend.shadow': True,
    'legend.borderpad': 0.5,
    'legend.columnspacing': 1.0,
    'legend.loc': 'best',
    'lines.linewidth': 2,
    'lines.markersize': 8,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
    'font.size': 10
}

# GUI Theme settings
GUI_THEME = {
    'primary_bg': '#f5f6fa',
    'secondary_bg': '#ffffff',
    'accent_bg': '#e1e4e8',
    'primary_fg': '#2c3e50',
    'secondary_fg': '#7f8c8d',
    'accent_fg': '#3498db',
    'success_color': '#27ae60',
    'warning_color': '#f39c12',
    'error_color': '#e74c3c',
    'info_color': '#3498db',
    'border_color': '#dfe6e9',
    'hover_color': '#74b9ff',
    'selected_color': '#0984e3'
}

# Font settings
FONTS = {
    'default': ('Arial', 10),
    'heading': ('Arial', 12, 'bold'),
    'subheading': ('Arial', 11, 'bold'),
    'small': ('Arial', 9),
    'monospace': ('Courier', 10),
    'button': ('Arial', 10),
    'label': ('Arial', 10)
}

# Icon mappings
ICONS = {
    'drops': '📉',
    'gains': '📈',
    'timeline': '📊',
    'recovery': '🔄',
    'conditions': '🎯',
    'statistics': '📊',
    'correlation': '🔗',
    'probability': '🎲',
    'filter': '🔍',
    'settings': '⚙️',
    'export': '💾',
    'print': '🖨️',
    'refresh': '🔄',
    'load': '📁',
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'info': 'ℹ️'
}

# Visualization settings
VIZ_SETTINGS = {
    'timeline': {
        'scatter_size_scale': 30,
        'line_width': 2,
        'marker_edge_width': 0.5,
        'alpha': 0.6
    },
    'recovery': {
        'path_alpha': 0.15,
        'mean_line_width': 2,
        'confidence_alpha': 0.3
    },
    'statistics': {
        'histogram_bins': 30,
        'kde_bandwidth': 'scott',
        'bar_alpha': 0.7
    },
    'correlation': {
        'heatmap_cmap': 'coolwarm',
        'annotation_size': 8,
        'cell_line_width': 0.5
    }
}

# Export settings
EXPORT_SETTINGS = {
    'figure_dpi': 300,
    'figure_format': 'png',
    'bbox_inches': 'tight',
    'pdf_metadata': {
        'Title': 'Market Analysis Report',
        'Author': 'Market Analyzer',
        'Subject': 'Financial Market Event Analysis',
        'Keywords': 'market, analysis, drops, gains, statistics'
    }
}

# Analysis thresholds
ANALYSIS_THRESHOLDS = {
    'major_event': 5.0,      # Percentage threshold for major events
    'minor_event': 1.0,      # Percentage threshold for minor events
    'high_vix': 30.0,        # High volatility threshold
    'low_vix': 15.0,         # Low volatility threshold
    'oversold_rsi': 30.0,    # RSI oversold threshold
    'overbought_rsi': 70.0,  # RSI overbought threshold
    'volume_spike': 1.5      # Volume spike multiplier
}

# Time period definitions (in days)
TIME_PERIODS = {
    '1D': 1,
    '2D': 2,
    '3D': 3,
    '1W': 7,
    '1M': 30,
    '3M': 90,
    '6M': 180,
    '1Y': 365,
    '3Y': 1095
}

# Statistical analysis settings
STATS_SETTINGS = {
    'confidence_level': 0.95,
    'percentiles': [10, 25, 50, 75, 90],
    'correlation_threshold': 0.3,
    'min_sample_size': 30,
    'outlier_threshold': 3.0  # Standard deviations
}

# GUI Layout settings
LAYOUT_SETTINGS = {
    'sidebar_width': 350,
    'min_sidebar_width': 300,
    'max_sidebar_width': 500,
    'toolbar_height': 40,
    'status_bar_height': 60,
    'card_padding': 10,
    'section_spacing': 5,
    'button_spacing': 2
}

# Animation settings
ANIMATION_SETTINGS = {
    'transition_duration': 200,  # milliseconds
    'hover_delay': 100,
    'tooltip_delay': 500,
    'progress_update_interval': 100
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'max_plot_points': 10000,
    'chunk_size': 1000,
    'cache_size': 100,
    'update_delay': 50  # milliseconds
}