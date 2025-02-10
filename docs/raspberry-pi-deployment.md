# Raspberry Pi Deployment Guide

This guide explains how to deploy the Garden App on a Raspberry Pi using our automated setup script.

## Quick Start

1. Clone the repository:
```bash
git clone git@github.com:MattUebel/garden-app.git
cd garden-app
```

2. Run the setup script:
```bash
./scripts/setup-raspberry-pi.sh
```

That's it! The script handles everything else automatically.

## What the Setup Script Does

The setup script automates the entire deployment process:

1. Installs required dependencies:
   - Docker and Docker Compose
   - Cron for scheduled backups

2. Sets up persistent storage:
   - Creates `/var/lib/garden-app/db-data` for database files
   - Creates `/var/lib/garden-app/backups` for database backups

3. Configures automated backups:
   - Creates a backup script at `/usr/local/bin/backup-garden-db.sh`
   - Sets up daily backups at 2 AM
   - Maintains a 7-day backup history

4. Installs and starts the system service:
   - Creates a systemd service for automatic startup
   - Enables and starts the service

## Monitoring Your Deployment

After installation, you can:

1. Check the service status:
```bash
sudo systemctl status garden-app
```

2. View application logs:
```bash
sudo journalctl -u garden-app -f
```

3. Check running containers:
```bash
docker ps
```

## Database Backups

Backups are handled automatically, but you can:

- Trigger a manual backup:
```bash
sudo /usr/local/bin/backup-garden-db.sh
```

- Find backup files in `/var/lib/garden-app/backups`
- Backups are automatically pruned after 7 days

## Troubleshooting

1. If the service fails to start:
   - Check logs: `sudo journalctl -u garden-app -f`
   - Verify Docker is running: `sudo systemctl status docker`
   - Ensure proper file permissions in `/var/lib/garden-app`

2. If database backup fails:
   - Check container is running: `docker ps`
   - Verify backup directory permissions
   - Check available disk space: `df -h`

3. For permission issues:
   - Verify your user is in the docker group: `groups`
   - If not, log out and back in after the setup script runs

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)

For additional support, please open an issue in the GitHub repository.