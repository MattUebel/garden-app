# Raspberry Pi Deployment Guide

This guide explains how to deploy the Garden App on a Raspberry Pi, either directly or using Docker.

## Direct Installation

### 1. System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev gcc python3-dev
```

### 2. Database Setup
```bash
sudo -u postgres createuser pi
sudo -u postgres createdb garden_db
sudo -u postgres psql
    ALTER USER pi WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE garden_db TO pi;
```

### 3. Application Setup
```bash
git clone git@github.com:MattUebel/garden-app.git
cd garden-app
python3 -m venv venv
source venv/bin/activate
pip install wheel  # Install wheel first to help with binary dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a .env file:
```bash
DATABASE_URL=postgresql://pi:your_password@localhost:5432/garden_db
```

### 5. Running as a Service
```bash
# Copy the service file
sudo cp scripts/garden-app.service /etc/systemd/system/
sudo systemctl daemon-reload

# Start and enable the service
sudo systemctl start garden-app
sudo systemctl enable garden-app
```

You can view the logs using:
```bash
sudo journalctl -u garden-app -f
```

## Docker Deployment

### 1. Install Docker
```bash
# Use our setup script
curl -fsSL https://raw.githubusercontent.com/MattUebel/garden-app/main/scripts/setup-raspberry-pi.sh | bash
```

This script will:
- Install Docker and Docker Compose
- Set up automatic database backups
- Create required directories
- Configure the system service

### 2. Persistent Data
The setup script creates these directories:
- `/var/lib/garden-app/db-data`: Database storage
- `/var/lib/garden-app/backups`: Daily database backups

### 3. Database Backups
- Automatic daily backups at 2 AM
- Keeps last 7 days of backups
- Manual backup: `sudo /usr/local/bin/backup-garden-db.sh`

### 4. Monitoring
- Check service status: `sudo systemctl status garden-app`
- View logs: `sudo journalctl -u garden-app -f`
- Check Docker containers: `docker ps`

## Performance Considerations

> Note: For running on Raspberry Pi, we recommend using the direct installation method rather than Docker due to better ARM processor support and reduced overhead.

## Troubleshooting

1. If the service fails to start:
   - Check logs: `sudo journalctl -u garden-app -f`
   - Verify database connection
   - Ensure proper file permissions

2. If database backup fails:
   - Check container is running: `docker ps`
   - Verify backup directory permissions
   - Check available disk space