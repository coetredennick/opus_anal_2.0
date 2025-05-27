"""
UI Components - Reusable UI components and dialogs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import pandas as pd
import os
from typing import List, Tuple, Optional

from data_detector import DataTypeDetector


class UIComponents:
    """Reusable UI components and dialogs"""
    
    @staticmethod
    def create_scrollable_frame(parent: tk.Widget, width: int = 350) -> Tuple[ttk.Frame, tk.Canvas]:
        """Create a scrollable frame with canvas and scrollbar"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, width=width)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollable_frame.bind(
            "<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame, canvas

    @staticmethod
    def create_dialog_base(parent: tk.Widget, title: str, width: int = 600, 
                          height: int = 400) -> tk.Toplevel:
        """Create a base dialog window with standard settings"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        return dialog

    @staticmethod
    def create_validation_results_dialog(parent: tk.Widget, 
                                       results: List[Tuple[str, dict]]) -> None:
        """Show file validation results dialog"""
        dialog = UIComponents.create_dialog_base(parent, "File Validation Results")
        
        # Create text widget with frame
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Courier", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Format results
        output = UIComponents._format_validation_results(results)
        
        # Insert text with color coding
        text_widget.insert('1.0', output)
        
        # Add color tags
        text_widget.tag_config('valid', foreground='green')
        text_widget.tag_config('invalid', foreground='red')
        text_widget.tag_config('header', font=("Courier", 10, "bold"))
        
        # Apply tags to status lines
        lines = output.split('\n')
        line_num = 1
        for line in lines:
            if '✅ VALID' in line:
                text_widget.tag_add('valid', f"{line_num}.0", f"{line_num}.end")
            elif '❌ INVALID' in line:
                text_widget.tag_add('invalid', f"{line_num}.0", f"{line_num}.end")
            elif line.startswith('FILE VALIDATION RESULTS') or line.startswith('SUMMARY:'):
                text_widget.tag_add('header', f"{line_num}.0", f"{line_num}.end")
            line_num += 1
        
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Add export button
        def export_results():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(output)
        
        ttk.Button(button_frame, text="Export", command=export_results).pack(side=tk.LEFT, padx=5)

    @staticmethod
    def _format_validation_results(results: List[Tuple[str, dict]]) -> str:
        """Format validation results for display"""
        output = "FILE VALIDATION RESULTS\n" + "="*50 + "\n\n"
        
        valid_count = 0
        invalid_count = 0
        
        for filename, validation in results:
            status = "✅ VALID" if validation['valid'] else "❌ INVALID"
            data_type = validation['data_type'].upper() if validation['data_type'] != 'unknown' else 'UNKNOWN'
            
            output += f"{filename}\n"
            output += f"  Status: {status}\n"
            output += f"  Type: {data_type}\n"
            
            if validation['valid']:
                valid_count += 1
                if validation.get('missing_cols'):
                    output += f"  Missing optional columns: {', '.join(validation['missing_cols'])}\n"
            else:
                invalid_count += 1
                output += f"  Issues:\n"
                for issue in validation['issues']:
                    output += f"    - {issue}\n"
            
            output += "\n"
        
        # Summary
        total = len(results)
        output += "="*50 + "\n"
        output += f"SUMMARY: {valid_count}/{total} files are valid"
        if invalid_count > 0:
            output += f" ({invalid_count} invalid)"
        output += "\n"
        
        return output

    @staticmethod
    def create_format_guide_dialog(parent: tk.Widget) -> None:
        """Show file format guide dialog"""
        dialog = UIComponents.create_dialog_base(parent, "File Format Guide", 700, 500)
        
        # Create notebook for different sections
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        
        overview_text = scrolledtext.ScrolledText(overview_frame, wrap=tk.WORD, font=("Arial", 10))
        overview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        overview_text.insert('1.0', UIComponents._get_format_overview())
        overview_text.config(state=tk.DISABLED)
        
        # Required columns tab
        required_frame = ttk.Frame(notebook)
        notebook.add(required_frame, text="Required Columns")
        
        required_text = scrolledtext.ScrolledText(required_frame, wrap=tk.WORD, font=("Arial", 10))
        required_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        required_text.insert('1.0', UIComponents._get_required_columns_info())
        required_text.config(state=tk.DISABLED)
        
        # Examples tab
        examples_frame = ttk.Frame(notebook)
        notebook.add(examples_frame, text="Examples")
        
        examples_text = scrolledtext.ScrolledText(examples_frame, wrap=tk.WORD, font=("Courier", 9))
        examples_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        examples_text.insert('1.0', UIComponents._get_format_examples())
        examples_text.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    @staticmethod
    def _get_format_overview() -> str:
        """Get format overview text"""
        return """MARKET DATA FILE FORMAT GUIDE

This application supports CSV files with market drop or gain event data.

KEY FEATURES:
• Automatic detection of data type (drop vs gain)
• Flexible file naming - any filename works
• Support for partial data - only required columns needed
• Handles missing values gracefully

FILE DETECTION:
The application automatically detects the data type based on column names:
- Files with 'Drop (%)' column → Drop data
- Files with 'Gain (%)' column → Gain data
- Files with both → Uses the one with more data

