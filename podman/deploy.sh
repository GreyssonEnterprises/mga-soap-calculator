#!/bin/bash
set -euo pipefail

echo "🚀 Deploying MGA Soap Calculator to Podman on Fedora 42..."

# Build container image
echo "📦 Building container image..."
podman build -t localhost/mga-soap-calculator:latest .

# Create systemd user directory
echo "📁 Setting up Quadlet systemd directory..."
mkdir -p ~/.config/containers/systemd

# Copy Quadlet files
echo "📋 Installing Quadlet service units..."
cp podman/systemd/*.container ~/.config/containers/systemd/
cp podman/systemd/*.network ~/.config/containers/systemd/

# Create volumes
echo "💾 Creating persistent volumes..."
podman volume create mga-pgdata || true
podman volume create mga-logs || true

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl --user daemon-reload

# Enable and start services
echo "🌐 Starting network..."
systemctl --user enable --now mga-network

echo "🗄️  Starting PostgreSQL..."
systemctl --user enable --now mga-postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to initialize..."
sleep 10

echo "🌟 Starting MGA API..."
systemctl --user enable --now mga-api

# Enable linger for persistent services
echo "🔒 Enabling user linger for service persistence..."
loginctl enable-linger $USER || true

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Check service status:"
echo "  systemctl --user status mga-api"
echo "  systemctl --user status mga-postgres"
echo ""
echo "View logs:"
echo "  journalctl --user -u mga-api -f"
echo ""
echo "Health check:"
echo "  curl http://localhost:8000/api/v1/health"
