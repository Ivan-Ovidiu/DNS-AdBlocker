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
## Troubleshooting
### Port 53 Not Available

1. If you get an error that port 53 is already in use:
```
#Check what's using port 53
$ sudo netstat -tulpn | grep :53
```

2. Stop the conflicting service (usually systemd-resolved)
```
$ sudo systemctl stop systemd-resolved
```

3. Try starting again
```
$ docker-compose up
```

# Access the Dashboard
Once running, open your web browser and go to:
http://localhost:5000

## Main page with statistics
![image](https://github.com/user-attachments/assets/a78c3f46-4388-4301-aabd-2991ad2ffd4e)

## Logs, api endpoint: /logs
![image](https://github.com/user-attachments/assets/6d5fe3ae-bdad-42ce-96c3-f78ef2ee89ed)


