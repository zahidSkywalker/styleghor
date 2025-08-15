#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python backend/manage.py collectstatic --no-input

echo "Running migrations..."
python backend/manage.py migrate

echo "Build completed successfully!"