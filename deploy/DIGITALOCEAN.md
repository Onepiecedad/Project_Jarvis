# 🌊 JARVIS DigitalOcean Deployment Guide

## 📋 Prerequisites

- DigitalOcean account ([Sign up](https://www.digitalocean.com/))
- Your API keys ready:
  - OpenAI API Key
  - Supabase credentials (already configured)

---

## 🚀 Quick Deploy (5 minutes)

### Step 1: Create a Droplet

1. Go to [DigitalOcean](https://cloud.digitalocean.com/droplets/new)
2. Choose:
   - **OS:** Ubuntu 22.04 LTS
   - **Plan:** Basic, 4GB RAM / 2 vCPUs ($24/month) - *Recommended*
   - **Region:** Frankfurt (fra1) or Amsterdam (ams3) for EU
   - **Authentication:** SSH key (recommended) or password
3. Click **Create Droplet**

### Step 2: Connect to Your Server

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Run the Install Script

```bash
curl -fsSL https://raw.githubusercontent.com/Onepiecedad/Project_Jarvis/main/deploy/setup.sh | bash
```

### Step 4: Configure API Keys

```bash
nano /opt/jarvis/.env
```

Add your keys:

```env
MEMORY_BACKEND=supabase
SUPABASE_URL=https://bqtcedtstisonblzrfsn.supabase.co
SUPABASE_ANON_KEY=eyJ...your_key
SUPABASE_SERVICE_ROLE_KEY=eyJ...your_key
OPENAI_API_KEY=sk-...your_key
```

Press `Ctrl+O` to save, `Ctrl+X` to exit.

### Step 5: Restart JARVIS

```bash
cd /opt/jarvis && docker-compose restart
```

### Step 6: Access JARVIS

Open in your browser:

```
http://YOUR_DROPLET_IP
```

---

## 🔒 Set Up HTTPS (Recommended)

If you have a domain:

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d jarvis.yourdomain.com

# Auto-renew is enabled by default
```

---

## 🔧 Management Commands

| Action | Command |
|--------|---------|
| View logs | `docker logs -f jarvis` |
| Restart | `cd /opt/jarvis && docker-compose restart` |
| Stop | `cd /opt/jarvis && docker-compose down` |
| Start | `cd /opt/jarvis && docker-compose up -d` |
| Update | `cd /opt/jarvis && docker-compose pull && docker-compose up -d` |

---

## 💰 Cost Estimate

| Resource | Cost |
|----------|------|
| Droplet (4GB) | ~$24/month |
| Domain (optional) | ~$12/year |
| **Total** | **~$24-26/month** |

---

## 🆘 Troubleshooting

### JARVIS won't start

```bash
docker logs jarvis
```

### Can't access via browser

```bash
# Check if JARVIS is running
docker ps

# Check Nginx
systemctl status nginx

# Check firewall
ufw status
ufw allow 80
ufw allow 443
```

### Reset everything

```bash
cd /opt/jarvis
docker-compose down
docker-compose pull
docker-compose up -d
```

---

## 📱 Mobile Access

Once deployed, you can access JARVIS from any device:

- **Phone browser:** `http://YOUR_IP` or `https://jarvis.yourdomain.com`
- **Tablet:** Same URL
- **Other computers:** Same URL

The cloud-based Supabase memory means all your conversations and memories are synced across devices!