VALIDATION:
Use 'Tools > Validate Data Files' to check your files before loading.
The validator will report:
- Data type detection
- Missing required columns
- Date format issues
- Optional column availability"""

    @staticmethod
    def _get_required_columns_info() -> str:
        """Get required columns information"""
        return """REQUIRED COLUMNS:

MINIMUM REQUIREMENTS:
1. Date - Event date (YYYY-MM-DD format)
   - Examples: 2024-01-15, 1990-08-06
   - Must be parseable by pandas

2. Drop (%) OR Gain (%) - Primary event magnitude
   - Numeric values representing percentage
   - Can be positive or negative
   - Examples: 3.45, -2.18

3. Type - Event type description
   - Text field describing the event
   - Examples: "Single Day Drop", "Market Correction"

4. Severity - Event severity classification
   - Text field for categorization
   - Examples: "Major", "Minor", "Moderate"

OPTIONAL COLUMNS (enhance analysis):
• VIX - Volatility Index value
• RSI - Relative Strength Index value
• ATR - Average True Range value
• Volume - Trading volume
• Forward Returns:
  - 1D (%) - 1 day forward return
  - 2D (%) - 2 day forward return
  - 3D (%) - 3 day forward return
  - 1W (%) - 1 week forward return
  - 1M (%) - 1 month forward return
  - 3M (%) - 3 month forward return
  - 6M (%) - 6 month forward return
  - 1Y (%) - 1 year forward return
  - 3Y (%) - 3 year forward return
• Total Avg (%) - Average of forward returns"""

    @staticmethod
    def _get_format_examples() -> str:
        """Get format examples"""
        return """CSV FILE EXAMPLES:

DROP DATA FILE:
Date,Type,Drop (%),Severity,VIX,RSI,1D (%),1W (%),1M (%)
1990-08-06,Single Day Drop,3.02,Major,35.91,12.63,5.86,15.14,27.11
1990-08-23,Intraday Drop,1.12,Minor,29.53,24.80,-3.80,-4.74,-2.23
2000-04-14,Tech Crash,5.83,Major,32.07,15.00,1.44,4.22,-4.56

GAIN DATA FILE:
Date,Type,Gain (%),Severity,VIX,RSI,1D (%),1W (%),1M (%)
1990-01-08,Single Day Gain,0.45,Minor,20.26,None,-1.18,-4.75,-6.82
1999-01-04,Rally,2.34,Moderate,22.14,65.3,0.89,3.45,5.67
2020-03-24,Recovery Bounce,9.38,Major,61.00,28.9,0.15,-2.26,12.68

MINIMAL FILE (only required columns):
Date,Type,Drop (%),Severity
2024-01-15,Market Dip,1.5,Minor
2024-02-03,Correction,3.2,Moderate

FILE NAMING EXAMPLES (all work):
✓ SP500_drops_2024.csv
✓ market_data_gains.csv
✓ ^GSPC_analysis.csv
✓ my_custom_data.csv
✓ 2024_Q1_market_events.csv"""

    @staticmethod
    def show_file_type_detector_dialog(parent: tk.Widget) -> None:
        """Show file type detection tool dialog"""
        dialog = UIComponents.create_dialog_base(parent, "File Type Detector", 600, 400)
        
        # Instructions
        ttk.Label(
            dialog, 
            text="Select a CSV file to analyze its structure and detect data type:",
            font=("Arial", 10)
        ).pack(pady=10)
        
        # Result display
        result_frame = ttk.LabelFrame(dialog, text="Analysis Results", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True)
        
        def analyze_file():
            filename = filedialog.askopenfilename(
                title="Select CSV File to Analyze",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    # Read sample data
                    df = pd.read_csv(filename, nrows=5)
                    validation = DataTypeDetector.validate_csv_structure(filename)
                    
                    # Format output
                    output = f"FILE: {os.path.basename(filename)}\n"
                    output += "="*60 + "\n\n"
                    
                    output += f"Detected Type: {validation['data_type'].upper()}\n"
                    output += f"Valid: {'✅ Yes' if validation['valid'] else '❌ No'}\n\n"
                    
                    output += "COLUMNS FOUND:\n"
                    for i, col in enumerate(df.columns, 1):
                        output += f"  {i:2d}. {col}\n"
                    
                    output += f"\nTOTAL ROWS: {len(pd.read_csv(filename))}\n"
                    
                    output += f"\nSAMPLE DATA (first 5 rows):\n"
                    output += "-"*60 + "\n"
                    output += df.to_string() + "\n\n"
                    
                    if validation['issues']:
                        output += "ISSUES FOUND:\n"
                        for issue in validation['issues']:
                            output += f"  ⚠️ {issue}\n"
                    else:
                        output += "✅ No issues found - file is ready to load!\n"
                    
                    # Display results
                    result_text.delete('1.0', tk.END)
                    result_text.insert('1.0', output)
                    
                except Exception as e:
                    result_text.delete('1.0', tk.END)
                    result_text.insert('1.0', f"❌ Error analyzing file:\n{str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Select File", command=analyze_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)