

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
    update_dict = {}

    base_models = ['VIPRS', 'VIPRSMix', 'VIPRSAlpha', 'VIPRSSBayes', 'VIPRSSBayesAlpha']

    for bm in base_models:

        gs_models = [m for m in unique_models if f'{bm}-GS' in m]
        bo_models = [m for m in unique_models if f'{bm}-BO' in m]

        if len(gs_models) > 0:
            if f'{bm}-GS' in gs_models:
                update_dict.update({m: m for m in gs_models})
            else:
                u_gs_models = [bm + '-' + gsm.split('-')[-1].replace('l', '') for gsm in gs_models]
                if len(u_gs_models) == 1:
                    update_dict.update({gs_models[0]: u_gs_models[0].replace('v', '')})
                else:
                    update_dict.update(dict(zip(gs_models, u_gs_models)))

        if len(bo_models) > 1:
            update_dict.update({m: m for m in bo_models})
        elif len(bo_models) == 1:
            update_dict.update({bo_models[0]: bo_models[0].replace('v', '')})

    for m in unique_models:
        if m not in update_dict:
            update_dict.update({m: m})

    data_df['Model'] = data_df['Model'].map(update_dict)

    return data_df


def add_labels_to_bars(g, rotation=90):
    """
    This function takes a barplot and adds labels above each bar with its value.
    """

    max_height = 0.

    for idx, ax in enumerate(g.axes.flatten()):
        for p in ax.patches:
            if p.get_height() > max_height:
                max_height = p.get_height()

    for ax in g.axes.flatten():
        for p in ax.patches:

            x_height = p.get_height()

            if x_height > .25*max_height and rotation == 90:
                y = .5*p.get_height()
            else:
                y = p.get_height() + 0.02

            ax.text(p.get_x() + .4,
                    y,
                    f'{x_height:.3f}',
                    color='black',
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
    Currently assumes that the models passed all exist in the `base_order` list below.
    :param models: A list of models to sort
    """

    base_order = [
        'VIPRS', 'VIPRSMix', 'VIPRSAlpha', 'VIPRSSBayes',
        'VIPRS-GS', 'VIPRSMix-GS', 'VIPRSAlpha-GS', 'VIPRSSBayes-GS',
        'VIPRS-GSv', 'VIPRSMix-GSv', 'VIPRSAlpha-GSv', 'VIPRSSBayes-GSv',
        'VIPRS-GSl', 'VIPRSMix-GSl', 'VIPRSAlpha-GSl', 'VIPRSSBayes-GSl',
        'VIPRS-GSvl', 'VIPRSMix-GSvl', 'VIPRSAlpha-GSvl', 'VIPRSSBayes-GSvl',
        'VIPRS-BO',  'VIPRSMix-BO', 'VIPRSAlpha-BO', 'VIPRSSBayes-BO',
        'VIPRS-BOv', 'VIPRSMix-BOv', 'VIPRSAlpha-BOv', 'VIPRSSBayes-BOv',
        'VIPRS-BMA', 'VIPRSMix-BMA', 'VIPRSAlpha-BMA', 'VIPRSSBayes-BMA',
        'SBayesR',
        'Lassosum',
        'LDPred2-inf', 'LDPred2-auto', 'LDPred2-grid',
        'PRScs',
        'PRSice2',
    ]

    return [m for m in base_order if m in models]
