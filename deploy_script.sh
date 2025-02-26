# Navigate to the application directory
cd /to-do-web-app

# Stop the current Gunicorn process if it's running
# Replace 'my-flask-app' with the name of your Gunicorn process
pkill -f gunicorn || true

# Pull the latest code from the repository
git pull origin main

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application using Gunicorn with the configuration file
gunicorn -c gunicorn.conf.py flask_app:app &