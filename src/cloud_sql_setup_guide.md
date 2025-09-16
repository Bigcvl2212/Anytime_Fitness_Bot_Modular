# Google Cloud SQL PostgreSQL Setup Guide

## Overview
This guide will help you set up a Google Cloud SQL PostgreSQL instance for your gym bot application and migrate from SQLite.

## Cost Considerations
- **Free Tier**: Cloud SQL offers $300 in free credits for new users
- **Micro Instance**: db-f1-micro (shared CPU, 0.6GB RAM) - ~$7/month
- **Small Instance**: db-g1-small (shared CPU, 1.7GB RAM) - ~$25/month
- **Development**: Can pause instances when not in use to save costs

## Step 1: Create Cloud SQL Instance

### Via Google Cloud Console (Recommended for first setup)

1. **Go to Cloud SQL Console**
   - Visit: https://console.cloud.google.com/sql
   - Select your project or create a new one

2. **Create Instance**
   - Click "Create Instance"
   - Choose "PostgreSQL"
   - Select "Enterprise" (for production) or "Enterprise Plus" 

3. **Configure Instance**
   ```
   Instance ID: gym-bot-postgres
   Password: [Generate strong password - save it securely]
   Database version: PostgreSQL 15 (latest stable)
   Region: us-central1 (or closest to your location)
   Zonal availability: Single zone (for development)
   Machine type: db-f1-micro (for development)
   Storage: 10GB SSD (auto-increase enabled)
   ```

4. **Network Configuration**
   - Enable "Assign a public IP address"
   - Add authorized networks: Add your current IP address
   - Consider enabling SSL connections for security

### Via gcloud CLI (Alternative)

```bash
# Install Google Cloud SDK first: https://cloud.google.com/sdk/docs/install

# Create instance
gcloud sql instances create gym-bot-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-size=10GB \
    --storage-type=SSD \
    --storage-auto-increase

# Set password for postgres user
gcloud sql users set-password postgres \
    --instance=gym-bot-postgres \
    --password=[YOUR_SECURE_PASSWORD]

# Create application database
gcloud sql databases create gym_bot --instance=gym-bot-postgres
```

## Step 2: Network Configuration

### Option A: Public IP with Authorized Networks (Simpler)
- Add your current IP address to authorized networks
- Get your IP: https://whatismyipaddress.com/
- In Cloud SQL console: Connections > Networking > Add network

### Option B: Private IP with VPC (More Secure)
- Requires VPC setup and Cloud SQL Proxy
- Better for production but more complex setup

## Step 3: Connection Information

After setup, you'll have:
```
Host: [INSTANCE_IP] (from Cloud SQL console)
Port: 5432
Database: gym_bot
Username: postgres
Password: [The password you set]
```

## Step 4: Install Cloud SQL Proxy (Optional but Recommended)

The Cloud SQL Proxy provides secure access without managing SSL certificates:

```bash
# Download Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.windows.amd64.exe

# Make executable
chmod +x cloud-sql-proxy

# Run proxy (replace with your instance connection name)
./cloud-sql-proxy [PROJECT_ID]:[REGION]:[INSTANCE_NAME]
```

## Security Best Practices

1. **Use SSL connections** - Enable in Cloud SQL settings
2. **Limit authorized networks** - Only add necessary IP addresses
3. **Use Cloud SQL Proxy** - For production deployments
4. **Regular backups** - Enable automated backups (enabled by default)
5. **Strong passwords** - Use generated passwords, not simple ones

## Cost Optimization Tips

1. **Start Small**: Use db-f1-micro for development
2. **Auto-scaling**: Enable storage auto-increase
3. **Scheduling**: Use Cloud Scheduler to stop/start instances
4. **Monitoring**: Set up billing alerts
5. **Regional Choice**: Choose region closest to your users

## Next Steps

1. Create the Cloud SQL instance
2. Configure network access
3. Test connection
4. Run migration script
5. Update application configuration

## Environment Variables for Application

```bash
DB_TYPE=postgresql
DB_HOST=[CLOUD_SQL_INSTANCE_IP]
DB_PORT=5432
DB_NAME=gym_bot
DB_USER=postgres
DB_PASSWORD=[YOUR_PASSWORD]
DB_SSL_MODE=require
```

## Troubleshooting

### Common Issues:
1. **Connection refused**: Check authorized networks
2. **SSL errors**: Verify SSL configuration
3. **Authentication failed**: Confirm username/password
4. **Timeout**: Check firewall rules and network connectivity

### Useful Commands:
```bash
# Test connection with psql
psql "host=[IP] port=5432 dbname=gym_bot user=postgres sslmode=require"

# Check Cloud SQL instance status
gcloud sql instances describe gym-bot-postgres

# View connection information
gcloud sql instances describe gym-bot-postgres --format="value(ipAddresses[0].ipAddress)"
```