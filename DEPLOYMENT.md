# Production Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Variables
Set the following environment variables on your production server:

```bash
# Security
export SECRET_KEY="your-very-strong-secret-key-here"

# Database
export DATABASE_URL="postgresql://username:password@host:port/database_name"

# API Keys
export OPENWEATHER_API_KEY="your-openweather-api-key"
export TWILIO_ACCOUNT_SID="your-twilio-account-sid"
export TWILIO_AUTH_TOKEN="your-twilio-auth-token"
export TWILIO_PHONE_NUMBER="your-twilio-phone-number"

# Redis for rate limiting
export REDIS_URL="redis://localhost:6379"

# Flask environment
export FLASK_ENV="production"
export FLASK_APP="run.py"
```

### 2. Database Setup
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createuser smart_agriculture_user
sudo -u postgres createdb smart_agriculture
sudo -u postgres psql -c "ALTER USER smart_agriculture_user PASSWORD 'strong_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smart_agriculture TO smart_agriculture_user;"
```

### 3. Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 4. SSL Certificate
- Obtain SSL certificate (Let's Encrypt, CloudFlare, or commercial CA)
- Configure web server (Nginx/Apache) to use HTTPS
- Update SECURITY_HEADERS in config to include HSTS

### 5. Web Server Configuration

#### Nginx Configuration Example:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # File upload limits
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static {
        alias /path/to/smart_agriculture_app/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6. Application Deployment
```bash
# Install system dependencies
sudo apt-get install python3 python3-pip python3-venv

# Clone application
git clone <your-repo-url>
cd smart_agriculture_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python run.py db upgrade  # If using Flask-Migrate
# Or
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

### 7. Process Management (Systemd Service)
Create `/etc/systemd/system/smart-agriculture.service`:

```ini
[Unit]
Description=Smart Crop Care Assistant Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/smart_agriculture_app
Environment=PATH=/path/to/smart_agriculture_app/venv/bin
EnvironmentFile=/path/to/smart_agriculture_app/.env
ExecStart=/path/to/smart_agriculture_app/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-agriculture
sudo systemctl start smart-agriculture
```

## Security Checklist

### ✅ Completed
- [x] SQLAlchemy 2.0 compatibility (Query.get → Session.get)
- [x] Timezone-aware datetime usage
- [x] Security headers implementation
- [x] Rate limiting configured
- [x] File upload validation and security
- [x] Input validation and sanitization
- [x] Error handling and logging
- [x] CSRF protection (Flask-WTF)
- [x] Password hashing (Werkzeug)
- [x] Session security configuration

### ⚠️ Production Requirements
- [ ] Strong SECRET_KEY in environment
- [ ] PostgreSQL database instead of SQLite
- [ ] Redis for session storage and rate limiting
- [ ] SSL/TLS certificate configured
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting setup

## Performance Optimization

### Database
- [ ] Database connection pooling configured
- [ ] Database indexes optimized
- [ ] Query performance analyzed

### Caching
- [ ] Redis caching for frequent queries
- [ ] Static file caching headers set
- [ ] CDN for static assets (optional)

### Monitoring
- [ ] Application performance monitoring (APM)
- [ ] Error tracking (Sentry, Rollbar)
- [ ] Log aggregation (ELK stack, CloudWatch)
- [ ] Health check endpoints

## Backup and Recovery

### Database Backups
```bash
# Daily backup script
#!/bin/bash
pg_dump smart_agriculture > backup_$(date +%Y%m%d).sql
# Upload to cloud storage
```

### Application Backups
- [ ] Code repository backups
- [ ] Configuration file backups
- [ ] Upload directory backups
- [ ] SSL certificate backups

## Maintenance

### Regular Tasks
- [ ] Security updates (weekly)
- [ ] Database maintenance (monthly)
- [ ] Log rotation (daily)
- [ ] Backup verification (weekly)
- [ ] Performance review (monthly)

### Monitoring Alerts
- [ ] High error rates
- [ ] Database connection issues
- [ ] High memory/CPU usage
- [ ] Disk space warnings
- [ ] SSL certificate expiration

## Scaling Considerations

### Horizontal Scaling
- [ ] Load balancer configuration
- [ ] Session storage in Redis
- [ ] Database read replicas
- [ ] Static file CDN

### Vertical Scaling
- [ ] Server resource monitoring
- [ ] Database performance tuning
- [ ] Application profiling
