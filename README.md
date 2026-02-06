# Paper Aggregator

🌐 **[Live Demo](https://paper-aggregator.onrender.com/)**

A modern, web-based tool for aggregating and tracking accepted papers from major AI, Machine Learning, and Computer Security conferences (CVPR, NeurIPS, ICLR, ICML, ICCV, ECCV, USENIX Security, IEEE S&P, ACM CCS, NDSS).
## Next Step
- **Vectorized Database**: We plan to scrape the abstracts of papers and vectorize them. So you can do vectorized matching, not just a simple keyword search.
- **More Conferences**: We plan to include more conferences: the next step is to include top system conferences, for example, MobiSys...
## Features

- **Multi-Conference Support**: Scrapers for over 10 major conferences covering 2022-2026.
- **Selective Scrape**: Choose specific conferences to update directly from the UI.
- **Real-time Logs**: Monitor scraping progress with a built-in log console.
- **Paper Tagging**: Automatically identifies and tags "Short Papers" (e.g., posters/demos) based on page counts.
- **Modern UI**: Dark-themed, responsive interface with robust filtering by keyword, year, and conference.

## Prerequisites

- **Python 3.9+**
- **Conda** (recommended)

## Installation & Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/RunWang123/Paper_Agg.git
cd Paper_Agg
```

### 2. Set Up Environment
Using Conda:
```bash
conda create -n paper_agg python=3.9
conda activate paper_agg
pip install -r requirements.txt
```

### 3. Initialize & Run
The project includes a `run.sh` script that handles environment activation, database initialization, and starting the FastAPI server.

```bash
chmod +x run.sh
./run.sh
```

**Note**: On the first run, the system will initialize the database and perform an initial scan of all configured conferences. Depending on your network speed and the number of conferences, this may take several minutes. You can monitor the progress in the terminal.

Alternatively, run the server manually:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the UI
Open your browser and navigate to:
`http://localhost:8000`

## Configuration

### Adding/Modifying Conferences
Conference URLs and scraper types are managed in `config/conferences.json`. You can update conference sites or add new years there.

### Project Structure
- `scrapers/`: Individual logic for each conference/site structure.
- `database/`: SQLite database and SQLAlchemy models.
- `templates/`: Jinja2 HTML templates.
- `static/`: CSS and frontend assets.
- `main.py`: FastAPI endpoints and application logic.
- `scanner.py`: Core logic for running scrapers and updating the database.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
