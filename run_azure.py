#!/usr/bin/env python3
"""
Azure App Service runner for Lab Manager
Simple configuration for Azure deployment
"""
import os
import sys
from dotenv import load_dotenv

def setup_azure_environment():
    """Setup environment for Azure App Service"""
    # Load Azure environment variables
    if os.path.exists('.env.azure'):
        load_dotenv('.env.azure')
        print("🌐 Loading Azure App Service configuration...")
    else:
        load_dotenv('.env')
        print("📁 Loading default environment...")
    
    # Set Azure App Service specific settings
    port = int(os.environ.get('WEBSITES_PORT', 8000))
    os.environ['INSTANCE_PORT'] = str(port)
    
    # Ensure production settings
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    
    print(f"🚀 Azure App Service Configuration:")
    print(f"  Port: {port}")
    print(f"  Site: {os.environ.get('WEBSITE_SITE_NAME', 'lab-manager')}")
    print(f"  Environment: Production")

def main():
    """Main Azure startup function"""
    setup_azure_environment()
    
    # Import and create app
    from app import create_app
    
    app, socketio = create_app()
    
    # Production configuration
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Get Azure App Service configuration
    host = "0.0.0.0"  # Azure requires 0.0.0.0
    port = int(os.environ.get('WEBSITES_PORT', 8000))
    
    print(f"🌐 Starting Lab Manager on Azure App Service")
    print(f"📍 Host: {host}:{port}")
    
    try:
        # Run with SocketIO
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        print(f"❌ Error starting Azure App Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
