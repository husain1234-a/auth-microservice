#!/bin/bash

# Order Service Startup Script

echo "Starting Order Service..."

# Initialize database tables
echo "Initializing database tables..."
python init_db.py

# Start the service
echo "Starting the Order Service..."
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload