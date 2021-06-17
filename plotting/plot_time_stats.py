import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

time_df = []

for log_f in glob.glob("log/model_fit/*/*/*.out"):

    _, _, panel, model, _ = log_f.split('/')

    try:
        with open(log_f, 'r') as f:
            lines = f.read().splitlines()
            duration = float(lines[-1].split(':')[-1].strip())

        time_df.append({'LD Panel': panel, 'Model': model, 'Duration': duration})

    except Exception as e:
        print(e)
        continue

time_df = pd.DataFrame(time_df)

for ldp in time_df['LD Panel'].unique():

    if ldp == 'external':
        continue

    df = time_df.loc[time_df['LD Panel'].isin(['external', ldp])]

    plt.figure(figsize=(9, 6))
    ax = sns.boxplot(x="Model", y="Duration", hue="Model", data=df)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.ylabel("Runtime (Minutes)")
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    makedir(f"plots/{ldp}")

    plt.savefig(f"plots/{ldp}/runtime.pdf", bbox_inches='tight')
    plt.close()
