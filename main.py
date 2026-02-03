from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import SessionLocal, Paper, init_db
from scanner import Scanner
from starlette.requests import Request
from typing import Optional, List
from fastapi import Query

app = FastAPI(title="Paper Aggregator")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup
@app.on_event("startup")
def on_startup():
    init_db()
    # Configure logging to write to file
    import logging
    file_handler = logging.FileHandler("scraper.log", mode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Get the root logger or scanner logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    
    # Explicitly add to scanner and scrapers loggers to ensure capture
    logging.getLogger("scanner").addHandler(file_handler)
    logging.getLogger("scrapers").addHandler(file_handler)
    logging.getLogger("uvicorn").addHandler(file_handler) # Optional: capture server logs too

@app.get("/api/logs")
async def get_logs():
    """Returns the last 100 lines of the scraper log."""
    try:
        with open("scraper.log", "r") as f:
            lines = f.readlines()
            return {"logs": lines[-100:]} # Return last 100 lines
    except FileNotFoundError:
        return {"logs": ["Log file not found."]}

@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request, 
    db: Session = Depends(get_db), 
    q: Optional[str] = None,
    min_year: Optional[str] = None, # changed to str to handle empty string form submission
    max_year: Optional[str] = None,
    conferences: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=500)
):
    query = db.query(Paper).order_by(Paper.id.desc())
    
    # Text Search
    if q:
        search = f"%{q}%"
        query = query.filter(
            (Paper.title.ilike(search)) | 
            (Paper.authors.ilike(search)) | 
            (Paper.conference.ilike(search))
        )
    
    # Year Filter
    if min_year and min_year.strip():
        try:
            query = query.filter(Paper.year >= int(min_year))
        except ValueError:
            pass # Ignore invalid int
            
    if max_year and max_year.strip():
        try:
            query = query.filter(Paper.year <= int(max_year))
        except ValueError:
            pass # Ignore invalid int
        
    # Conference Filter
    if conferences:
        # conferences comes as a list e.g. ["CVPR 2025", "NDSS 2025"]
        query = query.filter(Paper.conference.in_(conferences))
    
    # Get total filtered count
    total_count = query.count()
    
    # Pagination
    total_pages = (total_count + limit - 1) // limit
    offset = (page - 1) * limit
    
    # Apply limit for display
    papers = query.offset(offset).limit(limit).all()
    
    # Get available conferences and years for the filter UI
    # We can cache this or query distinct values
    all_confs = db.query(Paper.conference).distinct().all()
    all_confs = [c[0] for c in all_confs if c[0]]
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "papers": papers, 
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "query": q,
        "all_confs": sorted(all_confs),
        "selected_confs": conferences or [],
        "min_year": min_year,
        "max_year": max_year
    })

@app.post("/api/refresh")
async def refresh_data(background_tasks: BackgroundTasks, conf: Optional[str] = Query(None)):
    """
    Trigger a scraper update.
    conf: Optional comma-separated list of conferences to update (e.g. "CVPR,ICCV").
          If None, updates all.
    """
    scanner = Scanner()
    target_confs = None
    if conf:
        target_confs = [c.strip() for c in conf.split(",") if c.strip()]
        
    background_tasks.add_task(scanner.run, target_confs=target_confs)
    msg = f"Update started for {target_confs}" if target_confs else "Update started for all conferences"
    return {"message": msg}

@app.get("/api/papers")
def get_papers_api(db: Session = Depends(get_db)):
    return db.query(Paper).limit(500).all()
