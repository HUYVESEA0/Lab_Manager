#!/bin/bash
# Azure App Service startup script for Lab Manager

echo "Starting Lab Manager on Azure App Service..."

# Ensure we're in the right directory
cd /home/site/wwwroot

# Install any missing dependencies
pip install -r requirements.txt

# Run database migrations if needed
python -c "
try:
    from flask_migrate import upgrade
    from app import create_app
    app, _ = create_app()
    with app.app_context():
        upgrade()
    print('Database migrations completed')
except Exception as e:
    print(f'Migration warning: {e}')
"

# Start the application
echo "Starting Lab Manager with run_azure.py..."
python run_azure.py
