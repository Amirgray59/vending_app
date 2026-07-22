#!/bin/sh
echo "Running the migrations ..."
alembic upgrade head 
echo "Migrations completed! "

echo "Runnin the Server..." 
uvicorn app.main:app --host 0.0.0.0 --port 8000 