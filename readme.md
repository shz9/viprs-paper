# Variational PRS paper

## Steps to reproduce the analyses

1. Run the sample QC script, which selects individuals 
that match certain QC criteria, computes the covariates file 
and splits the samples into 3 categories: LD computation, training, testing:

```shell
python data_preparation/sample_qc.py
```

2. Run the `snp_qc.sh` script for each of the autosomal chromosomes:

```shell
for chr in {1..22}
do
    sbatch ./data_preparation/snp_qc.sh "$chr"
done
```

3. Compute the LD matrices by calling the python module:

```shell
python data_preparation/compute_ld_matrices.py
```

4. Simulate phenotypes for all samples and using the configurations specified in the script:

```shell
python simulation/simulate_phenotypes.py
```

5. Run GWAS on the simulated phenotypes using PLINK:

```shell
for f in {}
do
  sbatch gwas/run_gwas_plink.sh 
done
```

6. Fit the variational PRS model to the summary statistics using:

```shell
python fit_vi_prs.py
```

