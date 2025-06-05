# DNS AdBlocker and tracker with Docker orchestration

A Pi-hole inspired DNS server implementation that blocks advertisements and tracking domains at the network level. Built with Python and containerized using Docker Compose for easy deployment and configuration.

## Features

- **Custom DNS Server** - Intercepts DNS queries and blocks known ad/tracking domains
- **Real-time Blocking** - Returns `0.0.0.0` for blocked domains, effectively blocking ads and trackers
- **Multiple Blocklists** - Integrates curated lists from GitHub and custom domains
- **Company Classification** - Categorizes blocked domains by company (Google, Facebook, Microsoft, etc.)
- **Web Dashboard** - Flask-based web interface for statistics and monitoring
- **Docker Support** - Easy deployment with Docker Compose
- **Comprehensive Logging** - Tracks all DNS queries and blocked requests
- **Statistics & Analytics** - Detailed insights into blocking patterns and company tracking

## Installation/Requierments
1. Install Docker
```
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
```
2. Clone and Start
```
bashgit clone <repository-url>
cd dns-ad-blocker
```
3. Run the Application
```
#Start the DNS blocker
docker-compose up 
#Stop the DNS blocker
docker-compose down
#Check status
docker-compose ps
```

# Access the Dashboard
Once running, open your web browser and go to:
http://localhost:5000
