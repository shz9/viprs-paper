# Fast and Accurate Bayesian Polygenic Risk Modeling with Variational Inference (2022)

By: Shadi Zabad, Simon Gravel, and Yue Li
<br />McGill University

This repository contains reproducible code to replicate the analyses in our upcoming publication describing 
the Variational Inference of Polygenic Risk Scores (`VIPRS`) method. The repository includes scripts for all the 
steps in the analyses, from data pre-processing and QC, all the way to figure generation and plotting.

If you would like to run this method on your dataset of choice, please consult the pages for the main software packages powering these analyses:

- `magenpy`: [Modeling and Analysis of (Statistical) Genetics data](https://github.com/shz9/magenpy)
- `viprs`: [Variational Inference of Polygenic Risk Scores](https://github.com/shz9/viprs)

In what follows, we will describe the steps and the workflow to replicate the analyses described in the paper.

## Required data 

In terms of the data that you need to reproduce the analyses, there 
are three main data sources:

1. ~~The 1000 Genomes Project genotype data: This data source is used to compute 
reference LD matrices for analyses with summary statistics. You can download 1000G data from here:
ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/~~
   
2. [The 1000G Phase III genetic map](https://mathgen.stats.ox.ac.uk/impute/1000GP%20Phase%203%20haplotypes%206%20October%202014.html): This is used to extract SNP positions along the chromosome in Centi Morgan (cM). This is important to define LD boundaries for each SNP (e.g. by default, each SNP has a window of 3cM around it). You can download the genetic map into the desired folder as follows:

```shell
wget https://mathgen.stats.ox.ac.uk/impute/1000GP_Phase3.tgz
tar -xvzf 1000GP_Phase3.tgz
rm 1000GP_Phase3/*.gz
```   

3. The UK Biobank (UKB) genotype and phenotype data: You will need to [apply for access](https://www.ukbiobank.ac.uk/enable-your-research/apply-for-access) via the AMS portal to gain access to this dataset.

## Getting started

In order to replicate these analyses, we assume that the user has access to a compute cluster with:

- SLURM workload manager system.
- python 3.7 

You can replicate some of these analyses on your personal machine, but you would have to significantly modify (some) the scripts provided.

To get started, navigate to a folder of choice on your cluster and execute the following commands:

```shell
git clone https://github.com/shz9/viprs-paper.git
cd viprs-paper
source starter_script.sh
```

This will clone the current repository from GitHub, and execute the [starter script](https://github.com/shz9/viprs-paper/blob/master/starter_script.sh), which installs all the required python dependencies in a new virtual environment called `pyenv`. If you wish to change the name of the virtual environment or its location, be mindful that you may need to propagate this change to some of the downstream scripts. The starter script also compiles the `cython` code in the `magenpy` and `viprs` packages.

Once the previous steps executed successfully, you will need to inspect the [global_config.sh](https://github.com/shz9/viprs-paper/blob/master/global_config.sh) script to set the relevant configurations and paths on your system. In particular, 
make sure to change the paths for:

- The UK Biobank genotype data (the imputed `.bgen` files)
- The UK Biobank phenotype data
- The directory for the files with the genetic map.

The UKB files structure on your system may differ from what we assume in our scripts, so it is also a good idea to inspect some of the downstream scripts to make sure that the specified paths are valid.

## Data pre-processing and QC

To prepare the raw genotype data for the downstream analyses, you will need to run the scripts in the `data_preparation` folder.
The following order of operations is recommended, though some of these steps can in principle be run in parallel:

0. Ensure that the `pyenv` environment is activated:

```shell
source ~/pyenv/bin/activate
```

1. Run the sample and SNP QC filtering scripts:

```shell
python data_preparation/generate_qc_filters.py
```

2. Submit the batch jobs to perform QC and filtering on the genotype data and transform it into `.bed` format:

```shell
source data_preparation/batch_qc.sh
```

3. Harmonize the genotype data across chromosomes:

```shell
source data_preparation/harmonize_ukbb_genotypes.sh
```

4. Submit batch job to compute the LD matrices (you may modify this script to only compute matrices for the windowed estimator with 50k sample size):

```shell
source data_preparation/batch_ld.sh 
```

5. Extract and transform real phenotypes for the UKB participants:

```shell
python data_preparation/prepare_real_phenotypes.py
```

6. Split the samples into 5 training/validation/testing folds:

```shell
python data_preparation/generate_cv_folds.py
```

7. Generate a table of the effect sample size for each phenotype:

```shell
python data_preparation/generate_train_sample_size.py
```

8. Download and transform external GWAS summary statistics:

```shell
source data_preparation/download_external_sumstats.sh
python data_preparation/transform_external_sumstats.py
```

## Simulations

To generate simulated quantitative and binary traits, you can submit genome-wide simulation jobs by invoking the command:

```shell
source simulation/batch_simulations.sh
```

## GWAS summary statistics

To generate GWAS summary statistics, we use the `plink2` software. To submit jobs that generate GWAS summary statistics to all simulated and real phenotypes for the UK Biobank participants, invoke the following script:

```shell
python gwas/batch_gwas.py
```

## Model fitting

Once the GWAS summary statistics have been generated, the next step is to perform model fitting. For the `viprs` software, you can perform model fitting by following the analysis commands in `model_fit/analysis_commands.sh`. For instance, to run the standard `VIPRS` model shown in the main figures of the paper, you can submit jobs as follows:

```shell
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed
```

Whereas to run the grid search version of the model `VIPRS-GS`, you need to modify the command above to the following:

```shell
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed --strategy GS --opt-params pi --grid-metric validation
```

The script `fit_prs.py` shows how to use the `viprs` software for model fitting, if you need to tweak it for your particular dataset.

------

To run external PRS methods on the GWAS summary statistics, you need to execute the setup script for each method separately and then submit the jobs. The setup scripts download the software, create virtual environments, and install dependencies for each PRS method. For example, to run `Lassosum`, all you need is to execute the setup file and then submit the jobs to perform model fitting:

```shell
source external/Lassosum/setup_lassosum_environment.sh
python external/Lassosum/batch_lassosum.py
```

For some methods, such as `SBayesR`, you may need to transform the GWAS summary statistics into, e.g. the COJO format. In that case, you may need to execute the `transform_sumstats.py` script before you run the method:

```shell
source external/SBayesR/setup_sbayesr_environment.sh
source external/SBayesR/transform_sumstats_job.sh
python external/SBayesR/batch_sbayesr.py
```

## Individual scoring (Generating PGS)

To generate PRS for individuals in the test sets, you need to run the scoring scripts for each method. Some of these commands are listed in the `score/analysis_commands.sh` script. For example, to generate PGS from the standard `VIPRS` model, you can submit jobs as follows:

```shell
python score/batch_score.py -m VIPRS -l ukbb_50k_windowed
```

To generate PGS for an external method, such as `SBayesR`, you can also submit jobs as follows:

```shell
python score/batch_score.py -m SBayesR -l external
```

## Evaluation

Once the polygenic scores for individuals in the test set have been generated, the next step is to evaluate the predictive performance of the various PRS models. To do this, you can simply execute the following python script:

```shell
python evaluation/predictive_performance.py
```

## 10m SNPs analysis

To replicate the analysis with the 10 million SNPs, you need to execute the scripts in the `analysis_10m_snps` directory. The order of operations is similar to what we described above. You need to start with executing the scripts in the data preprocessing folder (`analysis_10m_snps/data_preparation`), then moving onto the GWAS step (`analysis_10m_snps/gwas`), model fitting (`analysis_10m_snps/model_fit`), scoring (`analysis_10m_snps/score`), and evaluation (`analysis_10m_snps/evaluation`).

## Multi-population analysis

Similarly, to replicate the multi-population analysis, you need to execute the scripts in `multi_pop_analysis`, starting with data preprocessing (`multi_pop_analysis/data_preparation`), scoring (`multi_pop_analysis/score`), and evaluation (`multi_pop_analysis/evaluation`).

## Generating figures and plots

Finally, to generate the figures and plots you see in the manuscript, you can execute the bash script in the `plotting` directory:

```shell
source plotting/batch_plot.sh
```

## Questions and inquiries

If you have any questions or inquiries about any of the steps in this analysis, feel free to open an issue under this GitHub repo or email the corresponding authors on the manuscript.
