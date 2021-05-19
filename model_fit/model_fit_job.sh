#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/model_fit/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

model=${2:-"vem_c"}

start_time=`date +%s`

python model_fit/fit_prs.py -s "$1" -m "$model"

end_time=`date +%s`

echo "Job finished with exit code $? at: `date`"
echo "Execution time: $((end_time-start_time))"
