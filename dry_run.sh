#!/bin/bash
#SBATCH --job-name dry_run_check
#SBATCH --nodes 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 8gb
#SBATCH --time 00:10:00
#SBATCH --output dry_run_%j.log

# Load conda/mamba if needed (Palmetto specific)
module load anaconda3/2023.09 || true
source activate h100_env || conda activate h100_env

# Set database URL (Oracle Cloud VM)
export DATABASE_URL='postgresql://paper_user:paper_password@150.136.114.211:5432/paper_agg'

# Go to repo directory
cd ~/Paper_Agg

# Run the dry run script
echo "Starting Dry Run at $(date)"
python scripts/dry_run.py
echo "Finished at $(date)"
