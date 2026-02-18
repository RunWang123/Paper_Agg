#!/bin/bash
# Add CORS to Oracle backend
cd ~/Paper_Agg

# Kill existing uvicorn
pkill -f 'uvicorn main:app' 2>/dev/null
sleep 1

# Check if CORS is already present
if grep -q 'CORSMiddleware' main.py; then
    echo "CORS already present"
else
    # Use Python to modify the file safely
    python3 << 'PYEOF'
with open('main.py', 'r') as f:
    content = f.read()

cors_code = """from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Paper Aggregator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

content = content.replace('app = FastAPI(title="Paper Aggregator")', cors_code)
with open('main.py', 'w') as f:
    f.write(content)
print("CORS added!")
PYEOF
fi

# Restart uvicorn
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
sleep 3
echo "Uvicorn restarted!"
curl -s http://localhost:8000/api/stats
