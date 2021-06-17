import sys
import os.path as osp
import pandas as pd
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.PRSModel import PRSModel


class PLINK_PT(PRSModel):

    def __init__(self,
                 sumstats_file,
                 validation_gdl,
                 clump_pval_threshold=1.,
                 clump_r2_threshold=.1,
                 clump_kb_threshold=250,
                 pval_thresholds=(0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5)):

        super().__init__(validation_gdl)

        self.ss_table = pd.read_csv(sumstats_file, sep="\s+")

        self.clump_pval_threshold = clump_pval_threshold
        self.clump_r2_threshold = clump_r2_threshold
        self.clump_kb_threshold = clump_kb_threshold
        self.pval_thresholds = pval_thresholds

        self.best_threshold = None
        self.best_r2 = None

    def fit(self):

        ss_tables = self.gdl.to_sumstats_table(per_chromosome=True)
        beta_hat = self.gdl.beta_hats
        p_vals = self.gdl.p_values

        clump_beta = beta_hat.copy()

        temp_files = []

        for bfile, ss_table, beta_key in zip(self.gdl.bed_files, ss_tables, beta_hat.keys()):

            clumped_prefix = f"temp/plink/{self.gdl.phenotype_id}_{osp.basename(bfile)}"
            temp_files.append(clumped_prefix)

            ss_table.to_csv(f"{clumped_prefix}.sumstats", index=False, sep="\t")

            clump_cmd = f"""
                plink \
                --bfile {bfile} \
                --clump-p1 {self.clump_pval_threshold} \
                --clump-r2 {self.clump_r2_threshold} \
                --clump-kb {self.clump_kb_threshold} \
                --clump {clumped_prefix}.sumstats \
                --clump-snp-field SNP \
                --clump-field PVAL \
                --out {clumped_prefix}
            """

            run_shell_script(clump_cmd)

            retained_snps = pd.read_csv(f"{clumped_prefix}.clumped", sep="\s+")
            clump_beta[beta_key][~clump_beta[beta_key].index.isin(retained_snps['SNP'])] = 0.

        # For the remaining SNPs, find the best p-value threshold:

        for pt in self.pval_thresholds:

            self.inf_beta = {}

            for i, beta in clump_beta.items():
                new_beta = beta.copy()
                new_beta[p_vals[i] > pt] = 0.
                self.inf_beta[i] = new_beta

            if all([not self.inf_beta[i].any() for i in self.inf_beta]):
                continue

            r2 = evaluate_predictive_performance(self.predict_phenotype(test=False),
                                                 self.gdl.phenotypes[self.gdl.train_idx])['R2']

            if self.best_threshold is None:
                self.best_threshold = pt
                self.best_r2 = r2
            elif r2 > self.best_r2:
                self.best_threshold = pt
                self.best_r2 = r2

        self.inf_beta = {}

        for i, beta in clump_beta.items():
            new_beta = beta.copy()
            new_beta[p_vals[i] > self.best_threshold] = 0.
            self.inf_beta[i] = new_beta

        # Delete temporary files:
        for f_pattern in temp_files:
            delete_temp_files(f_pattern)

        return self