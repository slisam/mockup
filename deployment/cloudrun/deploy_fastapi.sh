#!/usr/bin/env bash
set -e

# ---------------------------------------------------------------------
# Global configuration
# ---------------------------------------------------------------------
PROJECT_ID="prj-ceva-ao-rate-card-sbx"
REGION="europe-west3"
REPOSITORY="ar-docker-euw3-rate-card-sbx"

SERVICE_NAME="crs-euw3-fastapi-dev"

# Directory of this script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$(cd "$SCRIPT_DIR/../.." && pwd)

echo "ROOT_DIR = $ROOT_DIR"
echo ""

# ---------------------------------------------------------------------
# Docker Authentication
# ---------------------------------------------------------------------
echo "Configuring Docker authentication with Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# ---------------------------------------------------------------------
# Resolve image URL
# ---------------------------------------------------------------------
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest"

echo "IMAGE_URL = $IMAGE_URL"
echo ""

# ---------------------------------------------------------------------
# Build Docker image (linux/amd64 forced)
# ---------------------------------------------------------------------
echo "----------------------------------------------"
echo "Building Docker image"
echo "----------------------------------------------"

docker buildx create --use > /dev/null 2>&1 || true

docker buildx build \
    --platform linux/amd64 \
    -t "$IMAGE_URL" \
    --push \
    "$ROOT_DIR"

echo ""
echo "Docker image built and pushed."
echo ""

# ---------------------------------------------------------------------
# Deploy Cloud Run Service (private)
# ---------------------------------------------------------------------
echo "----------------------------------------------"
echo "Deploying Cloud Run Service: $SERVICE_NAME"
echo "----------------------------------------------"

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_URL" \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --platform managed \
    --no-allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 600 \
    --port 8000 \
    --set-env-vars MODE=cloud \
    --set-env-vars PROJECT_ID=${PROJECT_ID} \
    --set-env-vars REGION=${REGION} \
    --set-env-vars BUCKET=csv-reg-euw3-rate-card-process \
    --set-env-vars GCS_DB_PATH=api-db/ratecard.sqlite \
    --set-env-vars LOCAL_DB_PATH=/tmp/ratecard.sqlite

echo ""
echo "----------------------------------------------"
echo "Deployment complete for service: $SERVICE_NAME"
echo "URL (IAM protected):"
gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format="value(status.url)"
echo "----------------------------------------------"