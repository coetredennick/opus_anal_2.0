#!/usr/bin/env python3
"""
Flexible Market Analyzer - Main Application
Enhanced drop and gain analysis tool with flexible file loading
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
import os
import sys
from typing import Dict, List, Optional, Tuple

from config import WINDOW_SIZE, PADDING, PLOT_STYLE
from analysis_tab import EnhancedAnalysisTab
from data_detector import DataTypeDetector
from file_utils import FileUtils
from refined_ui_components import UIComponents
from refined_data_processor import DataProcessor

INDEX_TAB_INFO = {
    "S&P 500 (^GSPC)": ("sp500drop.csv", "sp500gain.csv"),
    "NASDAQ (^IXIC)": ("nasdaqdrop.csv", "nasdaqgain.csv"),
    "Dow Jones (^DJI)": ("dowdrop.csv", "dowgain.csv"),
    "Russell 2000 (^RUT)": ("russeldrop.csv", "russelgain.csv"),
}

class FlexibleMarketAnalyzer:
    """Main application class for market analysis with multiple index tabs"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flexible Market Analyzer - Drop & Gain Analysis")
        self.root.geometry(WINDOW_SIZE)
        
        # Apply styling
        plt.rcParams.update(PLOT_STYLE)
        self._setup_theme()
        
        # Create main UI
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Storage for tab instances
        self.index_tabs: Dict[str, EnhancedAnalysisTab] = {}
        
        # Auto-load index data from dropcsvs/ and gaincsvs/
        self._auto_load_index_data()
        self._create_menu()
        
        # Bind cleanup
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_theme(self) -> None:
        """Setup application theme"""
        style = ttk.Style(self.root)
        available_themes = style.theme_names()
        preferred_themes = ['clam', 'vista', 'xpnative', 'aqua', 'default']
        
        for theme in preferred_themes:
            if theme in available_themes:
                try:
                    style.theme_use(theme)
                    break
                except tk.TclError:
                    continue

    def _auto_load_index_data(self):
        drop_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dropcsvs"))
        gain_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gaincsvs"))
        for index_name, (drop_file, gain_file) in INDEX_TAB_INFO.items():
            drop_path = os.path.join(drop_dir, drop_file)
            gain_path = os.path.join(gain_dir, gain_file)
            initial_files = []
            if os.path.isfile(drop_path):
                initial_files.append(drop_path)
            if os.path.isfile(gain_path):
                initial_files.append(gain_path)
            self.add_index_tab(index_name, initial_files if initial_files else None)

    def _create_menu(self) -> None:
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add New Index Tab", command=self._add_custom_index_tab)
        file_menu.add_command(label="Auto-Discover Data Files", command=self._global_auto_discover)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Data Files", command=self._validate_data_files)
        tools_menu.add_command(label="File Type Detector", command=self._show_file_type_detector)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="File Format Guide", command=self._show_format_guide)
        help_menu.add_command(label="About", command=self._show_about)

    def add_index_tab(self, index_name: str, initial_files: Optional[List[str]] = None) -> EnhancedAnalysisTab:
        """Add a new index analysis tab"""
        # Check if tab already exists
        if index_name in self.index_tabs:
            # Switch to existing tab
            for i in range(self.main_notebook.index("end")):
                if self.main_notebook.tab(i, "text") == index_name:
                    self.main_notebook.select(i)
                    return self.index_tabs[index_name]
        
        # Create new tab
        tab_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(tab_frame, text=index_name)
        
        # Create the analysis tab instance
        analysis_tab = EnhancedAnalysisTab(self.root, tab_frame, index_name, initial_files)
        self.index_tabs[index_name] = analysis_tab
        
        # Select the new tab
        self.main_notebook.select(tab_frame)
        
        return analysis_tab

    def _add_custom_index_tab(self) -> None:
        """Add a custom index tab with user-defined name"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Index")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Enter index name:").pack(pady=10)
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def create_tab():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Invalid Name", "Please enter a valid index name.")
                return
                
            if name in self.index_tabs:
                messagebox.showwarning("Duplicate Name", "An index with this name already exists.")
                return
                
            self.add_index_tab(name)
            dialog.destroy()
        
        ttk.Button(button_frame, text="Create", command=create_tab).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        name_entry.bind('<Return>', lambda e: create_tab())

    def _global_auto_discover(self) -> None:
        """Auto-discover data files for all indices"""
        directory = filedialog.askdirectory(title="Select Directory with Market Data Files")
        if not directory:
            return
        
        discovered_files = FileUtils.auto_discover_files(directory)
        
        if not discovered_files or all(not files for files in discovered_files.values()):
            messagebox.showinfo("No Files", "No CSV files found in selected directory.")
            return
        
        # Analyze files and group by potential index
        file_analysis = self._analyze_discovered_files(discovered_files)
        
        # Show results and allow user to create tabs
        self._show_global_discovery_dialog(file_analysis)

    def _analyze_discovered_files(self, discovered_files: Dict[str, List[str]]) -> Dict[str, Dict[str, List[str]]]:
        """Analyze discovered files and group by index symbol"""
        file_analysis = {}
        
        for data_type, files in discovered_files.items():
            if data_type == 'unknown':
                continue
                
            for csv_file in files:
                filename = os.path.basename(csv_file)
                
                # Try to extract index symbol from filename
                potential_symbols = DataTypeDetector.extract_index_symbols(filename)
                
                # If no symbols found, use a generic name
                if not potential_symbols:
                    potential_symbols = ['Unknown']
                
                for symbol in potential_symbols:
                    if symbol not in file_analysis:
                        file_analysis[symbol] = {'drops': [], 'gains': []}
                    file_analysis[symbol][data_type].append(csv_file)
        
        return file_analysis

    def _show_global_discovery_dialog(self, file_analysis: Dict[str, Dict[str, List[str]]]) -> None:
        """Show dialog for global file discovery results"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Global File Discovery")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Discovered Index Data Files:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create scrollable frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Track selections
        selections = {}
        
        for symbol, files in sorted(file_analysis.items()):
            # Symbol section
            symbol_frame = ttk.LabelFrame(scrollable_frame, text=f"Index: {symbol}")
            symbol_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Check if we already have this tab
            tab_exists = symbol in self.index_tabs
            default_create = not tab_exists
            
            selections[symbol] = {
                'create_tab': tk.BooleanVar(value=default_create), 
                'files': []
            }
            
            # Checkbox to create/update tab
            checkbox_text = f"Update existing tab for {symbol}" if tab_exists else f"Create tab for {symbol}"
            ttk.Checkbutton(symbol_frame, text=checkbox_text, 
                           variable=selections[symbol]['create_tab']).pack(anchor=tk.W)
            
            # File selections
            for data_type in ['drops', 'gains']:
                if files.get(data_type):
                    type_label = "📉 Drop Files:" if data_type == 'drops' else "📈 Gain Files:"
                    ttk.Label(symbol_frame, text=type_label, font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=20)
                    
                    for file_path in files[data_type]:
                        var = tk.BooleanVar(value=True)
                        filename = os.path.basename(file_path)
                        ttk.Checkbutton(symbol_frame, text=filename, variable=var).pack(anchor=tk.W, padx=40)
                        selections[symbol]['files'].append((file_path, data_type, var))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def create_selected_tabs():
            created_count = 0
            updated_count = 0
            
            for symbol, selection in selections.items():
                if selection['create_tab'].get():
                    # Collect selected files
                    selected_files = [(fp, dt) for fp, dt, var in selection['files'] if var.get()]
                    
                    if selected_files:
                        if symbol in self.index_tabs:
                            # Load additional files into existing tab
                            for file_path, data_type in selected_files:
                                self.index_tabs[symbol]._load_data_file(file_path, data_type)
                            updated_count += 1
                        else:
                            # Create new tab with initial files
                            file_paths = [fp for fp, _ in selected_files]
                            self.add_index_tab(symbol, file_paths)
                            created_count += 1
            
            if created_count > 0 or updated_count > 0:
                msg = []
                if created_count > 0:
                    msg.append(f"Created {created_count} new tab(s)")
                if updated_count > 0:
                    msg.append(f"Updated {updated_count} existing tab(s)")
                messagebox.showinfo("Success", " and ".join(msg) + ".")
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="Load Selected", command=create_selected_tabs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select All", 
                  command=lambda: self._toggle_all_selections(selections, True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", 
                  command=lambda: self._toggle_all_selections(selections, False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _toggle_all_selections(self, selections: Dict, value: bool) -> None:
        """Toggle all file selections"""
        for symbol_data in selections.values():
            symbol_data['create_tab'].set(value)
            for _, _, var in symbol_data['files']:
                var.set(value)

    def _validate_data_files(self) -> None:
        """Validate data files in a selected directory"""
        directory = filedialog.askdirectory(title="Select Directory to Validate")
        if not directory:
            return
        
        results = FileUtils.validate_files_in_directory(directory)
        
        if not results:
            messagebox.showinfo("No Files", "No CSV files found in selected directory.")
            return
        
        UIComponents.create_validation_results_dialog(self.root, results)

    def _show_file_type_detector(self) -> None:
        """Show file type detection tool"""
        UIComponents.show_file_type_detector_dialog(self.root)

    def _show_format_guide(self) -> None:
        """Show file format guide"""
        UIComponents.create_format_guide_dialog(self.root)

    def _show_about(self) -> None:
        """Show about dialog"""
        about_text = """Flexible Market Analyzer v2.0

Enhanced drop and gain analysis tool with flexible file loading.

Features:
• Auto-detection of drop/gain data
• Flexible file naming support
• Dual-mode analysis interface
• Advanced visualization tools
• File validation utilities

Compatible with any CSV file structure containing the required columns."""
        
        messagebox.showinfo("About", about_text)

    def _on_closing(self) -> None:
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
            self.root.destroy()

    def run(self) -> None:
        """Start the application"""
        try:
            print("Starting Flexible Market Analyzer...")
            print("This version works with ANY file naming convention!")
            print("Supports both drop and gain data with auto-detection.")
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    app = FlexibleMarketAnalyzer()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
        if os.path.isdir(data_dir):
            # Auto-discover files after startup
            app.root.after(1000, lambda: app._global_auto_discover())
        else:
            print(f"Invalid directory: {data_dir}")
    
    app.run()


if __name__ == "__main__":
    main()