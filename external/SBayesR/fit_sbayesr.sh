#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=00:30:00
#SBATCH --output=./log/model_fit/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

gctb_bin="$HOME/projects/def-sgravel/bin/gctb_v2.03/gctb"

trait_dir=$(dirname $2)
trait=$(basename "$trait_dir")
config_dir=$(dirname $trait_dir)
config=$(basename "$config_dir")

gctb_bin --sbayes R \
         --ldm "$1" \
         --pi 0.95,0.02,0.02,0.01 \
         --gamma 0.0,0.01,0.1,1 \
         --gwas-summary "$2" \
         --chain-length 10000 \
         --burn-in 2000 \
         --out-freq 100 \
         --out "data/model_fit/external/sbayesr/$config/$trait/chr_22"

