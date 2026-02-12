from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, Paper, init_db, IS_POSTGRES
from scanner import Scanner
from starlette.requests import Request
from typing import Optional, List
from fastapi import Query
import json

# Import embedding functions only if PostgreSQL is available
if IS_POSTGRES:
    from embeddings import generate_embedding, create_paper_embedding_text


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Paper Aggregator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/search")
async def search_papers(
    db: Session = Depends(get_db), 
    q: Optional[str] = None,
    min_year: Optional[str] = None,
    max_year: Optional[str] = None,
    conferences: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Search papers with filters. Returns JSON for the Next.js frontend.
    """
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
            pass
            
    if max_year and max_year.strip():
        try:
            query = query.filter(Paper.year <= int(max_year))
        except ValueError:
            pass
        
    # Conference Filter
    if conferences:
        query = query.filter(Paper.conference.in_(conferences))
    
    # Get total count
    total_count = query.count()
    
    # Pagination
    total_pages = (total_count + limit - 1) // limit
    offset = (page - 1) * limit
    
    # Fetch papers
    papers = query.offset(offset).limit(limit).all()
    
    # Serialize papers to JSON-safe dicts (exclude embedding vector)
    papers_json = []
    for p in papers:
        papers_json.append({
            "id": p.id,
            "title": p.title,
            "authors": p.authors,
            "conference": p.conference,
            "year": p.year,
            "url": p.url,
            "pdf_url": p.pdf_url,
            "tags": p.tags,
        })
    
    return {
        "papers": papers_json,
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

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
    # Keep existing HTML endpoint for fallback/comparison
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
    
    # Load all configured conferences from conferences.json for the update modal
    configured_confs = []
    try:
        with open("config/conferences.json", "r") as f:
            conf_config = json.load(f)
            configured_confs = sorted(conf_config.keys())
    except Exception:
        pass  # If loading fails, just use empty list
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "papers": papers, 
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "query": q,
        "all_confs": sorted(all_confs),
        "configured_confs": configured_confs,
        "selected_confs": conferences or [],
        "min_year": min_year,
        "max_year": max_year
    })

@app.post("/api/refresh")
async def refresh_data(
    background_tasks: BackgroundTasks, 
    conf: Optional[str] = Query(None),
    fetch_abstracts: bool = Query(True, description="Fetch abstracts from paper detail pages (default: True for semantic search)")
):
    """
    Trigger a scraper update.
    conf: Optional comma-separated list of conferences to update (e.g. "CVPR,ICCV").
          If None, updates all.
    fetch_abstracts: Fetches abstracts for semantic search (default True). Set to False for faster title-only scraping.
    """
    scanner = Scanner()
    target_confs = None
    if conf:
        target_confs = [c.strip() for c in conf.split(",") if c.strip()]
        
    background_tasks.add_task(scanner.run, target_confs=target_confs, fetch_abstracts=fetch_abstracts)
    msg = f"Update started for {target_confs or 'all conferences'}"
    if not fetch_abstracts:
        msg += " (fast mode - no abstracts)"
    else:
        msg += " (with abstracts for semantic search)"
    return {"message": msg}

@app.get("/api/papers")
def get_papers_api(db: Session = Depends(get_db)):
    return db.query(Paper).limit(500).all()


@app.get("/api/semantic-search")
async def semantic_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    conferences: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Semantic search for papers using vector similarity.
    Returns papers ranked by semantic similarity to the query.
    """
    if not IS_POSTGRES:
        raise HTTPException(
            status_code=501,
            detail="Semantic search requires PostgreSQL with pgvector"
        )
    
    # Generate embedding for the query
    query_embedding = generate_embedding(q)
    
    # Build the SQL query with filters
    filters = []
    params = {"limit": limit}
    
    if min_year:
        filters.append("year >= :min_year")
        params["min_year"] = min_year
    
    if max_year:
        filters.append("year <= :max_year")
        params["max_year"] = max_year
    
    if conferences:
        filters.append("conference = ANY(:conferences)")
        params["conferences"] = conferences
    
    where_clause = ""
    if filters:
        where_clause = "WHERE embedding IS NOT NULL AND " + " AND ".join(filters)
    else:
        where_clause = "WHERE embedding IS NOT NULL"
    
    # Convert embedding to string for SQL injection (safe - generated internally, not user input)
    embedding_str = str(query_embedding)
    
    # Use pgvector's <=> operator for cosine distance
    sql = text(f"""
        SELECT 
            id, title, authors, conference, year, url, pdf_url, tags,
            1 - (embedding <=> '{embedding_str}'::vector) as similarity
        FROM papers
        {where_clause}
        ORDER BY embedding <=> '{embedding_str}'::vector
        LIMIT :limit
    """)
    
    result = db.execute(sql, params)
    papers = []
    for row in result:
        papers.append({
            "id": row.id,
            "title": row.title,
            "authors": row.authors,
            "conference": row.conference,
            "year": row.year,
            "url": row.url,
            "pdf_url": row.pdf_url,
            "tags": row.tags,
            "similarity": round(row.similarity * 100, 1)  # Convert to percentage
        })
    
    return {
        "query": q,
        "count": len(papers),
        "papers": papers
    }


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get database statistics including embedding coverage."""
    total_papers = db.query(Paper).count()
    
    stats = {
        "total_papers": total_papers,
        "is_postgres": IS_POSTGRES,
    }
    
    if IS_POSTGRES:
        # Count papers with embeddings
        embedded_count = db.execute(
            text("SELECT COUNT(*) FROM papers WHERE embedding IS NOT NULL")
        ).scalar()
        stats["papers_with_embeddings"] = embedded_count
        stats["embedding_coverage"] = round(embedded_count / total_papers * 100, 1) if total_papers > 0 else 0
    
    return stats
