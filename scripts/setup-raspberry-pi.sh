#!/bin/bash

# Exit on error
set -e

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    gcc \
    python3-dev \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev \
    libwebp6 \
    libjasper1 \
    libilmbase23 \
    libopenexr23 \
    libgstreamer1.0-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5 \
    libqtgui4 \
    libqt4-test \
    libopencv-dev

echo "Setting up PostgreSQL..."
sudo -u postgres createuser pi || echo "User 'pi' might already exist"
sudo -u postgres createdb garden_db || echo "Database 'garden_db' might already exist"
sudo -u postgres psql -c "ALTER USER pi WITH PASSWORD 'garden_password';" || echo "Password might already be set"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE garden_db TO pi;" || echo "Privileges might already be granted"

echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

echo "Creating environment file..."
if [ ! -f .env ]; then
    echo "DATABASE_URL=postgresql://pi:garden_password@localhost:5432/garden_db" > .env
    echo "Created .env file"
else
    echo ".env file already exists"
fi

echo "Setting up systemd service..."
sudo cp scripts/garden-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable garden-app
sudo systemctl start garden-app

echo "Installation complete!"
echo "The garden app should now be running at http://localhost:8000"
echo "View logs with: sudo journalctl -u garden-app -f"