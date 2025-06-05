DNS Ad & Tracker Blocker with Docker
A Pi-hole inspired DNS server implementation that blocks advertisements and tracking domains at the network level. Built with Python and containerized using Docker Compose for easy deployment and configuration.
Features

Custom DNS Server: Intercepts DNS queries and blocks known ad/tracking domains
Real-time Blocking: Returns 0.0.0.0 for blocked domains, effectively blocking ads and trackers
Multiple Blocklists: Integrates curated lists from GitHub and custom domains
Company Classification: Categorizes blocked domains by company (Google, Facebook, Microsoft, etc.)
Web Dashboard: Flask-based web interface for statistics and monitoring
Docker Support: Easy deployment with Docker Compose
Comprehensive Logging: Tracks all DNS queries and blocked requests
Statistics & Analytics: Detailed insights into blocking patterns and company tracking

Architecture
Client DNS Request → Custom DNS Server → Check Blocklist → 
├─ Blocked: Return 0.0.0.0
└─ Allowed: Forward to Upstream DNS (8.8.8.8)
Prerequisites
System Requirements

Linux/macOS/Windows with administrative privileges
Docker and Docker Compose
Python 3.8+ (if running without Docker)
Minimum 2GB RAM and 1GB disk space

Installation of Dependencies
Ubuntu/Debian
bash# Update package list
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
CentOS/RHEL/Fedora
bash# Install Docker
sudo dnf install -y docker docker-compose
# or for older versions: sudo yum install -y docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
macOS
bash# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or using Homebrew:
brew install --cask docker
brew install docker-compose
Windows

Install Docker Desktop from https://www.docker.com/products/docker-desktop
Enable WSL2 integration
Install Windows Subsystem for Linux (WSL2)

Installation & Setup
1. Clone the Repository
bashgit clone <repository-url>
cd dns-ad-blocker
2. Project Structure
dns-ad-blocker/
├── dns_server.py              # Main DNS server implementation
├── web_dashboard.py           # Flask web interface
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Container build instructions
├── requirements.txt           # Python dependencies
├── dns_blocker.log           # DNS server logs
├── dns_stats.json            # Statistics storage
└── README.md                 # This file
3. Start with Docker Compose
bash# Build and start the services
sudo docker-compose up -d

# View logs
sudo docker-compose logs -f

# Stop services
sudo docker-compose down
