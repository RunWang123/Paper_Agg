#!/usr/bin/env python3
"""
Batch vectorization script for existing papers.
Run this once to generate embeddings for all papers in the database.

Usage:
    python vectorize_papers.py [--batch-size 32] [--limit 1000]
"""

import argparse
from database import SessionLocal, Paper, IS_POSTGRES

if not IS_POSTGRES:
    print("Error: This script requires PostgreSQL with pgvector.")
    print("Set DATABASE_URL environment variable to your PostgreSQL connection string.")
    exit(1)

from embeddings import generate_embeddings_batch, create_paper_embedding_text
from sqlalchemy import text


def vectorize_papers(batch_size: int = 32, limit: int = None):
    """Generate embeddings for all papers that don't have them yet."""
    db = SessionLocal()
    
    try:
        # Count papers without embeddings
        total_query = text("SELECT COUNT(*) FROM papers WHERE embedding IS NULL")
        total_without = db.execute(total_query).scalar()
        
        print(f"Found {total_without} papers without embeddings")
        
        if total_without == 0:
            print("All papers already have embeddings!")
            return
        
        # Process in batches
        processed = 0
        target = min(limit, total_without) if limit else total_without
        
        while processed < target:
            # Fetch papers without embeddings
            fetch_limit = min(batch_size, target - processed)
            papers = db.query(Paper).filter(
                Paper.embedding == None  # noqa: E711
            ).limit(fetch_limit).all()
            
            if not papers:
                break
            
            # Create texts for embedding
            texts = []
            for paper in papers:
                text_to_embed = create_paper_embedding_text(
                    title=paper.title,
                    authors=paper.authors or "",
                    abstract=paper.abstract or ""
                )
                texts.append(text_to_embed)
            
            # Generate embeddings
            print(f"Generating embeddings for batch {processed // batch_size + 1} ({len(papers)} papers)...")
            embeddings = generate_embeddings_batch(texts, batch_size=batch_size)
            
            # Update papers with embeddings
            for paper, embedding in zip(papers, embeddings):
                update_sql = text(
                    "UPDATE papers SET embedding = :embedding WHERE id = :id"
                )
                db.execute(update_sql, {"embedding": str(embedding), "id": paper.id})
            
            db.commit()
            processed += len(papers)
            print(f"Progress: {processed}/{target} ({processed * 100 // target}%)")
        
        print(f"\nDone! Vectorized {processed} papers.")
        
        # Show final stats
        embedded_count = db.execute(
            text("SELECT COUNT(*) FROM papers WHERE embedding IS NOT NULL")
        ).scalar()
        total_count = db.query(Paper).count()
        print(f"Total papers with embeddings: {embedded_count}/{total_count} ({embedded_count * 100 // total_count}%)")
        
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings for papers")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for embedding generation")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to process")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Paper Vectorization Script")
    print("=" * 50)
    print(f"Batch size: {args.batch_size}")
    print(f"Limit: {args.limit or 'None (all papers)'}")
    print()
    
    vectorize_papers(batch_size=args.batch_size, limit=args.limit)
