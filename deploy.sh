#!/bin/bash

# Production Deployment Script for Gym Bot
# This script prepares and deploys the application to Google Cloud Run

set -e  # Exit on any error

echo "🚀 Starting production deployment..."

# Check if required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID environment variable is not set"
    echo "   Set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

# Set deployment variables
SERVICE_NAME="gym-bot-app"
REGION="us-central1"
IMAGE_NAME="gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME"

echo "📦 Project ID: $GCP_PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🏷️  Image: $IMAGE_NAME"

# Authenticate with Google Cloud (if not already authenticated)
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
    echo "❌ Not authenticated with Google Cloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the active project
echo "🎯 Setting active project..."
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
echo "⚡ Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Build the Docker image
echo "🔨 Building Docker image..."
gcloud builds submit --tag $IMAGE_NAME .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 100 \
    --max-instances 10 \
    --env-vars-file .env.production \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "   1. Set up Cloud SQL database if not already done"
echo "   2. Configure secrets in Google Secret Manager"
echo "   3. Test the application at the service URL"
echo ""
echo "🔍 To view logs: gcloud logging read 'resource.type=cloud_run_revision' --limit 50"
echo "⚙️  To update: Rerun this script after making changes"