"""
src/visualization
Automated plot generation and comparative metrics reporting for CIPAT report, slides, and viva.
Exports:
- generate_e4_figures: 8 publication charts for Experiment E4 (Autoscaling dynamics)
- generate_e7_figures: 8 publication charts for Experiment E7 (Security & Data Classification)
"""

from src.visualization.e4_plots import generate_e4_figures
from src.visualization.e7_plots import generate_e7_figures

__all__ = [
    "generate_e4_figures",
    "generate_e7_figures",
]
