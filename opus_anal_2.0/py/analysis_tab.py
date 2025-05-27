# enhanced_analysis_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
from typing import List, Optional, Dict
import numpy as np

from config import DATE_COL, PADDING
from refined_data_processor import DataProcessor
from data_detector import DataTypeDetector
from refined_visualizations import EnhancedVisualizations

# Import the enhanced visualizations
# from enhanced_visualizations import EnhancedVisualizations

class EnhancedAnalysisTab:
    def __init__(self, root: tk.Tk, parent_frame: ttk.Frame, index_name: str, initial_files: Optional[List[str]] = None):
        self.root = root
        self.parent_frame = parent_frame
        self.index_name = index_name
        self.data_processor = DataProcessor()
        
        # Data storage
        self.raw_df_drops: Optional[pd.DataFrame] = None
        self.raw_df_gains: Optional[pd.DataFrame] = None
        self.processed_df_drops: Optional[pd.DataFrame] = None
        self.processed_df_gains: Optional[pd.DataFrame] = None
        
        self.current_analysis_mode = 'drops'
        self.current_filters: Dict[str, any] = {}
        self.filtered_df: Optional[pd.DataFrame] = None
        self.current_viz_type = None

        # Create enhanced UI
        self._setup_enhanced_ui()
        
        # Initialize visualizations with enhanced version
        self.visualizations = EnhancedVisualizations(self.fig, self.canvas)

        # Load initial files if provided
        if initial_files:
            for file_path in initial_files:
                self._load_data_file(file_path)

    def _setup_enhanced_ui(self) -> None:
        """Setup enhanced UI with better organization and aesthetics"""
        # Configure styles
        self._configure_styles()
        
        # Main container with gradient-like background
        main_container = ttk.Frame(self.parent_frame, style='Main.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Enhanced status bar with more info
        self._create_enhanced_status_bar(main_container)
        
        # Create notebook for better organization
        self.main_notebook = ttk.Notebook(main_container, style='Enhanced.TNotebook')
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Analysis Dashboard (now the only tab for analysis and filters)
        self.analysis_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.analysis_frame, text=' 📊 Analysis Dashboard ')
        self._create_analysis_dashboard()
        
        # Tab 2: Statistics & Reports
        self.stats_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.stats_frame, text=' 📈 Statistics ')
        self._create_statistics_tab()

    def _configure_styles(self):
        """Configure custom styles for enhanced aesthetics"""
        style = ttk.Style()
        
        # Main frame style
        style.configure('Main.TFrame', background='#f5f5f5')
        
        # Enhanced notebook style
        style.configure('Enhanced.TNotebook', background='#e0e0e0', tabposition='n')
        style.configure('Enhanced.TNotebook.Tab', padding=[20, 10], font=('Arial', 10))
        
        # Card-like frames
        style.configure('Card.TFrame', background='white', relief='flat', borderwidth=1)
        style.configure('Card.TLabel', background='white', font=('Arial', 10))
        
        # Enhanced buttons
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', font=('Arial', 10))
        style.configure('Info.TButton', font=('Arial', 10))

    def _create_enhanced_status_bar(self, parent):
        """Create enhanced status bar with more information"""
        status_container = ttk.Frame(parent, style='Card.TFrame')
        status_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side: Status and data info
        left_frame = ttk.Frame(status_container)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        self.status_label = ttk.Label(left_frame, text=f"📍 {self.index_name}: Ready", 
                                     font=('Arial', 11, 'bold'))
        self.status_label.pack(side=tk.TOP, anchor=tk.W)
        
        self.data_info_label = ttk.Label(left_frame, text="No data loaded", 
                                        font=('Arial', 9), foreground='gray')
        self.data_info_label.pack(side=tk.TOP, anchor=tk.W)
        
        # Right side: Action buttons
        right_frame = ttk.Frame(status_container)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        ttk.Button(right_frame, text="📁 Load Data", command=self._browse_data,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(right_frame, text="♻️ Refresh", command=self._refresh_analysis,
                  style='Info.TButton').pack(side=tk.LEFT, padx=2)

    def _create_analysis_dashboard(self):
        """Create the main analysis dashboard"""
        # Create paned window for resizable sections
        paned = ttk.PanedWindow(self.analysis_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Controls and filters (now scrollable and condensed)
        left_panel_width = 320
        left_panel_container = ttk.Frame(paned, width=left_panel_width)
        paned.add(left_panel_container, weight=1)
        
        # Make left panel scrollable
        canvas = tk.Canvas(left_panel_container, borderwidth=0, background="#f5f5f5", width=left_panel_width)
        scrollbar = ttk.Scrollbar(left_panel_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Improved mouse wheel/trackpad scrolling support
        def _on_mousewheel(event):
            # For Windows and MacOS
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _on_mousewheel_linux(event):
            # For Linux
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel_linux)
            canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        # Controls and filters in scrollable_frame
        self._create_quick_controls(scrollable_frame)
        self._create_threshold_filters(scrollable_frame, condensed=True)
        self._create_recovery_filters(scrollable_frame, condensed=True)
        self._create_market_condition_filters(scrollable_frame, condensed=True)
        self._create_temporal_filters(scrollable_frame, condensed=True)
        ttk.Button(scrollable_frame, text="🔍 Apply Filters", 
                   command=self._apply_filters_and_update,
                   style='Primary.TButton').pack(fill=tk.X, padx=6, pady=6)
        self._create_event_list(scrollable_frame)
        
        # Right panel: Visualization
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=3)
        
        # Create visualization area
        self._create_visualization_area(right_panel)

    def _create_quick_controls(self, parent):
        """Create quick control panel with common actions"""
        # Card frame for controls
        control_card = ttk.LabelFrame(parent, text="Quick Controls", 
                                     style='Card.TFrame', padding=10)
        control_card.pack(fill=tk.X, padx=5, pady=5)
        
        # Analysis mode selector with icons
        mode_frame = ttk.Frame(control_card)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="Analysis Mode:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value=self.current_analysis_mode)
        mode_selector = ttk.Combobox(mode_frame, textvariable=self.mode_var,
                                    values=['drops', 'gains'], state='readonly', width=10)
        mode_selector.pack(side=tk.LEFT, padx=5)
        mode_selector.bind('<<ComboboxSelected>>', lambda e: self._set_analysis_mode())
        
        # Condensed visualization buttons in a single column
        viz_frame = ttk.LabelFrame(control_card, text="Visualizations", padding=5)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        viz_buttons = [
            ("📈 Timeline", lambda: self._update_visualization("timeline")),
            ("🔄 Recovery", lambda: self._update_visualization("recovery")),
            ("🎯 Conditions", lambda: self._update_visualization("conditions")),
            ("📊 Statistics", lambda: self._update_visualization("stats")),
            ("🔗 Correlation", lambda: self._update_visualization("correlation")),
            ("🎲 Probability", lambda: self._update_visualization("probability"))
        ]
        for i, (text, command) in enumerate(viz_buttons):
            btn = ttk.Button(viz_frame, text=text, command=command, style='Info.TButton')
            btn.pack(fill=tk.X, padx=2, pady=2)

    def _create_event_list(self, parent):
        """Create enhanced event list with better formatting"""
        list_card = ttk.LabelFrame(parent, text="Event List", style='Card.TFrame', padding=5)
        list_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary section
        self.summary_frame = ttk.Frame(list_card)
        self.summary_frame.pack(fill=tk.X, pady=5)
        
        self.summary_text = tk.Text(self.summary_frame, height=3, wrap=tk.WORD,
                                   font=('Arial', 9), bg='#f8f9fa', relief=tk.FLAT)
        self.summary_text.pack(fill=tk.X, padx=5)
        self._update_summary("Ready to analyze market events")
        
        # Enhanced treeview with better styling
        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Create treeview with alternating row colors
        self.event_tree = ttk.Treeview(tree_frame, selectmode='browse',
                                      yscrollcommand=y_scroll.set,
                                      xscrollcommand=x_scroll.set,
                                      columns=["Date", "Type", "Value", "VIX", "RSI"],
                                      show='headings', height=10)
        
        # Configure scrollbars
        y_scroll.config(command=self.event_tree.yview)
        x_scroll.config(command=self.event_tree.xview)
        
        # Grid layout
        self.event_tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure columns with better formatting
        columns_config = {
            "Date": {"width": 100, "anchor": tk.CENTER},
            "Type": {"width": 120, "anchor": tk.W},
            "Value": {"width": 80, "anchor": tk.E},
            "VIX": {"width": 60, "anchor": tk.E},
            "RSI": {"width": 60, "anchor": tk.E}
        }
        
        for col, config in columns_config.items():
            self.event_tree.heading(col, text=col)
            self.event_tree.column(col, width=config["width"], anchor=config["anchor"])
        
        # Add alternating row colors
        self.event_tree.tag_configure('odd', background='#f8f9fa')
        self.event_tree.tag_configure('even', background='white')
        
        # Bind selection event
        self.event_tree.bind('<<TreeviewSelect>>', self._on_event_select)

    def _create_visualization_area(self, parent):
        """Create enhanced visualization area"""
        viz_card = ttk.LabelFrame(parent, text="Visualization", 
                                 style='Card.TFrame', padding=10)
        viz_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figure with better default size and DPI
        self.fig = plt.Figure(figsize=(10, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_card)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Enhanced toolbar frame
        toolbar_frame = ttk.Frame(viz_card)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Add custom toolbar buttons
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar_frame, text="💾 Save", command=self._save_figure,
                  style='Info.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="🖨️ Print", command=self._print_figure,
                  style='Info.TButton').pack(side=tk.LEFT, padx=2)

    def _create_threshold_filters(self, parent, condensed=False):
        """Create threshold filter section"""
        card = ttk.LabelFrame(parent, text="Event Magnitude Filters", padding=6 if condensed else 15)
        card.pack(fill=tk.X, padx=6 if condensed else 10, pady=3 if condensed else 5)
        threshold_frame = ttk.Frame(card)
        threshold_frame.pack(fill=tk.X)
        font = ('Arial', 9) if condensed else None
        ttk.Label(threshold_frame, text="Minimum (%):", font=font).grid(row=0, column=0, sticky=tk.W, pady=1)
        self.min_threshold_var = tk.StringVar(value="0.1")
        ttk.Entry(threshold_frame, textvariable=self.min_threshold_var, width=7, font=font).grid(row=0, column=1, padx=3)
        ttk.Label(threshold_frame, text="Maximum (%):", font=font).grid(row=1, column=0, sticky=tk.W, pady=1)
        self.max_threshold_var = tk.StringVar()
        ttk.Entry(threshold_frame, textvariable=self.max_threshold_var, width=7, font=font).grid(row=1, column=1, padx=3)

    def _create_recovery_filters(self, parent, condensed=False):
        """Create recovery filter section"""
        card = ttk.LabelFrame(parent, text="Recovery Analysis Filters", padding=6 if condensed else 15)
        card.pack(fill=tk.X, padx=6 if condensed else 10, pady=3 if condensed else 5)
        font = ('Arial', 9) if condensed else None
        ttk.Label(card, text="Minimum Recovery (%):", font=font).grid(row=0, column=0, sticky=tk.W)
        self.recovery_threshold = tk.StringVar()
        ttk.Entry(card, textvariable=self.recovery_threshold, width=10, font=font).grid(row=0, column=1, padx=3)
        ttk.Label(card, text="Recovery Period:", font=font).grid(row=1, column=0, sticky=tk.W, pady=(6 if condensed else 10, 2))
        self.recovery_period = tk.StringVar(value="1D")
        periods = ["1D", "2D", "3D", "1W", "1M", "3M", "6M", "1Y"]
        period_frame = ttk.Frame(card)
        period_frame.grid(row=1, column=1, sticky=tk.W)
        for i, period in enumerate(periods):
            ttk.Radiobutton(period_frame, text=period, variable=self.recovery_period,
                           value=period).grid(row=i//4, column=i%4, sticky=tk.W, padx=2, pady=1)

    def _create_market_condition_filters(self, parent, condensed=False):
        """Create market condition filters"""
        card = ttk.LabelFrame(parent, text="Market Condition Filters", padding=6 if condensed else 15)
        card.pack(fill=tk.X, padx=6 if condensed else 10, pady=3 if condensed else 5)
        font = ('Arial', 9) if condensed else None
        self.condition_vars = {}
        indicators = ['VIX', 'RSI', 'Volume']
        for idx, indicator in enumerate(indicators):
            frame = ttk.Frame(card)
            frame.pack(fill=tk.X, pady=2 if condensed else 5)
            self.condition_vars[indicator] = {
                'enabled': tk.BooleanVar(),
                'min': tk.StringVar(),
                'max': tk.StringVar()
            }
            cb = ttk.Checkbutton(frame, text=f"Filter by {indicator}",
                                variable=self.condition_vars[indicator]['enabled'])
            cb.grid(row=0, column=0, sticky=tk.W)
            range_frame = ttk.Frame(frame)
            range_frame.grid(row=0, column=1, padx=2)
            ttk.Label(range_frame, text="Min:", font=font).grid(row=0, column=0, sticky=tk.W)
            ttk.Entry(range_frame, textvariable=self.condition_vars[indicator]['min'],
                     width=7, font=font).grid(row=0, column=1, padx=2)
            ttk.Label(range_frame, text="Max:", font=font).grid(row=0, column=2, sticky=tk.W, padx=(6 if condensed else 10, 0))
            ttk.Entry(range_frame, textvariable=self.condition_vars[indicator]['max'],
                     width=7, font=font).grid(row=0, column=3, padx=2)

    def _create_temporal_filters(self, parent, condensed=False):
        """Create temporal filters"""
        card = ttk.LabelFrame(parent, text="Temporal Filters", padding=6 if condensed else 15)
        card.pack(fill=tk.X, padx=6 if condensed else 10, pady=3 if condensed else 5)
        font = ('Arial', 9) if condensed else None
        ttk.Label(card, text="Date Range:", font=font).grid(row=0, column=0, sticky=tk.W)
        date_frame = ttk.Frame(card)
        date_frame.grid(row=0, column=1, pady=2)
        ttk.Label(date_frame, text="From:", font=font).grid(row=0, column=0, sticky=tk.W)
        self.date_from_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_from_var, width=10, font=font).grid(row=0, column=1, padx=2)
        ttk.Label(date_frame, text="To:", font=font).grid(row=0, column=2, sticky=tk.W, padx=(6 if condensed else 10, 0))
        self.date_to_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_to_var, width=10, font=font).grid(row=0, column=3, padx=2)
        # Day of week filter
        ttk.Label(card, text="Day of Week:", font=font).grid(row=1, column=0, sticky=tk.W, pady=(6 if condensed else 10, 2))
        dow_frame = ttk.Frame(card)
        dow_frame.grid(row=1, column=1, pady=2)
        self.dow_vars = {}
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        for i, day in enumerate(days):
            self.dow_vars[day] = tk.BooleanVar(value=True)
            ttk.Checkbutton(dow_frame, text=day, variable=self.dow_vars[day]).grid(
                row=0, column=i, padx=2)

    def _create_statistics_tab(self):
        """Create statistics and reports tab"""
        # Create notebook for different stat views
        stats_notebook = ttk.Notebook(self.stats_frame)
        stats_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary statistics
        summary_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(summary_frame, text="Summary")
        self._create_summary_stats(summary_frame)
        
        # Detailed analysis
        detailed_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(detailed_frame, text="Detailed Analysis")
        self._create_detailed_analysis(detailed_frame)
        
        # Export options
        export_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(export_frame, text="Export")
        self._create_export_options(export_frame)

    def _create_summary_stats(self, parent):
        """Create summary statistics view"""
        # Create text widget for stats display
        stats_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20,
                                              font=('Courier', 10))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add refresh button
        ttk.Button(parent, text="Refresh Statistics", 
                  command=lambda: self._update_statistics_display(stats_text),
                  style='Primary.TButton').pack(pady=5)
        
        self.stats_text_widget = stats_text

    def _create_detailed_analysis(self, parent):
        """Create detailed analysis view"""
        # Create frame for analysis options
        options_frame = ttk.LabelFrame(parent, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Analysis type selector
        ttk.Label(options_frame, text="Analysis Type:").grid(row=0, column=0, sticky=tk.W)
        analysis_types = ["Temporal Patterns", "Recovery Analysis", 
                         "Market Regime Analysis", "Correlation Study"]
        self.analysis_type_var = tk.StringVar(value=analysis_types[0])
        ttk.Combobox(options_frame, textvariable=self.analysis_type_var,
                    values=analysis_types, state='readonly', width=25).grid(row=0, column=1, padx=5)
        
        # Results display
        results_frame = ttk.LabelFrame(parent, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.analysis_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                         font=('Courier', 10))
        self.analysis_results.pack(fill=tk.BOTH, expand=True)
        
        # Run analysis button
        ttk.Button(options_frame, text="Run Analysis",
                  command=self._run_detailed_analysis,
                  style='Primary.TButton').grid(row=0, column=2, padx=10)

    def _create_export_options(self, parent):
        """Create export options"""
        export_card = ttk.LabelFrame(parent, text="Export Options", padding=20)
        export_card.pack(padx=20, pady=20)
        
        # Export format options
        ttk.Label(export_card, text="Export Format:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        export_options = [
            ("📊 Excel Report (.xlsx)", self._export_excel),
            ("📄 PDF Report (.pdf)", self._export_pdf),
            ("📈 CSV Data (.csv)", self._export_csv),
            ("🖼️ Charts (.png)", self._export_charts)
        ]
        
        for text, command in export_options:
            ttk.Button(export_card, text=text, command=command,
                      style='Info.TButton').pack(fill=tk.X, pady=5)

    # Data handling methods
    def _browse_data(self):
        """Browse and load data file"""
        file_path = filedialog.askopenfilename(
            title=f"Load CSV File for {self.index_name}",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self._load_data_file(file_path)

    def _load_data_file(self, file_path: str, explicit_data_type: Optional[str] = None) -> None:
        """Load data file with enhanced feedback"""
        try:
            # Show loading indicator
            self.status_label.config(text="📊 Loading data...")
            self.root.update()
            
            raw_df = pd.read_csv(file_path)
            
            # Detect data type
            detected_type = explicit_data_type
            if not detected_type:
                validation_result = DataTypeDetector.validate_csv_structure(file_path, raw_df.copy())
                detected_type = validation_result['data_type']
                if detected_type == 'unknown':
                    messagebox.showerror("Load Error", 
                                       f"Could not determine data type for {os.path.basename(file_path)}")
                    return

            # Clean data
            cleaned_df = DataProcessor.clean_data(raw_df, detected_type)
            
            if cleaned_df is not None and not cleaned_df.empty:
                # Store data
                if detected_type == 'drops':
                    self.raw_df_drops = raw_df
                    self.processed_df_drops = cleaned_df
                    icon = "📉"
                else:
                    self.raw_df_gains = raw_df
                    self.processed_df_gains = cleaned_df
                    icon = "📈"
                
                # Update UI
                self.status_label.config(text=f"{icon} {detected_type.capitalize()} data loaded successfully")
                self._update_data_info()
                
                # Set mode and apply default filters
                self.mode_var.set(detected_type)
                self._set_analysis_mode()
                self.min_threshold_var.set("0.1")
                self._apply_filters_and_update()
                
            else:
                messagebox.showerror("Load Error", 
                                   f"Failed to load or clean data from {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading file:\n{str(e)}")
            self.status_label.config(text="❌ Error loading data")

    def _set_analysis_mode(self):
        """Set analysis mode with UI updates"""
        self.current_analysis_mode = self.mode_var.get()
        self.filtered_df = self._get_current_df()
        
        # Update UI elements
        icon = "📉" if self.current_analysis_mode == 'drops' else "📈"
        self.status_label.config(text=f"{icon} {self.current_analysis_mode.capitalize()} Analysis Mode")
        
        # Update event list and visualization
        self._update_event_list()
        if self.current_viz_type:
            self._update_visualization(self.current_viz_type)
        else:
            self._update_visualization("timeline")

    def _get_current_df(self) -> Optional[pd.DataFrame]:
        """Get current dataframe based on mode"""
        if self.current_analysis_mode == 'drops':
            return self.processed_df_drops
        else:
            return self.processed_df_gains

    def _apply_filters_and_update(self):
        """Apply filters with enhanced feedback"""
        df = self._get_current_df()
        if df is None or df.empty:
            self.filtered_df = None
            self._update_event_list()
            self._update_visualization("timeline")
            return
        
        # Show filtering indicator
        self.status_label.config(text="🔍 Applying filters...")
        self.root.update()
        
        mask = pd.Series(True, index=df.index)
        
        # Apply threshold filters
        try:
            min_val = float(self.min_threshold_var.get()) if self.min_threshold_var.get() else None
            max_val = float(self.max_threshold_var.get()) if self.max_threshold_var.get() else None
            col = 'Drop (%)' if self.current_analysis_mode == 'drops' else 'Gain (%)'
            
            if min_val is not None:
                mask &= df[col] >= min_val
            if max_val is not None:
                mask &= df[col] <= max_val
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid threshold values")
            return
        
        # Apply market condition filters
        for indicator, vars_dict in self.condition_vars.items():
            if indicator in df.columns and vars_dict['enabled'].get():
                try:
                    min_val = float(vars_dict['min'].get()) if vars_dict['min'].get() else None
                    max_val = float(vars_dict['max'].get()) if vars_dict['max'].get() else None
                    if min_val is not None:
                        mask &= (df[indicator] >= min_val)
                    if max_val is not None:
                        mask &= (df[indicator] <= max_val)
                except ValueError:
                    continue
        
        # Apply temporal filters if set
        if hasattr(self, 'date_from_var') and self.date_from_var.get():
            try:
                date_from = pd.to_datetime(self.date_from_var.get())
                mask &= df[DATE_COL] >= date_from
            except:
                pass
                
        if hasattr(self, 'date_to_var') and self.date_to_var.get():
            try:
                date_to = pd.to_datetime(self.date_to_var.get())
                mask &= df[DATE_COL] <= date_to
            except:
                pass
        
        # Apply day of week filter
        if hasattr(self, 'dow_vars'):
            dow_mask = pd.Series(False, index=df.index)
            for day, var in self.dow_vars.items():
                if var.get():
                    day_num = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].index(day)
                    dow_mask |= (pd.to_datetime(df[DATE_COL]).dt.dayofweek == day_num)
            mask &= dow_mask
        
        # Apply recovery filter
        try:
            recovery_val = float(self.recovery_threshold.get()) if self.recovery_threshold.get() else None
            if recovery_val is not None:
                # Get the selected recovery period column
                recovery_period = self.recovery_period.get()  # e.g., "1D"
                recovery_col = f"{recovery_period} (%)"  # e.g., "1D (%)"
                if recovery_col in df.columns:
                    # Filter for events where recovery meets threshold
                    mask &= df[recovery_col] >= recovery_val
                else:
                    messagebox.showwarning("Missing Data", f"Recovery period {recovery_period} not available in data.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid number entered for recovery filter.")
            return
        
        self.filtered_df = df[mask].copy()
        
        # Update UI
        self._update_event_list()
        self._update_visualization(self.current_viz_type or "timeline")
        
        count = len(self.filtered_df)
        icon = "✅" if count > 0 else "⚠️"
        self.status_label.config(text=f"{icon} Found {count} events matching criteria")
        self._update_data_info()

    def _update_event_list(self):
        """Update event list with enhanced formatting"""
        # Clear existing items
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        
        if self.filtered_df is None or self.filtered_df.empty:
            self._update_summary("No events found matching the current criteria")
            return
        
        # Generate summary
        summary = self._generate_summary_stats()
        self._update_summary(f"Found {len(self.filtered_df)} matching events\n{summary}")
        
        # Add events with alternating colors
        col = 'Drop (%)' if self.current_analysis_mode == 'drops' else 'Gain (%)'
        for idx, (_, row) in enumerate(self.filtered_df.iterrows()):
            values = [
                row.get(DATE_COL, '').strftime('%Y-%m-%d') if pd.notna(row.get(DATE_COL)) else '',
                row.get('Type', ''),
                f"{row.get(col, 0):.2f}%",
                f"{row.get('VIX', 0):.1f}" if pd.notna(row.get('VIX')) else 'N/A',
                f"{row.get('RSI', 0):.1f}" if pd.notna(row.get('RSI')) else 'N/A'
            ]
            
            tag = 'odd' if idx % 2 == 0 else 'even'
            self.event_tree.insert('', tk.END, values=tuple(values), tags=(tag,))

    def _update_visualization(self, viz_type: str):
        """Update visualization with error handling"""
        self.current_viz_type = viz_type
        
        if not hasattr(self, 'visualizations'):
            # Initialize if not already done
            self.visualizations = EnhancedVisualizations(self.fig, self.canvas)
        
        try:
            if viz_type == "timeline":
                self.visualizations.show_timeline(self.filtered_df, self.current_analysis_mode)
            elif viz_type == "recovery":
                self.visualizations.show_recovery_paths(self.filtered_df, self.current_analysis_mode)
            elif viz_type == "conditions":
                self.visualizations.show_market_conditions(self.filtered_df, self.current_analysis_mode)
            elif viz_type == "stats":
                self.visualizations.show_statistics(self.filtered_df, self.current_analysis_mode)
            elif viz_type == "correlation":
                self.visualizations.show_correlation_analysis(self.filtered_df, self.current_analysis_mode)
            elif viz_type == "probability":
                self.visualizations.show_probability_analysis(self.filtered_df, self.current_analysis_mode)
        except Exception as e:
            print(f"Visualization error: {e}")
            self.visualizations.show_empty_plot(f"Error creating {viz_type} visualization")

    # Helper methods
    def _update_summary(self, text: str):
        """Update summary text"""
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', text)
        self.summary_text.config(state=tk.DISABLED)

    def _generate_summary_stats(self) -> str:
        """Generate summary statistics"""
        if self.filtered_df is None or self.filtered_df.empty:
            return "No data available"
        
        return self.data_processor.generate_summary_stats(self.filtered_df, self.current_analysis_mode)

    def _update_data_info(self):
        """Update data info label"""
        drops_count = len(self.processed_df_drops) if self.processed_df_drops is not None else 0
        gains_count = len(self.processed_df_gains) if self.processed_df_gains is not None else 0
        filtered_count = len(self.filtered_df) if self.filtered_df is not None else 0
        
        info = f"📉 Drops: {drops_count} | 📈 Gains: {gains_count} | 🔍 Filtered: {filtered_count}"
        self.data_info_label.config(text=info)

    def _refresh_analysis(self):
        """Refresh current analysis"""
        self._apply_filters_and_update()

    def _save_figure(self):
        """Save current figure"""
        if self.current_viz_type:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), 
                          ("SVG files", "*.svg"), ("All files", "*.*")]
            )
            if filename:
                self.fig.savefig(filename, bbox_inches='tight', dpi=300)
                messagebox.showinfo("Success", f"Figure saved to {os.path.basename(filename)}")

    def _print_figure(self):
        """Print current figure"""
        # Placeholder for print functionality
        messagebox.showinfo("Print", "Print functionality not yet implemented")

    def _on_event_select(self, event):
        """Handle event selection"""
        # Placeholder for event selection handling
        pass

    def _update_statistics_display(self, text_widget):
        """Update statistics display"""
        stats = self._generate_summary_stats()
        text_widget.config(state=tk.NORMAL)
        text_widget.delete('1.0', tk.END)
        text_widget.insert('1.0', stats)
        text_widget.config(state=tk.DISABLED)

    def _run_detailed_analysis(self):
        """Run detailed analysis based on selected type"""
        if self.filtered_df is None or self.filtered_df.empty:
            self.analysis_results.delete('1.0', tk.END)
            self.analysis_results.insert('1.0', "No data available for analysis")
            return
        
        analysis_type = self.analysis_type_var.get()
        results = f"Running {analysis_type}...\n\n"
        
        # Placeholder for different analysis types
        if analysis_type == "Temporal Patterns":
            results += self._analyze_temporal_patterns()
        elif analysis_type == "Recovery Analysis":
            results += self._analyze_recovery_patterns()
        elif analysis_type == "Market Regime Analysis":
            results += self._analyze_market_regimes()
        elif analysis_type == "Correlation Study":
            results += self._analyze_correlations()
        
        self.analysis_results.delete('1.0', tk.END)
        self.analysis_results.insert('1.0', results)

    def _analyze_temporal_patterns(self) -> str:
        """Analyze temporal patterns in the data"""
        df = self.filtered_df.copy()
        df['Year'] = pd.to_datetime(df[DATE_COL]).dt.year
        df['Month'] = pd.to_datetime(df[DATE_COL]).dt.month
        df['DayOfWeek'] = pd.to_datetime(df[DATE_COL]).dt.day_name()
        
        col = 'Drop (%)' if self.current_analysis_mode == 'drops' else 'Gain (%)'
        
        results = "TEMPORAL PATTERN ANALYSIS\n" + "="*50 + "\n\n"
        
        # Yearly analysis
        yearly = df.groupby('Year')[col].agg(['count', 'mean', 'std', 'max'])
        results += "Yearly Summary:\n"
        results += yearly.to_string() + "\n\n"
        
        # Monthly analysis
        monthly = df.groupby('Month')[col].agg(['count', 'mean'])
        results += "Monthly Patterns:\n"
        results += monthly.to_string() + "\n\n"
        
        # Day of week analysis
        dow = df.groupby('DayOfWeek')[col].agg(['count', 'mean'])
        results += "Day of Week Analysis:\n"
        results += dow.to_string() + "\n"
        
        return results

    def _analyze_recovery_patterns(self) -> str:
        """Analyze recovery patterns"""
        # Placeholder implementation
        return "Recovery pattern analysis not yet implemented"

    def _analyze_market_regimes(self) -> str:
        """Analyze market regimes"""
        # Placeholder implementation
        return "Market regime analysis not yet implemented"

    def _analyze_correlations(self) -> str:
        """Analyze correlations"""
        # Placeholder implementation
        return "Correlation analysis not yet implemented"

    # Export methods
    def _export_excel(self):
        """Export to Excel"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename and self.filtered_df is not None:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                self.filtered_df.to_excel(writer, sheet_name='Event Data', index=False)
                # Add summary stats sheet
                summary_df = pd.DataFrame([self._generate_summary_stats().split('\n')])
                summary_df.to_excel(writer, sheet_name='Summary', index=False, header=False)
            messagebox.showinfo("Success", f"Data exported to {os.path.basename(filename)}")

    def _export_pdf(self):
        """Export to PDF"""
        messagebox.showinfo("Export", "PDF export not yet implemented")

    def _export_csv(self):
        """Export to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename and self.filtered_df is not None:
            self.filtered_df.to_csv(filename, index=False)
            messagebox.showinfo("Success", f"Data exported to {os.path.basename(filename)}")

    def _export_charts(self):
        """Export all charts"""
        directory = filedialog.askdirectory(title="Select Directory for Charts")
        if directory:
            # Save all visualization types
            viz_types = ["timeline", "recovery", "conditions", "stats", "correlation", "probability"]
            for viz_type in viz_types:
                self._update_visualization(viz_type)
                self.fig.savefig(os.path.join(directory, f"{self.index_name}_{viz_type}.png"), 
                               bbox_inches='tight', dpi=300)
            messagebox.showinfo("Success", f"All charts saved to {directory}")