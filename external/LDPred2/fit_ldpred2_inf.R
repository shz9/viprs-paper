# NOTE: This code is modified from:
# https://github.com/privefl/paper-ldpred2/blob/master/code/run-ldpred2-gwide.R#L34-L118

library(bigsnpr)
library(dplyr)

args <- commandArgs(trailingOnly=TRUE)
ss_dir_path <- args[1]
ss_type <- args[2]

# Get the number of available cores:
NCORES <- nb_cores()

# Extract information about the trait and configuration:
trait <- basename(ss_dir_path)
config <- basename(dirname(ss_dir_path))
trait_config <- gsub("_fold_[0-9]*", "", config)

# ----------------------------------------------------------
# Step 1: Prepare the GWAS summary statistics:

for (chr in 1:22){
  ss <- read.table(file.path(ss_dir_path, sprintf("chr_%d.PHENO1.glm.linear", chr)), header=TRUE)

  if (ss_type == "plink"){
    names(ss) <- c("chr", "pos", "rsid", "REF", "ALT1", "a1", "maf", "n_eff", "beta", "beta_se", "z", "p")
    ss$a0 <- mapply(function(ref, alt, a1) {if (ref == a1) alt else ref}, ss$REF, ss$ALT, ss$a1)
  } else{
    names(ss) <- c("chr", "pos", "rsid", "a0", "a1", "maf", "n_eff", "beta", "z", "beta_se", "p")
  }

  if (chr == 1){
    sumstats <- ss
  } else{
    sumstats <- rbind(sumstats, ss)
  }
}

# ----------------------------------------------------------
# Step 2: Match the GWAS summary statistics and the LD reference panel

map_ldref <- readRDS("~/projects/def-sgravel/data/ld/ukb_eur_ldpred2_ld/map.rds")

sumstats <- snp_match(sumstats, map_ldref, join_by_pos=F)
(sumstats <- tidyr::drop_na(tibble::as_tibble(sumstats)))

tmp <- tempfile(tmpdir = Sys.getenv("SLURM_TMPDIR", unset="temp"))
on.exit(file.remove(paste0(tmp, ".sbk")), add = TRUE)

for (chr in 1:22) {

  print(paste("> Matching chromosome:", chr))

  ## indices in 'sumstats'
  ind.chr <- which(sumstats$chr == chr)
  ## indices in 'corr'
  ind.chr2 <- sumstats$`_NUM_ID_`[ind.chr]
  ## indices in 'corr'
  ind.chr3 <- match(ind.chr2, which(map_ldref$chr == chr))

  corr0 <- readRDS(sprintf("~/projects/def-sgravel/data/ld/ukb_eur_ldpred2_ld/LD_chr%d.rds", chr))[ind.chr3, ind.chr3]

  if (chr == 1) {
    df_beta <- sumstats[ind.chr, c("beta", "beta_se", "n_eff", "_NUM_ID_")]
    ld <- Matrix::colSums(corr0^2)
    corr <- as_SFBM(corr0, tmp)
  } else {
    df_beta <- rbind(df_beta, sumstats[ind.chr, c("beta", "beta_se", "n_eff", "_NUM_ID_")])
    ld <- c(ld, Matrix::colSums(corr0^2))
    corr$add_columns(corr0, nrow(corr))
  }
}

subset_map_ldref <- map_ldref[df_beta$`_NUM_ID_`,]

# ----------------------------------------------------------
# Step 3: Perform model fitting

(ldsc <- with(df_beta, snp_ldsc(ld, length(ld), chi2 = (beta / beta_se)^2,
                                sample_size = n_eff, blocks = NULL,
                                ncores = NCORES)))
h2_est <- ldsc[["h2"]]

print("Performing model fit...")
beta_inf <- snp_ldpred2_inf(corr, df_beta, h2_est, ncores = NCORES)

# ----------------------------------------------------------
# Step 4: Write the posterior effect sizes

# Create the output directory:

dir.create(sprintf("data/model_fit/external/LDPred2-inf/%s/%s/", config, trait),
           showWarnings = FALSE,
           recursive = TRUE)

# Write out the effect sizes:
print("Writing the results to file...")

for (chr in 1:22) {
  chr_snp_cond <- subset_map_ldref$chr == chr
  chr_sumstats <- subset_map_ldref[chr_snp_cond, c("chr", "rsid", "a1", "a0")]
  chr_sumstats$PIP <- NA

  # Write out the beta_inf results:
  chr_sumstats$BETA <- beta_inf[chr_snp_cond]
  names(chr_sumstats) <- c("CHR", "SNP", "A1", "A2", "PIP", "BETA")
  write.table(chr_sumstats,
              sprintf("data/model_fit/external/LDPred2-inf/%s/%s/chr_%d.fit", config, trait, chr),
              row.names = F,
              sep = "\t")
}
