import numpy as np


def set_figure_size(width, fraction=1, subplots=(1, 1), height_extra_pct=0., width_extra_pct=0.):
    """Set figure dimensions to avoid scaling in LaTeX.

    Modified from https://jwalton.info/Embed-Publication-Matplotlib-Latex/

    Parameters
    ----------
    width: float or string
            Document width in points, or string of predined document type
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    height_extra_pct: float
            Stretch the final height by percentage
    width_extra_pct: float
            Stretch the final width by percentage
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    if width == 'paper':
        width_pt = 505.89
    elif width == 'thesis':
        width_pt = 426.79135
    elif width == 'beamer':
        width_pt = 307.28987
    else:
        width_pt = width

    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return fig_width_in + fig_width_in*width_extra_pct, fig_height_in + fig_height_in*height_extra_pct


def add_hatch_to_facet_plot(g, patch_index=None, kind='bar', hatch="//"):

    from seaborn.axisgrid import FacetGrid

    if isinstance(g, FacetGrid):
        axes = g.axes.flatten()
    else:
        axes = [g]

    for ax in axes:

        if kind == 'bar':
            container = ax.patches
        elif kind == 'box':
            container = ax.artists

        for p_idx, patch in enumerate(container):

            if patch_index is not None:
                if p_idx not in patch_index:
                    continue
            patch.set_hatch(hatch)

    return g


def update_model_names(data_df):

    unique_models = data_df['Model'].unique()

    def process_search_model_names(base_model, strategy):

        model_name = f'{base_model}-{strategy}'

        strategy_models = [m for m in unique_models if model_name in m]

        if len(strategy_models) < 1:
            return {}

        search_names = [m.replace(model_name, '').split('_')[0] for m in strategy_models]

        # Check if some of the grids are localized while others are not:
        l_in_model = ['l' in m for m in search_names]

        # Check if all models used validation:
        v_in_model = ['v' in m for m in search_names]

        # Check if all models used pseudo-validation:
        p_in_model = ['p' in m for m in search_names]

        if sum(l_in_model) == len(l_in_model):
            search_names = [m.replace('l', '') for m in search_names]

        if sum(v_in_model) == len(v_in_model):
            search_names = [m.replace('v', '') for m in search_names]
        elif sum(p_in_model) == len(p_in_model):
            search_names = [m.replace('p', '') for m in search_names]
        else:
            for i in range(len(search_names)):
                if v_in_model[i]:
                    search_names[i] = '-val'
                elif p_in_model[i]:
                    search_names[i] = '-pseudoval'
                else:
                    search_names[i] = '-ELBO'

        # Check that the search was done over the same hyperparameters:
        param_in_model = ['_' + m.split('_')[1] for m in strategy_models]
        if len(set(param_in_model)) == 1:
            param_in_model = ['']*len(param_in_model)

        # If need be, replace the old model names:

        new_model_names = [model_name + search_names[i] + param_in_model[i] for i in range(len(strategy_models))]

        return dict(zip(strategy_models, new_model_names))

    update_dict = {}
    base_models = ['VIPRS', 'VIPRSMix', 'VIPRSAlpha']
    base_strategies = ['GS', 'BO', 'BMA']

    for bm in base_models:
        for st in base_strategies:
            update_dict.update(process_search_model_names(bm, st))

    for m in unique_models:
        if m not in update_dict:
            update_dict.update({m: m})

    data_df['Model'] = data_df['Model'].map(update_dict)

    return data_df


def add_lines_to_bars(ax, values, orientation='vertical', color='r', label=None):
    """
    Add vertical or horizontal lines to barplots
    :param ax: The axis on which to draw the lines
    :param values: The place where to add the line
    :param orientation: Orientation (vertical or horizontal)
    :param color: Color of the line
    """

    n_models = len(ax.patches) // len(values)

    if orientation == 'vertical':
        sorted_patches = sorted(ax.patches, key=lambda x: x.get_y())
    else:
        sorted_patches = sorted(ax.patches, key=lambda x: x.get_x())

    for i, p in enumerate(sorted_patches):

        if i > 0:
            label = None

        if i % n_models != 0 or i == len(ax.patches) - 1:
            continue

        if orientation == 'vertical':
            ax.vlines(ymin=p.get_y(), ymax=sorted_patches[i + n_models - 1].get_y() + p.get_height(),
                      x=values[i // n_models], colors=color, label=label)
        else:
            ax.hlines(xmin=p.get_x(), xmax=sorted_patches[i + n_models - 1].get_x() + p.get_width(),
                      y=values[i // n_models], colors=color, label=label)

    return ax


def add_labels_to_bars(g, rotation=90, fontsize='smaller'):
    """
    This function takes a barplot and adds labels above each bar with its value.
    """

    from seaborn.axisgrid import FacetGrid

    if isinstance(g, FacetGrid):
        axes = g.axes.flatten()
    else:
        axes = [g]

    for ax in axes:

        y_min, y_max = ax.get_ylim()
        scale = ax.get_yaxis().get_scale()

        for p, l in zip(ax.patches, ax.lines):

            if scale == 'linear':

                x_height = [l.get_ydata()[1], p.get_height()][np.isnan(l.get_ydata()[1])] - y_min

                if round(x_height, 3) > .5 * (y_max - y_min) and rotation == 90:
                    y = y_min + .5 * x_height
                else:
                    y = y_min + x_height * 1.05 + 0.05 * (y_max - y_min)
            else:

                x_height = l.get_ydata()[1]

                if np.log10(x_height) - np.log10(y_min) > .5 * (np.log10(y_max) - np.log10(y_min)) and rotation == 90:
                    y = 10 ** (.5 * (np.log10(x_height) - np.log10(y_min)) + np.log10(y_min))
                else:
                    y = 10 ** (np.log10(y_min) + (np.log10(x_height) - np.log10(y_min)) * 1.05 + .05 * (
                                np.log10(y_max) - np.log10(y_min)))

            ax.text(p.get_x() + .4,
                    y,
                    f'{p.get_height():.3f}',
                    color='black',
                    fontsize=fontsize,
                    rotation=rotation,
                    ha='center')


def add_labels_to_bars_vertical(ax, fontsize='smaller'):

    y_min, y_max = ax.get_ylim()

    for p in ax.patches:

        p_height = p.get_height()

        if round(p_height, 3) > .45 * (y_max - y_min):
            y = y_min + .5 * p_height
        else:
            y = y_min + p_height * 1.05 + 0.05 * (y_max - y_min)

        x = p.get_x() + .5*p.get_width()
        value = p.get_height()
        ax.text(x, y,
                f'{value:.3f}',
                ha="center",
                va="bottom",
                color='black',
                rotation=90,
                fontsize=fontsize)


def add_labels_to_bars_horizontal(ax, fontsize='smaller'):
    x_min, x_max = ax.get_xlim()

    for p in ax.patches:

        x_height = p.get_width()

        if round(x_height, 3) > .45 * (x_max - x_min):
            x = x_min + .5 * x_height
        else:
            x = x_min + x_height * 1.05 + 0.05 * (x_max - x_min)

        y = p.get_y() + p.get_height()
        value = p.get_width()
        ax.text(x, y,
                f'{value:.3f}',
                ha="left",
                va="bottom",
                color='black',
                fontsize=fontsize)


def sort_traits(trait_type, traits):

    if trait_type == 'quantitative':
        return [t for t in [
            'HEIGHT', 'HDL', 'BMI',
            'FVC', 'FEV1', 'HC',
            'WC', 'LDL', 'BW',
            'PASS_HEIGHT', 'PASS_HDL',
            'PASS_BMI', 'PASS_LDL'
        ] if t in traits]
    else:
        return [t for t in ['ASTHMA', 'T2D', 'T1D', 'RA', 'PASS_T2D', 'PASS_RA'] if t in traits]


def sort_simulations(sims):

    simulations = ['Proportion Causal: 0.01%', 'Proportion Causal: 0.1%', 'Proportion Causal: 1%',
                   'Sparse Mixture', 'Infinitesimal Mixture', 'Infinitesimal']

    return [s for s in simulations if s in sims]


def metric_name(metric):

    metrics = {
        'ROC-AUC': 'AUROC',
        'Average Precision': 'Average Precision',
        'PR-AUC': 'AUPRC',
        'R2': 'Prediction $R^2$',
        'Alt R2': 'Prediction $R^2$',
        'Full R2': 'Prediction $R^2$',
        'Naive R2': 'Prediction $R^2$',
        'Pearson Correlation': 'Correlation',
        'Partial Correlation': 'Partial Correlation',
        'Estimated Heritability': 'Estimated Heritability',
        'Estimated Prop. Causal': 'Estimated Prop. Causal'
    }

    return metrics[metric]


def sort_models(models):
    """
    :param models: A list of models to sort
    """

    def viprs_model_sort(m):

        num = 0

        if 'VIPRSMix' in m:
            num += 1
        elif 'VIPRSAlpha' in m:
            num += 2
        elif 'VIPRSSBayes' in m:
            num += 3
        elif 'VIPRSSBayesAlpha' in m:
            num += 4

        if '-GS' in m:
            num += 1000
        elif '-BO' in m:
            num += 2000
        elif '-BMA' in m:
            num += 3000

        for strategy in ('-GS', '-BO', '-BMA'):
            if strategy + 'vl' in m:
                num += 300
            elif strategy + 'l' in m:
                num += 200
            elif strategy + 'v' in m:
                num += 100

        if '_p' in m:
            num += 10
        elif '_e' in m:
            num += 20
        elif '_pe' in m:
            num += 30

        return num

    external_model_order = [
        'SBayesR',
        'Lassosum',
        'MegaPRS',
        'LDPred2-inf', 'LDPred2-auto', 'LDPred2-grid',
        'PRScs',
        'PRSice2',
    ]

    viprs_models = sorted([m for m in models if 'VIPRS' in m], key=viprs_model_sort)
    external_models = sorted([m for m in models if m in external_model_order],
                             key=lambda x: external_model_order.index(x))

    return viprs_models + external_models
