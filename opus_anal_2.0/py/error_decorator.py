# Add this to refined_visualizations.py

from functools import wraps

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

# Then use it on visualization methods:
@handle_plot_errors("timeline visualization")
def show_timeline(self, filtered_df, analysis_mode, date_col='Date'):
    # ... existing code without try/except wrapper