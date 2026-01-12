#!/bin/bash
# =============================================================================
# JARVIS DigitalOcean Deploy Script
# =============================================================================
# This script sets up JARVIS (Agent Zero) on a fresh Ubuntu 22.04 Droplet
#
# Usage:
#   1. Create a DigitalOcean Droplet (Ubuntu 22.04, 4GB RAM minimum)
#   2. SSH into the droplet: ssh root@YOUR_IP
#   3. Run: curl -fsSL https://raw.githubusercontent.com/Onepiecedad/Project_Jarvis/main/deploy/setup.sh | bash
#   Or copy this script and run it manually
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         🤖 JARVIS - DigitalOcean Setup Script 🤖              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# -----------------------------------------------------------------------------
# Step 1: Update system
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
apt-get update -qq
apt-get upgrade -y -qq
echo -e "${GREEN}✓ System updated${NC}"

# -----------------------------------------------------------------------------
# Step 2: Install Docker
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/7] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# -----------------------------------------------------------------------------
# Step 3: Install Docker Compose
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/7] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y -qq docker-compose-plugin
    # Also install standalone docker-compose for compatibility
    curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# -----------------------------------------------------------------------------
# Step 4: Create JARVIS directory and docker-compose.yml
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/7] Creating JARVIS configuration...${NC}"
mkdir -p /opt/jarvis
cd /opt/jarvis

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  jarvis:
    container_name: jarvis
    image: agent0ai/agent-zero:latest
    restart: unless-stopped
    volumes:
      - ./data:/a0
    ports:
      - "50080:80"
    environment:
      - MEMORY_BACKEND=${MEMORY_BACKEND:-local}
      - SUPABASE_URL=${SUPABASE_URL:-}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
EOF

echo -e "${GREEN}✓ Configuration created${NC}"

# -----------------------------------------------------------------------------
# Step 5: Create .env file (user will need to fill in secrets)
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/7] Creating environment file...${NC}"

if [ ! -f .env ]; then
    cat > .env << 'EOF'
# =============================================================================
# JARVIS Environment Configuration
# =============================================================================
# Fill in your API keys below

# Memory Backend: 'supabase' for cloud memory, 'local' for local storage
MEMORY_BACKEND=supabase

# Supabase Configuration (get from https://supabase.com/dashboard)
SUPABASE_URL=https://bqtcedtstisonblzrfsn.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_key_here
EOF
    echo -e "${YELLOW}⚠ Created .env file - you need to add your API keys!${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# -----------------------------------------------------------------------------
# Step 6: Install Nginx for reverse proxy (optional but recommended)
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[6/7] Installing Nginx...${NC}"
apt-get install -y -qq nginx

# Create Nginx config for JARVIS
cat > /etc/nginx/sites-available/jarvis << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain if you have one

    location / {
        proxy_pass http://localhost:50080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/jarvis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo -e "${GREEN}✓ Nginx installed and configured${NC}"

# -----------------------------------------------------------------------------
# Step 7: Pull and start JARVIS
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[7/7] Starting JARVIS...${NC}"
docker-compose pull
docker-compose up -d

echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         🎉 JARVIS Installation Complete! 🎉                   ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""
echo "1. Edit the .env file with your API keys:"
echo -e "   ${YELLOW}nano /opt/jarvis/.env${NC}"
echo ""
echo "2. Restart JARVIS after adding keys:"
echo -e "   ${YELLOW}cd /opt/jarvis && docker-compose restart${NC}"
echo ""
echo "3. Access JARVIS at:"
echo -e "   ${GREEN}http://$(curl -s ifconfig.me)${NC}"
echo ""
echo "4. (Optional) Set up SSL with your domain:"
echo -e "   ${YELLOW}apt install certbot python3-certbot-nginx${NC}"
echo -e "   ${YELLOW}certbot --nginx -d your-domain.com${NC}"
echo ""
echo -e "${BLUE}📂 Files Location:${NC}"
echo "   Config:  /opt/jarvis/docker-compose.yml"
echo "   Env:     /opt/jarvis/.env"
echo "   Data:    /opt/jarvis/data/"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "   View logs:    docker logs -f jarvis"
echo "   Restart:      cd /opt/jarvis && docker-compose restart"
echo "   Stop:         cd /opt/jarvis && docker-compose down"
echo "   Update:       cd /opt/jarvis && docker-compose pull && docker-compose up -d"
echo ""
