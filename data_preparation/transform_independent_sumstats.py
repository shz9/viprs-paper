import pandas as pd

# Transform the HEIGHT summary statistics data from Wood et al. (GIANT)
# to LDSC-style summary statistics:
wood_height = pd.read_csv("./data/gwas/quantitative/independent/Wood_HEIGHT/combined.sumstats", sep="\s+")

wood_height.rename(columns={
    'MarkerName': 'SNP',
    'Allele1': 'A1',
    'Allele2': 'A2'
}, inplace=True)

wood_height['Z'] = wood_height['b'] / wood_height['SE']
wood_height['CHISQ'] = wood_height['Z']**2

wood_height[['SNP', 'A1', 'A2', 'N', 'CHISQ', 'Z']].to_csv(
    "./data/gwas/quantitative/independent/Wood_HEIGHT/combined.sumstats", sep="\t", index=False
)

# -------------------------------------------------------------
# Transform the BMI summary statistics data from Locke et al. (GIANT)
# to LDSC-style summary statistics:

locke_bmi = pd.read_csv("./data/gwas/quantitative/independent/Locke_BMI/combined.sumstats", sep="\s+")

locke_bmi['Z'] = locke_bmi['b'] / locke_bmi['se']
locke_bmi['CHISQ'] = locke_bmi['Z']**2

locke_bmi[['SNP', 'A1', 'A2', 'N', 'CHISQ', 'Z']].to_csv(
    "./data/gwas/quantitative/independent/Locke_BMI/combined.sumstats", sep="\t", index=False
)

# -------------------------------------------------------------
# Transform the BMI meta-analyzed summary statistics data from Yengo et al.
# to LDSC-style summary statistics:

yengo_bmi = pd.read_csv("./data/gwas/quantitative/independent/Yengo_BMI/combined.sumstats", sep="\s+")

yengo_bmi.rename(columns={
    'Tested_Allele': 'A1',
    'Other_Allele': 'A2'
}, inplace=True)

yengo_bmi['Z'] = yengo_bmi['BETA'] / yengo_bmi['SE']
yengo_bmi['CHISQ'] = yengo_bmi['Z']**2

yengo_bmi[['SNP', 'A1', 'A2', 'N', 'CHISQ', 'Z']].to_csv(
    "./data/gwas/quantitative/independent/Yengo_BMI/combined.sumstats", sep="\t", index=False
)

# -------------------------------------------------------------
# Transform the HEIGHT meta-analyzed summary statistics data from Yengo et al.
# to LDSC-style summary statistics:

yengo_height = pd.read_csv("./data/gwas/quantitative/independent/Yengo_HEIGHT/combined.sumstats", sep="\s+")

yengo_height.rename(columns={
    'Tested_Allele': 'A1',
    'Other_Allele': 'A2'
}, inplace=True)

yengo_height['Z'] = yengo_height['BETA'] / yengo_height['SE']
yengo_height['CHISQ'] = yengo_height['Z']**2

yengo_height[['SNP', 'A1', 'A2', 'N', 'CHISQ', 'Z']].to_csv(
    "./data/gwas/quantitative/independent/Yengo_HEIGHT/combined.sumstats", sep="\t", index=False
)
