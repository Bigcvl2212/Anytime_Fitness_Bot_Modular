# Gym Bot - Production Deployment Guide

This guide covers deploying the Gym Bot application to Google Cloud Run for production use.

## 🏗️ Architecture Overview

The application is structured for cloud deployment with the following components:

```
gym-bot-modular/
├── src/                    # Core application code
│   ├── main_app.py        # Flask application factory
│   ├── routes/            # API endpoints and web routes
│   ├── services/          # Business logic and integrations
│   ├── config/            # Configuration and security
│   └── utils/             # Utilities and validation
├── templates/             # HTML templates
├── static/               # CSS, JS, and assets
├── wsgi.py              # WSGI entry point
├── run_dashboard.py     # Development entry point
└── deploy.sh           # Production deployment script
```

## 🚀 Quick Deployment

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed and configured
3. **Docker** installed (for local testing)
4. **Python 3.11+** (for local development)

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd gym-bot-modular

# Set your Google Cloud project ID
export GCP_PROJECT_ID=your-project-id-here

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project $GCP_PROJECT_ID
```

### 2. Configure Environment Variables

Edit `.env.production` to set your specific configuration:

```bash
# Update these values in .env.production
GCP_PROJECT_ID=your-project-id
DB_NAME=your-database-name
# Other configuration as needed
```

### 3. Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh
```

The script will:
- Enable required Google Cloud APIs
- Build the Docker image using Cloud Build
- Deploy to Cloud Run
- Provide you with the service URL

## 🗄️ Database Setup

### Option 1: PostgreSQL on Cloud SQL (Recommended)

```bash
# Create Cloud SQL instance
gcloud sql instances create gym-bot-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create gym_bot_production \
    --instance=gym-bot-db

# Create user (optional - can use default postgres user)
gcloud sql users create app_user \
    --instance=gym-bot-db \
    --password=your-secure-password
```

### Option 2: SQLite (Development/Testing)

The application will automatically use SQLite if PostgreSQL is not configured. The database file will be stored in the container (note: data will be lost when container restarts).

## 🔐 Secrets Management

Store sensitive credentials in Google Secret Manager:

```bash
# Store ClubOS credentials
echo -n "your-clubos-username" | gcloud secrets create clubos-username --data-file=-
echo -n "your-clubos-password" | gcloud secrets create clubos-password --data-file=-

# Store Square credentials
echo -n "your-square-access-token" | gcloud secrets create square-access-token --data-file=-
echo -n "your-square-location-id" | gcloud secrets create square-location-id --data-file=-

# Store database password
echo -n "your-db-password" | gcloud secrets create db-password --data-file=-
```

## 🔧 Configuration

### Environment Variables

The application uses these environment variables (set in `.env.production`):

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `DB_TYPE` | Database type | `postgresql` |
| `DB_HOST` | Database host | `localhost` |
| `DB_NAME` | Database name | `gym_bot_production` |
| `GCP_PROJECT_ID` | Google Cloud project ID | Required |
| `LOG_LEVEL` | Logging level | `INFO` |

### Security Settings

Production security is automatically configured:
- HTTPS enforcement
- Secure cookies
- CSRF protection
- Input validation and sanitization
- Rate limiting

## 📊 Monitoring and Logs

### View Application Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

### Health Check
The application includes a health check endpoint at `/health`

### Monitoring
- Cloud Run automatically provides metrics
- Application logs are sent to Cloud Logging
- Set up alerting in Cloud Monitoring as needed

## 🔄 Updates and Maintenance

### Deploy Updates
```bash
# After making changes to the code
./deploy.sh
```

### Database Migrations
```bash
# SSH into a Cloud Run instance or use Cloud Shell
# Run migration scripts as needed
```

### Scaling
Cloud Run automatically scales based on traffic. Configure limits in the deployment:
- Max instances: 10 (configurable)
- Memory: 1Gi
- CPU: 1 vCPU
- Timeout: 300 seconds

## 🛠️ Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env.local
# Edit .env.local with your local settings

# Run locally
python run_dashboard.py
```

### Testing
```bash
# Run tests
python -m pytest tests/
```

## 🆘 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Dockerfile syntax
   - Ensure all required files are included
   - Review Cloud Build logs

2. **Database Connection Issues**
   - Verify Cloud SQL instance is running
   - Check database credentials in Secret Manager
   - Ensure network connectivity

3. **Authentication Problems**
   - Verify Google Cloud authentication
   - Check service account permissions
   - Ensure required APIs are enabled

### Debug Commands
```bash
# Check service status
gcloud run services describe gym-bot-app --region=us-central1

# View recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit=20

# Test local Docker build
docker build -t gym-bot-test .
docker run -p 8080:8080 gym-bot-test
```

## 📞 Support

For issues or questions:
1. Check the logs first
2. Review this documentation
3. Check Google Cloud documentation
4. Contact the development team

## 🔒 Security Considerations

- All sensitive data is stored in Google Secret Manager
- HTTPS is enforced in production
- Database connections are secured
- Input validation is applied to all endpoints
- Regular security updates should be applied