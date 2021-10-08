library(lassosum)
library(data.table)
library(parallel)

args <- commandArgs(trailingOnly=TRUE)
ss_dir_path <- args[1]
ss_type <- args[2]

# Extract information about the trait and configuration:
trait <- basename(ss_dir_path)
config_dir <- dirname(ss_dir_path)
config <- basename(config_dir)
trait_type <- basename(dirname(config_dir))
trait_config <- gsub("_fold_[0-9]*", "", config)

if (trait_type == "binary"){
  reg_type <- "logistic"
} else {
  reg_type <- "logistic"
}

# Options for Lassosum:
LDblocks <- "EUR.hg19"
ref_dir <- "data/ukbb_qc_genotypes"
ref_keep <- "data/keep_files/ukbb_ld_10k_subset.keep"
validation_dir <- "data/ukbb_qc_genotypes"

if (trait_config == "real"){
  validation_keep <- sprintf("data/keep_files/ukbb_cv/%s/%s/%s/validation.keep",
                             trait_type, trait, gsub("real_", "", config))
} else{
  validation_keep <- "data/keep_files/ukbb_valid_subset.keep"
}

cl <- makeCluster(7)

for (chr in 1:22) {

  print(sprintf("Processing Chromosome %d", chr))
  ss <- read.table(file.path(ss_dir_path, sprintf("chr_%d.PHENO1.glm.%s", chr, reg_type)), header=TRUE)

  if (ss_type == "plink"){
    names(ss) <- c("chr", "pos", "rsid", "REF", "ALT1", "a1", "maf", "n", "beta", "beta_se", "z", "p")
  }
  else{
    names(ss) <- c("chr", "pos", "rsid", "a0", "a1", "maf", "n", "beta", "z", "beta_se", "p")
  }

  cor <- p2cor(p = ss$p, n = max(ss$n), sign = ss$beta)

  # Remove SNPs with undefined correlations:
  na_idx <- which(is.na(cor))

  if (length(na_idx) != 0) {
    cor <- cor[-na_idx]
    ss <- ss[-na_idx,]
  }

  out_chr <- lassosum.pipeline(cor=cor, chr=ss$CHR, pos=ss$pos, A1=ss$a1, snp=ss$rsid,
                               ref.bfile=file.path(ref_dir, sprintf("chr_%d", chr)),
                               test.bfile=file.path(validation_dir, sprintf("chr_%d", chr)),
                               keep.ref=ref_keep,
                               keep.test=validation_keep,
                               LDblocks=LDblocks,
                               cluster=cl)

  if (chr == 1){
    out <- out_chr
    combined_ss <- ss
  }
  else {
    out <- merge(out, out_chr)
    combined_ss <- rbind(combined_ss, ss)
  }
}

# Read the phenotype for the validation set:
pheno <- read.table(paste0("data/phenotypes/", trait_type, "/", trait_config, "/", trait, ".txt"),
                    header=FALSE, col.names=c('FID', 'IID', 'phenotype'))
valid_df <- read.table(validation_keep, header=FALSE, col.names=c('FID', 'IID'))
pheno <- merge(pheno, valid_df)

# Validation with phenotype
v <- validate(out, pheno=pheno)

# Extract the best betas from the validation object:

inf_eff_df <- data.frame(rsid=out$sumstats$snp,
                         A1=out$sumstats$A1,
                         A2=out$sumstats$A2,
                         BETA=v$best.beta)
final_res_df <- merge(combined_ss[,c("chr", "rsid", "pos")], inf_eff_df)
final_res_df <- final_res_df[with(final_res_df, order(chr, pos)),]
final_res_df$PIP <- NA
final_res_df <- final_res_df[, c("chr", "rsid", "A1", "A2", "PIP", "BETA")]
names(final_res_df) <- c("CHR", "SNP", "A1", "A2", "PIP", "BETA")

# Create the output directory:

dir.create(sprintf("data/model_fit/external/Lassosum/%s/%s/%s/", trait_type, config, trait),
           showWarnings = FALSE,
           recursive = TRUE)

# Write out the results by chromosome:

for (chr in 1:22) {
  chr_sumstats <- final_res_df[final_res_df$CHR == chr,]
  write.table(chr_sumstats,
              sprintf("data/model_fit/external/Lassosum/%s/%s/%s/chr_%d.fit", trait_type, config, trait, chr),
              row.names = F,
              sep = "\t")
}
