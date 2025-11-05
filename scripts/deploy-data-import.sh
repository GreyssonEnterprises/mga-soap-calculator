#!/bin/bash
# Deploy and import complete ingredient databases to grimm-lin

set -e

echo "==> Deploying ingredient data import to grimm-lin"

# Create remote working directory
ssh grimm-lin "mkdir -p /tmp/mga-data-import"

# Copy JSON data files
echo "Copying oils database..."
scp working/user-feedback/oils-db-additions/complete-oils-database.json grimm-lin:/tmp/mga-data-import/

echo "Copying additives database..."
scp working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json grimm-lin:/tmp/mga-data-import/

echo "Copying essential oils database..."
scp working/user-feedback/essential-oils-usage-reference.json grimm-lin:/tmp/mga-data-import/

echo "Copying colorants database..."
scp working/user-feedback/natural-colorants-reference.json grimm-lin:/tmp/mga-data-import/

# Copy import scripts
echo "Copying import scripts..."
scp scripts/import_oils_database.py grimm-lin:/tmp/mga-data-import/
scp scripts/import_additives.py grimm-lin:/tmp/mga-data-import/
scp scripts/import_essential_oils.py grimm-lin:/tmp/mga-data-import/
scp scripts/import_colorants.py grimm-lin:/tmp/mga-data-import/

# Copy data files into container working directory
echo "Copying data files into container..."
ssh grimm-lin "podman cp /tmp/mga-data-import/complete-oils-database.json soap-api:/opt/app-root/src/working/user-feedback/oils-db-additions/"
ssh grimm-lin "podman cp /tmp/mga-data-import/additives-usage-reference.json soap-api:/opt/app-root/src/working/user-feedback/additive-calculator-feature-request/"
ssh grimm-lin "podman cp /tmp/mga-data-import/essential-oils-usage-reference.json soap-api:/opt/app-root/src/working/user-feedback/"
ssh grimm-lin "podman cp /tmp/mga-data-import/natural-colorants-reference.json soap-api:/opt/app-root/src/working/user-feedback/"

# Run imports from app root with PYTHONPATH
echo ""
echo "==> Importing oils database (151 oils)..."
ssh grimm-lin "podman exec -w /opt/app-root/src -e PYTHONPATH=/opt/app-root/src soap-api python scripts/import_oils_database.py"

echo ""
echo "==> Importing additives (30 additives)..."
ssh grimm-lin "podman exec -w /opt/app-root/src -e PYTHONPATH=/opt/app-root/src soap-api python scripts/import_additives.py"

echo ""
echo "==> Importing essential oils (39 essential oils)..."
ssh grimm-lin "podman exec -w /opt/app-root/src -e PYTHONPATH=/opt/app-root/src soap-api python scripts/import_essential_oils.py"

echo ""
echo "==> Importing colorants (79 colorants)..."
ssh grimm-lin "podman exec -w /opt/app-root/src -e PYTHONPATH=/opt/app-root/src soap-api python scripts/import_colorants.py"

# Verify counts
echo ""
echo "==> Verification:"
echo -n "Oils: "
curl -s http://grimm-lin:8000/api/v1/oils | jq 'length'
echo -n "Additives: "
curl -s http://grimm-lin:8000/api/v1/additives | jq 'length'
echo -n "Essential Oils: "
curl -s http://grimm-lin:8000/api/v1/essential-oils | jq 'length'
echo -n "Colorants: "
curl -s http://grimm-lin:8000/api/v1/colorants | jq 'length'

echo ""
echo "✅ Data import complete!"
