#!/bin/bash
#SBATCH --job-name backfill_arxiv
#SBATCH --nodes 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 16gb
#SBATCH --time 02:00:00
#SBATCH --output backfill_%j.log

# Load conda/mamba
module load anaconda3/2023.09 || true
source activate h100_env || conda activate h100_env

# Set database URL (Oracle Cloud VM)
export DATABASE_URL='postgresql://paper_user:paper_password@150.136.114.211:5432/paper_agg'

# Start backfill
echo "Starting ArXiv Backfill at $(date)"
python scripts/backfill_arxiv.py
echo "Finished at $(date)"
