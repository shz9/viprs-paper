

def set_figure_size(width, fraction=1, subplots=(1, 1)):
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

    return fig_width_in, fig_height_in


def update_model_names(data_df):

    unique_models = data_df['Model'].unique()

    def process_search_model_names(base_model, strategy):

        model_name = f'{base_model}-{strategy}'

        strategy_models = [m for m in unique_models if model_name in m]

        if len(strategy_models) < 1:
            return {}

        # Check if some of the grids are localized while others are not:
        l_in_model = ['l' in m.replace(model_name, '').split('_')[0] for m in strategy_models]

        # Check if there are models with different grid metrics (validation vs. ELBO):
        v_in_model = ['v' in m.replace(model_name, '').split('_')[0] for m in strategy_models]

        # Check that the search was done over the same hyperparameters:
        param_in_model = [m.split('_')[1] for m in strategy_models]

        # If need be, replace the old model names:

        new_model_names = [m.replace(model_name, '') for m in strategy_models]

        # If all models include a localized grid, remove the `l` modifier:
        if sum(l_in_model) == len(l_in_model):
            new_model_names = [m.replace('l', '') for m in new_model_names]

        # If all models evaluated performance with a validation set:
        if sum(v_in_model) == len(v_in_model):
            new_model_names = [m.replace('v', '') for m in new_model_names]

        # If all models searched the same hyperparameters:
        if len(set(param_in_model)) == 1:
            new_model_names = [m.split('_')[0] for m in new_model_names]

        new_model_names = [model_name + m for m in new_model_names]

        return dict(zip(strategy_models, new_model_names))

    update_dict = {}
    base_models = ['VIPRS', 'VIPRSMix', 'VIPRSAlpha', 'VIPRSSBayes', 'VIPRSSBayesAlpha']
    base_strategies = ['GS', 'BO', 'BMA']

    for bm in base_models:
        for st in base_strategies:
            update_dict.update(process_search_model_names(bm, st))

    for m in unique_models:
        if m not in update_dict:
            update_dict.update({m: m})

    data_df['Model'] = data_df['Model'].map(update_dict)

    return data_df


def add_labels_to_bars(g, rotation=90, fontsize='smaller'):
    """
    This function takes a barplot and adds labels above each bar with its value.
    """

    for ax in g.axes.flatten():

        y_min, y_max = ax.get_ylim()

        for p in ax.patches:

            x_height = p.get_height() - y_min

            if x_height > .3*(y_max - y_min) and rotation == 90:
                y = y_min + .5*x_height
            else:
                y = y_min + x_height + 0.02

            ax.text(p.get_x() + .4,
                    y,
                    f'{p.get_height():.3f}',
                    color='black',
                    fontsize=fontsize,
                    rotation=rotation,
                    ha='center')


def sort_traits(trait_type, traits):

    if trait_type == 'quantitative':
        return [t for t in [
            'HEIGHT', 'HDL', 'BMI',
            'FVC', 'FEV1', 'HC',
            'WC', 'LDL', 'BW'
        ] if t in traits]
    else:
        return [t for t in ['ASTHMA', 'T2D', 'T1D', 'RA'] if t in traits]


def metric_name(metric):

    pred_metrics = {
        'ROC-AUC': 'ROC-AUC',
        'Average Precision': 'Average Precision',
        'PR-AUC': 'PR-AUC',
        'R2': 'Prediction $R^2$',
        'Alt R2': 'Prediction $R^2$',
        'Full R2': 'Prediction $R^2$',
        'Naive R2': 'Prediction $R^2$',
        'Pearson Correlation': 'Correlation',
        'Partial Correlation': 'Partial Correlation'
    }

    return pred_metrics[metric]


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
        'LDPred2-inf', 'LDPred2-auto', 'LDPred2-grid',
        'PRScs',
        'PRSice2',
    ]

    viprs_models = sorted([m for m in models if 'VIPRS' in m], key=viprs_model_sort)
    external_models = sorted([m for m in models if m in external_model_order],
                             key=lambda x: external_model_order.index(x))

    return viprs_models + external_models
