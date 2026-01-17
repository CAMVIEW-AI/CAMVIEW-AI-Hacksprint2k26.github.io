# Deployment Guide - CAMVIEW.AI Traffic Safety System

This guide covers multiple deployment scenarios for the traffic safety monitoring system.

---

## Deployment Options

| Deployment Type | Best For | Complexity |
|----------------|----------|------------|
| **Local Server** | Testing, small-scale monitoring | Low |
| **Cloud VM** | Production, remote access | Medium |
| **Docker Container** | Scalable, portable deployment | Medium |
| **Edge Device** | Real-time CCTV integration | High |

---

## Option 1: Local Server Deployment (Simplest)

### Prerequisites
- Windows/Linux server with Python 3.10+
- Webcam or video files
- Internet connection (for Firebase)

### Steps

1. **Clone/Copy the Project**
   ```bash
   # Copy the entire project folder to your server
   C:\CAMVIEW.AI\
   ```

2. **Install Dependencies**
   ```bash
   cd C:\CAMVIEW.AI
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # Linux
   
   pip install -r requirements.txt
   ```

3. **Configure Settings**
   - Edit `config/settings.py`
   - Set video source paths
   - Configure Firebase (optional)

4. **Run the Engine**
   ```bash
   python main.py --source "path/to/video.mp4"
   # or for webcam:
   python main.py --source 0
   ```

5. **Run the Dashboard** (separate terminal)
   ```bash
   streamlit run app.py
   ```

6. **Access Dashboard**
   - Open browser: http://localhost:8501

### Keep it Running (Windows Service)

Create a batch file `start_engine.bat`:
```batch
@echo off
cd C:\CAMVIEW.AI
call .venv\Scripts\activate
python main.py --source "your_video_source.mp4"
```

Use Task Scheduler to run on startup.

---

## Option 2: Cloud VM Deployment (AWS/Azure/GCP)

### Prerequisites
- Cloud account (AWS EC2, Azure VM, or Google Cloud Compute Engine)
- SSH access
- Domain name (optional)

### AWS EC2 Example

1. **Launch EC2 Instance**
   - Instance Type: `g4dn.xlarge` (GPU) or `t3.large` (CPU)
   - OS: Ubuntu 22.04 LTS
   - Storage: 50GB SSD
   - Security Group: Open ports 22 (SSH), 8501 (Streamlit)

2. **Connect via SSH**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install System Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3.10 python3-pip python3-venv
   sudo apt install -y libgl1-mesa-glx libglib2.0-0  # OpenCV dependencies
   ```

4. **Transfer Project Files**
   ```bash
   # From local machine:
   scp -i your-key.pem -r CAMVIEW.AI ubuntu@your-ec2-ip:~/
   ```

5. **Setup Python Environment**
   ```bash
   cd ~/CAMVIEW.AI
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Setup Firebase Credentials**
   ```bash
   # Copy your firebase_service_account.json to the server
   scp -i your-key.pem firebase_service_account.json ubuntu@your-ec2-ip:~/CAMVIEW.AI/
   ```

7. **Run as Background Service**

   Create systemd service file `/etc/systemd/system/camview-engine.service`:
   ```ini
   [Unit]
   Description=CAMVIEW.AI Traffic Safety Engine
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/CAMVIEW.AI
   ExecStart=/home/ubuntu/CAMVIEW.AI/.venv/bin/python main.py --source 0
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Create dashboard service `/etc/systemd/system/camview-dashboard.service`:
   ```ini
   [Unit]
   Description=CAMVIEW.AI Streamlit Dashboard
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/CAMVIEW.AI
   ExecStart=/home/ubuntu/CAMVIEW.AI/.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start services:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable camview-engine camview-dashboard
   sudo systemctl start camview-engine camview-dashboard
   ```

8. **Setup Nginx Reverse Proxy** (optional, for HTTPS)
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   ```

   Create `/etc/nginx/sites-available/camview`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

   Enable site and get SSL:
   ```bash
   sudo ln -s /etc/nginx/sites-available/camview /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   sudo certbot --nginx -d your-domain.com
   ```

9. **Access Dashboard**
   - HTTP: http://your-ec2-ip:8501
   - HTTPS: https://your-domain.com

---

## Option 3: Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Create Dockerfile

`Dockerfile`:
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command (can be overridden)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  engine:
    build: .
    container_name: camview-engine
    volumes:
      - ./data:/app/data
      - ./firebase_service_account.json:/app/firebase_service_account.json
      - ./videos:/app/videos  # Mount video directory
    command: python main.py --source /app/videos/input.mp4
    restart: unless-stopped

  dashboard:
    build: .
    container_name: camview-dashboard
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    depends_on:
      - engine
    restart: unless-stopped
