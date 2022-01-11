# Variational PRS paper

## TODO List

- [ ] Update code for external PRS methods to be self-contained and replicable.
- [ ] Aggregate performance statistics and make them available on GitHub.
- [ ] Modify plotting scripts to have a script per figure.
- [ ] Re-run other variations of VIPRS method.
- [ ] Include scripts for analysis with 10m SNPs.


## Data 

In terms of the data that you need to reproduce the analyses, there 
are three main data sources:

1. [The 1000 Genomes Project genotype data](
ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/): This data source is used to compute 
reference LD matrices for analyses with summary statistics.
   
2. [The 1000G Phase III genetic map](https://mathgen.stats.ox.ac.uk/impute/1000GP%20Phase%203%20haplotypes%206%20October%202014.html): This is used to extract SNP positions along
the chromosome in CentiMorgan (cM). This is important to define LD boundaries for
   each SNP (e.g. by default, each SNP has a window of 1cM around it).

```shell
wget https://mathgen.stats.ox.ac.uk/impute/1000GP_Phase3.tgz
tar -xvzf 1000GP_Phase3.tgz
rm 1000GP_Phase3/*.gz
```   

3. The UKBB genotype and phenotype data.

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

