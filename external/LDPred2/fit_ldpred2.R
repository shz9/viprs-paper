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
# Step 1: Prepare the validation dataset:
# Obtain the indices of individuals in the validation subset:

# 1.1: Read the validation subset file:

if (trait_config == "real"){
  validation_subset_path <- sprintf("data/keep_files/ukbb_cv/%s/%s/validation.keep", trait, gsub("real_", "", config))
}
else{
  validation_subset_path <- "data/keep_files/ukbb_valid_subset.keep"
}

validation_subset <- read.table(validation_subset_path,
                                header=FALSE, col.names=c('FID', 'IID'))
fam_list <- read.table("data/ukbb_qc_genotypes/combined.fam", header=FALSE)[, 1:2]
names(fam_list) <- c('FID', 'IID')

ind_subset <- which(fam_list$IID %in% validation_subset$IID)

# Prepare the genotype file for the validation set:
backing_file <- tempfile(tmpdir = Sys.getenv("SLURM_TMPDIR", unset="temp"))
on.exit(file.remove(paste0(backing_file, ".rds")), add = TRUE)

# Read the bigSNP object:
obj.bigSNP <- snp_attach("data/ukbb_qc_genotypes/UKBB_imp_hm3.rds")

# Subset the bigSNP object:
obj.bigSNP <- snp_attach(subset(obj.bigSNP,
                                ind.row = ind_subset,
                                backingfile = backing_file))

G   <- obj.bigSNP$genotypes
CHR <- obj.bigSNP$map$chromosome
POS <- obj.bigSNP$map$physical.pos

map_valid <- obj.bigSNP$map[-(2:3)]
names(map_valid) <- c("chr", "pos", "a0", "a1")

# Read the phenotypes for the validation set:
y <- read.table(paste0("data/phenotypes/", trait_config, "/", trait, ".txt"),
                header=FALSE, col.names=c('FID', 'IID', 'phenotype'))
y <- left_join(fam_list, y)$phenotype

ind.val2 <- ind_subset[!is.na(y[ind_subset])]

# ----------------------------------------------------------
# Step 2: Prepare the GWAS summary statistics:

for (chr in 1:22){
  ss <- read.table(file.path(ss_dir_path, sprintf("chr_%d.PHENO1.glm.linear", chr)), header=TRUE)

  if (ss_type == "plink"){
    names(ss) <- c("chr", "pos", "rsid", "REF", "ALT1", "a1", "maf", "n_eff", "beta", "beta_se", "z", "p")
    ss$a0 <- mapply(function(ref, alt, a1) {if (ref == a1) alt else ref}, ss$REF, ss$ALT, ss$a1)
  }
  else{
    names(ss) <- c("chr", "pos", "rsid", "a0", "a1", "maf", "n_eff", "beta", "z", "beta_se", "p")
  }

  if (chr == 1){
    sumstats <- ss
  }
  else{
    sumstats <- rbind(sumstats, ss)
  }
}

# ----------------------------------------------------------
# Step 3: Match the GWAS summary statistics and the LD reference panel

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
  ## indices in 'G'
  ind.chr3 <- match(ind.chr2, which(CHR == chr))
  #ind.chr3 <- ind.chr3[!is.na(ind.chr3)]

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

# ----------------------------------------------------------
# Step 4: Perform model fitting

(ldsc <- with(df_beta, snp_ldsc(ld, length(ld), chi2 = (beta / beta_se)^2,
                                sample_size = n_eff, blocks = NULL)))
h2_est <- ldsc[["h2"]]

# -------------------------
# Step 4.1: LDpred2-inf
beta_inf <- snp_ldpred2_inf(corr, df_beta, h2_est)

# -------------------------
# Step 4.2: LDpred2-grid
(h2_seq <- round(h2_est * c(0.7, 1, 1.4), 4))
(p_seq <- signif(seq_log(1e-5, 1, length.out = 21), 2))
(params <- expand.grid(p = p_seq, h2 = h2_seq))

beta_grid <- snp_ldpred2_grid(corr, df_beta, params, ncores = NCORES)
params$sparsity <- colMeans(beta_grid == 0)

bigparallelr::set_blas_ncores(NCORES)
pred_grid <- big_prodMat(G, beta_grid, ind.row = ind.val2,
                         ind.col = df_beta[["_NUM_ID_"]])
params$score <- big_univLogReg(as_FBM(pred_grid), y[ind.val2])$score


best_beta_grid <- params %>%
  mutate(id = row_number()) %>%
  arrange(desc(score)) %>%
  slice(1) %>%
  pull(id) %>%
  beta_grid[, .]

# -------------------------
# Step 4.3: LDpred2-auto
multi_auto <- snp_ldpred2_auto(corr, df_beta, h2_init = h2_est,
                               vec_p_init = seq_log(1e-4, 0.9, 30),
                               ncores = NCORES)
beta_auto <- sapply(multi_auto, function(auto) auto$beta_est)
pred_auto <- big_prodMat(G, beta_auto, ind.row = ind.val,
                         ind.col = df_beta[["_NUM_ID_"]])
sc <- apply(pred_auto, 2, sd)
keep <- abs(sc - median(sc)) < 3 * mad(sc)
final_beta_auto <- rowMeans(beta_auto[, keep])

# ----------------------------------------------------------
# Step 5: Write the posterior effect sizes according to the 3 models:

for (chr in 1:22) {
  snp_cond <- sumstats$chr == chr
  chr_sumstats <- sumstats[snp_cond, c("chr", "rsid", "a1", "a0")]
  chr_sumstats$PIP <- NA

  # Write out the beta_inf results:
  chr_sumstats$BETA <- beta_inf[snp_cond]
  write.table(chr_sumstats,
              sprintf("data/model_fit/external/LDPred2-inf/%s/%s/chr_%d.fit", config, trait, chr),
              row.names = F,
              sep = "\t")

  # Write out the grid search results:
  chr_sumstats$BETA <- best_beta_grid[snp_cond]
  write.table(chr_sumstats,
              sprintf("data/model_fit/external/LDPred2-grid/%s/%s/chr_%d.fit", config, trait, chr),
              row.names = F,
              sep = "\t")

  # Write out the auto results:
  chr_sumstats$BETA <- final_beta_auto[snp_cond]
  write.table(chr_sumstats,
              sprintf("data/model_fit/external/LDPred2-auto/%s/%s/chr_%d.fit", config, trait, chr),
              row.names = F,
              sep = "\t")
}
