from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Paper(Base):
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    
    # Metadata
    conference = Column(String) # e.g. "CVPR 2025"
    year = Column(Integer)
    
    # URLs
    url = Column(String) # Link to paper page
    pdf_url = Column(String, nullable=True) # Direct PDF link if available
    
    # Source tracking
    source_url = Column(String) # Where we scrapped this from
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Tags
    tags = Column(String, nullable=True) # e.g. "Short Paper"

    # Avoid duplicate papers for same conference and year
    __table_args__ = (UniqueConstraint('title', 'conference', 'year', name='_title_conf_year_uc'),)

# Setup DB
DATABASE_URL = "sqlite:///./database/papers.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
