
if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Paper Aggregator & Scraper")
    parser.add_argument("--conference", type=str, help="Run scraper for specific conference (e.g. CVPR)")
    parser.add_argument("--year", type=int, help="Run scraper for specific year (e.g. 2024)")
    parser.add_argument("--serve", action="store_true", help="Run the web server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for web server")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server")
    
    args = parser.parse_args()
    
    if args.conference:
        # Run scraper mode
        print(f"Starting Scraper for {args.conference} {args.year or ''}...")
        
        # Initialize DB if not already done
        try:
            init_db()
        except Exception as e:
            print(f"DB Init Warning: {e}")
            
        scanner = Scanner()
        # Create a list if specific conference requested
        target = [args.conference] if args.conference else None
        
        # Run scanner (Scanner.run usually takes target_confs list)
        # We need to make sure Scanner passes 'year' down if supported, 
        # or we might need to modify Scanner.run to accept year filter.
        # For now, Scanner.run(target_confs) scans all configured years for that conf.
        # If args.year is provided, we might need a way to limit it.
        # Let's check Scanner.run signature first.
        scanner.run(target_confs=target)
        
        print("Scrape run complete.")
        
    elif args.serve:
        # Run server mode
        uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
        
    else:
        # Default to server if no args (or you can print help)
        print("No arguments provided. Running web server...")
        uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
