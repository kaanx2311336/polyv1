#!/bin/bash
# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
# Seed categories if needed
python seed_categories.py
# Create admin if needed
python create_admin.py

# Run Gunicorn
exec gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
