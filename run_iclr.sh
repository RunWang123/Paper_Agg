#!/bin/bash
#SBATCH --job-name iclr_scrape
#SBATCH --nodes 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 16gb
#SBATCH --time 04:00:00
#SBATCH --output iclr_%j.log

# Load conda/mamba
module load anaconda3/2023.09 || true
source activate h100_env || source /home/mbirada/.conda/envs/h100_env/bin/activate

# Set DB URL
export DATABASE_URL='postgresql://paper_user:paper_password@150.136.114.211:5432/paper_agg'

echo "Starting ICLR Scrape..."
echo "Database: $DATABASE_URL"

# Run for 2024 and 2023
python main.py --conference ICLR --year 2024
python main.py --conference ICLR --year 2023

echo "Done!"
