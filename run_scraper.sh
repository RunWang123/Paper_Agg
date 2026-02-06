#!/bin/bash
#SBATCH --job-name paper_scrape
#SBATCH --nodes 1
#SBATCH --cpus-per-task 30
#SBATCH --mem 64gb
#SBATCH --time 10:00:00
#SBATCH --output scraper_%j.log

# Load conda/mamba if needed (Palmetto specific)
module load anaconda3/2023.09 || true
source activate h100_env || conda activate h100_env

# Set database URL
export DATABASE_URL='postgresql://paper_user:SecurePass123@3.80.49.152:5432/paper_agg'

# Go to repo directory
cd ~/Paper_Agg

# Install dependencies
pip install -r requirements.txt

# Run the scraper with abstracts + embeddings
echo "Starting scraper at $(date)"
srun python -c "from scanner import Scanner; Scanner().run()"
echo "Finished at $(date)"
