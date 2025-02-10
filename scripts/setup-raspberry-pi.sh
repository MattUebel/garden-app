#!/bin/bash

# Exit on error
set -e

echo "Installing Docker and required dependencies..."
sudo apt update
sudo apt install -y \
    docker.io \
    docker-compose \
    cron

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group to avoid using sudo
sudo usermod -aG docker $USER

echo "Creating persistent directories..."
# Create directories for persistent data
sudo mkdir -p /var/lib/garden-app/db-data
sudo mkdir -p /var/lib/garden-app/backups

# Set proper ownership
sudo chown -R $USER:$USER /var/lib/garden-app

echo "Setting up database backup script..."
cat << 'EOF' | sudo tee /usr/local/bin/backup-garden-db.sh
#!/bin/bash
BACKUP_DIR="/var/lib/garden-app/backups"
CONTAINER_NAME="garden-app-db-1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/garden_db_$TIMESTAMP.sql"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Database container ${CONTAINER_NAME} is not running. Skipping backup."
    exit 1
fi

# Create backup
docker exec $CONTAINER_NAME pg_dump -U postgres garden_db > $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "garden_db_*.sql" -type f -mtime +7 -delete
EOF

# Make backup script executable
sudo chmod +x /usr/local/bin/backup-garden-db.sh

# Add backup cron job - runs daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-garden-db.sh") | crontab -

echo "Setting up systemd service..."
cat << 'EOF' | sudo tee /etc/systemd/system/garden-app.service
[Unit]
Description=Garden App Docker Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/docker-compose -f /home/pi/garden-app/compose.yaml up
ExecStop=/usr/bin/docker-compose -f /home/pi/garden-app/compose.yaml down
WorkingDirectory=/home/pi/garden-app
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable garden-app
sudo systemctl start garden-app

echo "Installation complete!"
echo "The garden app should now be running via Docker"
echo "View logs with: sudo journalctl -u garden-app -f"
echo "Manual backup can be triggered with: sudo /usr/local/bin/backup-garden-db.sh"
echo "Database backups are stored in /var/lib/garden-app/backups"