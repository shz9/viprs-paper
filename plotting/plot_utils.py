
def update_model_names(data_df):

    unique_models = data_df['Model'].unique()
    update_dict = {}

    gs_models = [m for m in unique_models if '-GS' in m]
    bo_models = [m for m in unique_models if '-BO' in m]

    if len(gs_models) > 0:
        if 'VIPRS-GS' in gs_models:
            update_dict.update({m: m for m in gs_models})
        else:
            u_gs_models = [gsm.replace('l', '') for gsm in gs_models]
            if len(u_gs_models) == 1:
                update_dict.update({gs_models[0]: u_gs_models[0].replace('v', '')})
            else:
                update_dict.update(dict(zip(gs_models, u_gs_models)))

    if len(bo_models) > 1:
        update_dict.update({m: m for m in bo_models})
    elif len(bo_models) == 1:
        update_dict.update({bo_models[0]: bo_models[0].replace('v', '')})

    for m in unique_models:
        if m not in gs_models and m not in bo_models:
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


def real_trait_order(trait_type):

    if trait_type == 'quantitative':
        return [
            'HEIGHT', 'HDL', 'BMI',
            'FVC', 'FEV1', 'HC',
            'WC', 'LDL', 'BW'
        ]
    else:
        return ['ASTHMA', 'T2D', 'T1D', 'RA']