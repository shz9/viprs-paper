library(bigsnpr)

# Read in the path to the sumstats file as an argument:
args <- commandArgs(trailingOnly=TRUE)
path_to_ss <- args[1]
chr <- 22
NCORES <- nb_cores()

# Get the trait name and the simulation configuration:
trait_dir <- dirname(path_to_ss)
trait <- basename(trait_dir)
config <- basename(dirname(trait_dir))

# Read the reference LD panel:

map_ldref <- readRDS("~/projects/def-sgravel/data/ld/ukb_eur_ldpred2_ld/map.rds")
corr <- readRDS("~/projects/def-sgravel/data/ld/ukb_eur_ldpred2_ld/LD_chr22.rds")

# Load the validation dataset:
obj.bigSNP <- snp_attach("data/ukbb_qc_genotypes_bigsnpr/chr_22.rds")

G   <- obj.bigSNP$genotypes
CHR <- obj.bigSNP$map$chromosome
POS <- obj.bigSNP$map$physical.pos

map_valid <- obj.bigSNP$map[-(2:3)]
names(map_valid) <- c("chr", "pos", "a0", "a1")

# Read the phenotypes for the validation set:
y <- read.table(paste0("data/simulated_phenotypes/", config, "/", trait, ".txt"),
                header=FALSE, col.names=c('FID', 'IID', 'phenotype'))
y <- y[y$IID %in% obj.bigSNP$fam$sample.ID, 'phenotype']

# Read the summary statistics:

ss <- read.table(path_to_ss, header=TRUE)
names(ss) <- c("chr", "pos", "rsid", "a0", "a1", "maf", "n_eff", "beta", "z", "beta_se", "p")

# Match the summary statistics with the LD reference panel SNPs
info_snp <- snp_match(ss, map_ldref)

# Filter SNPs that have significant mismatch between reference panels and summary statistics:
(info_snp <- tidyr::drop_na(tibble::as_tibble(info_snp)))

sd_ldref <- with(info_snp, sqrt(2 * af_UKBB * (1 - af_UKBB)))
sd_ss <- with(info_snp, 2 / sqrt(n_eff * beta_se^2))

is_bad <-
  sd_ss < (0.5 * sd_ldref) | sd_ss > (sd_ldref + 0.1) | sd_ss < 0.1 | sd_ldref < 0.05

df_beta <- info_snp[!is_bad, ]

# Make sure that the SNPs are also present in the validation dataset:

in_valid <- vctrs::vec_in(df_beta[, c("chr", "pos")], map_valid[, c("chr", "pos")])
df_beta <- df_beta[in_valid, ]

# Filter the reference correlation matrix:

ind.chr <- which(df_beta$chr == chr)
# indices in 'map_ldref'
ind.chr2 <- df_beta$`_NUM_ID_`[ind.chr]
# indices in 'corr_chr'
ind.chr3 <- match(ind.chr2, which(map_ldref$chr == chr))

corr0 <- corr[ind.chr3, ind.chr3]

# Estimate heritability:

(ldsc <- snp_ldsc2(corr0, df_beta))
h2_est <- ldsc[["h2"]]

# Fit LDPred2-auto:
multi_auto <- snp_ldpred2_auto(corr0, df_beta, h2_init = h2_est,
                               vec_p_init = seq_log(1e-4, 0.5, length.out = NCORES),
                               ncores = NCORES)
beta_auto <- sapply(multi_auto, function(auto) auto$beta_est)

