import sys

# Assume that we've put our Flask app in the 'eduthon_app' subdirectory
sys.path.insert(0, '/home/eduthon/eduthon_app')

from app import app as application

if __name__ == "__main__":
    application.run()