```

### Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Option 4: Edge Device Deployment (NVIDIA Jetson / Raspberry Pi)

### For NVIDIA Jetson Nano/Xavier

1. **Flash JetPack OS** (includes CUDA)

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip libopencv-dev
   pip3 install ultralytics opencv-python streamlit pandas firebase-admin
   ```

3. **Optimize for Edge**
   - Use FP16 inference (enabled in `detectors/yolo_wrapper.py`)
   - Process every 2-3 frames (skip frames)
   - Reduce resolution to 640x360

4. **Connect to RTSP Camera**
   ```bash
   python main.py --source rtsp://username:password@camera-ip:554/stream
   ```

---

## Post-Deployment Checklist

- [ ] Engine is running and processing video
- [ ] Dashboard is accessible via browser
- [ ] Events are being logged to `data/logs/events.jsonl`
- [ ] Firebase is receiving events (check Firestore console)
- [ ] System restarts automatically on reboot
- [ ] Monitoring/alerting is configured
- [ ] Backups are scheduled (for local file storage)
- [ ] Security: Firewall rules configured
- [ ] Security: HTTPS enabled (if public)
- [ ] Security: Firebase service account is secure

---

## Monitoring & Maintenance

### Check Service Status (Linux)
```bash
sudo systemctl status camview-engine
sudo systemctl status camview-dashboard
```

### View Logs
```bash
# Systemd logs
sudo journalctl -u camview-engine -f

# Docker logs
docker logs -f camview-engine
```

### Update the System
```bash
cd ~/CAMVIEW.AI
git pull  # if using git
sudo systemctl restart camview-engine camview-dashboard
```

### Backup Important Files
```bash
# Backup event logs
tar -czf camview-backup-$(date +%Y%m%d).tar.gz data/ firebase_service_account.json config/

# Upload to cloud storage (optional)
aws s3 cp camview-backup-*.tar.gz s3://your-bucket/backups/
```

---

## Troubleshooting

### Engine Not Starting
- Check Python version: `python --version` (must be 3.10+)
- Verify dependencies: `pip list | grep ultralytics`
- Check video source path
- Review logs for errors

### Dashboard Not Loading
- Verify Streamlit is running: `ps aux | grep streamlit`
- Check port 8501 is not blocked
- Test locally: `curl http://localhost:8501`

### No Events Appearing
- Verify YOLO model downloaded: `ls yolo11n.pt`
- Check confidence thresholds in `config/settings.py`
- Ensure video has detectable objects

### Firebase Not Working
- Verify credentials file exists
- Check Firebase project is active
- Review Firestore security rules
- Check internet connectivity

---

## Performance Optimization

### GPU Acceleration
```python
# In detectors/yolo_wrapper.py
model.to('cuda')  # Use GPU
model.half()      # FP16 precision
```

### Frame Skipping
```python
# In core/engine.py
if frame_id % 2 != 0:  # Process every 2nd frame
    continue
```

### Batch Processing
```python
# Process multiple frames at once
results = model(batch_frames)
```

---

## Scaling for Multiple Cameras

### Load Balancer Setup
```
Multiple Cameras → Load Balancer → Multiple Engine Instances → Shared Firestore
```

### Multi-Instance Configuration
Run separate instances for each camera:
```bash
# Camera 1
python main.py --source rtsp://camera1-ip --camera-id CAM_01

# Camera 2
python main.py --source rtsp://camera2-ip --camera-id CAM_02
```

All events flow to the same Firestore collection.

---

## Security Best Practices

1. **Never commit credentials** to Git
   - Add `firebase_service_account.json` to `.gitignore`

2. **Use environment variables** for sensitive data
   ```python
   import os
   FIREBASE_CREDS = os.getenv('FIREBASE_CREDENTIALS_PATH')
   ```

3. **Firewall rules**
   - Only open necessary ports (22, 8501)
   - Use VPN for remote access

4. **Regular updates**
   - Keep Python and dependencies updated
   - Monitor for security advisories

5. **Access control**
   - Add authentication to Streamlit dashboard
   - Use Firestore security rules

---

## Cost Estimation (Monthly)

| Deployment | Infrastructure | Estimated Cost |
|-----------|----------------|----------------|
| Local Server | Your hardware | Electricity only |
| AWS EC2 (t3.large) | 2 vCPU, 8GB RAM | ~$60/month |
| AWS EC2 (g4dn.xlarge) | 1 GPU, 16GB RAM | ~$380/month |
| Google Cloud VM | 4 vCPU, 15GB RAM | ~$100/month |
| Firebase Firestore | 1M writes/month | ~$5/month |

---

## Next Steps

1. Choose your deployment option
2. Follow the setup steps
3. Test with sample videos
4. Deploy to production
5. Monitor and optimize

For additional support, refer to:
- `README.md` - Project overview
- `FIREBASE_SETUP.md` - Firebase configuration
- `VIVA_EXPLANATION.md` - Technical details (if available)
