library(bigsnpr)

# Read in the path to the bed file as an argument:
args <- commandArgs(trailingOnly=TRUE)
path_to_bed <- args[1]

bigsnpr_validation_path <- gsub("ukbb_qc_genotypes", "ukbb_qc_genotypes_bigsnpr", path_to_bed)

# Obtain the indices of individuals in the validation subset:
validation_subset <- read.table("data/keep_files/ukbb_valid_subset.keep",
                                header=FALSE, col.names=c('FID', 'IID'))
fam_list <- read.table(gsub(".bed", ".fam", path_to_bed), header=FALSE)[, 1:2]
names(fam_list) <- c('FID', 'IID')

ind_subset <- which(fam_list$IID %in% validation_subset$IID)

snp_readBed2(path_to_bed,
             backingfile=sub_bed(bigsnpr_validation_path),
             ind.row=ind_subset)
