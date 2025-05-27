# In analysis_tab.py, replace the recovery filter section (around line 219) with:

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
            messagebox.showwarning("Missing Data", 
                f"Recovery period {recovery_period} not available in data.")
except ValueError:
    messagebox.showerror("Invalid Input", "Invalid number entered for recovery filter.")
    return