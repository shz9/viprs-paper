import sys
import pandas as pd

ss_file = sys.argv[1]

ss_df = pd.read_csv(sys.argv[1], sep="\t")
ss_df = ss_df[['SNP', 'A1', 'A2', 'MAF', 'BETA', 'SE', 'PVAL', 'N']]
ss_df.columns = ['SNP', 'A1', 'A2', 'freq', 'b', 'se', 'p', 'n']
ss_df.to_csv(ss_file.replace(".PHENO1.glm.linear", ".ma"), sep="\t", index=False)
