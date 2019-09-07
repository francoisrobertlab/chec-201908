#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --array=0-0
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=20G
#SBATCH --mail-user=christian.poitras@ircm.qc.ca
#SBATCH --mail-type=ALL

python $CHEC_PATH/Plot2do.py -i $SLURM_ARRAY_TASK_ID $@
