#!/bin/bash
#SBATCH --job-name=paper_scrape
#SBATCH --cpus-per-task=30
#SBATCH --mem=64G
#SBATCH --time=10:00:00
#SBATCH --output=scraper_%j.log

# Activate conda environment (adjust name if different)
source activate h100_env

# Set database URL
export DATABASE_URL='postgresql://paper_user:SecurePass123@3.80.49.152:5432/paper_agg'

# Go to repo directory
cd ~/Paper_Agg

# Install dependencies
pip install -r requirements.txt

# Run the scraper with abstracts + embeddings
echo "Starting scraper at $(date)"
python -c "from scanner import Scanner; Scanner().run()"
echo "Finished at $(date)"
