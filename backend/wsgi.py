#!/usr/bin/python3.10

import sys
import os

# Add your project directory to Python path
path = '/home/davidpascual13/portfolio_optimizer'
if path not in sys.path:
    sys.path.insert(0, path)

# Add backend directory to path
backend_path = '/home/davidpascual13/portfolio_optimizer/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set up environment variables
os.environ['FLASK_ENV'] = 'production'

# Import your Flask app
from app import app as application

if __name__ == "__main__":
    application.run()
