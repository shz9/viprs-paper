

def add_labels_to_bars(g):
    """
    This function takes a barplot and adds labels above each bar with its value.
    """
    for ax in g.axes.flatten():
        for p in ax.patches:
            ax.text(p.get_x() + .4,
                    p.get_height() + 0.02,
                    f'{p.get_height():.3f}',
                    color='black',
                    rotation='horizontal',
                    ha='center')
