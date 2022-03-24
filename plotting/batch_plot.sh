#!/bin/bash
source "$HOME/pyenv/bin/activate"

extension=${1:-"eps"}

python plotting/plot_figure_1.py --extension "$extension"
python plotting/plot_figure_2.py --extension "$extension"
python plotting/plot_figure_3.py --extension "$extension"
python plotting/plot_figure_4.py --extension "$extension"
python plotting/plot_figure_5.py --extension "$extension"


python plotting/plot_supp_figure_1.py --extension "$extension"
python plotting/plot_supp_figure_2.py --extension "$extension"
python plotting/plot_supp_figure_3.py --extension "$extension"
python plotting/plot_supp_figure_4.py --extension "$extension"
python plotting/plot_supp_figure_5.py --extension "$extension"
python plotting/plot_supp_figure_6.py --extension "$extension"
python plotting/plot_supp_figure_7.py --extension "$extension"
python plotting/plot_supp_figure_8.py --extension "$extension"
python plotting/plot_supp_figure_9.py --extension "$extension"
python plotting/plot_supp_figure_10.py --extension "$extension"

# Other supplementary figures:
python plotting/plot_prs_correlation_matrix.py --extension "$extension"

python plotting/plot_prs_validation_metrics.py --chromosome "chr_2" --extension "$extension"
