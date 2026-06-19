#!/bin/bash

#Activate virtual environment to read proper variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.workload_env/bin/activate"

# ==============================================================================
# CONFIGURATION
# ==============================================================================
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"
DB_HOST="localhost"
DB_PORT="5432"

# Where backups are stored and how long to keep them
LOCAL_BACKUP_DIR="$DB_BACKUP_DIR"
RETENTION_DAYS=14  # Keeps 2 weeks of rolling daily backups

# Runtime Variables
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILENAME="${DB_NAME}_production_${TIMESTAMP}.dump"
LOCAL_BACKUP_PATH="${LOCAL_BACKUP_DIR}/${BACKUP_FILENAME}"

# ==============================================================================
# EXECUTION
# ==============================================================================
set -e # Exit immediately if any command fails

echo "[${TIMESTAMP}] Starting local multi-tenant database backup..."

# Ensure local backup directory exists with restricted access
mkdir -p "${LOCAL_BACKUP_DIR}"
chmod 0700 "${LOCAL_BACKUP_DIR}"

# 1. Run pg_dump (Custom format captures public + all tenant schemas seamlessly)
echo "Dumping database structure and data..."
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -F c -b -f "${LOCAL_BACKUP_PATH}"

# Restrict backup file permissions so other Linux users cannot read it
chmod 0600 "${LOCAL_BACKUP_PATH}"
echo "Backup created successfully at: ${LOCAL_BACKUP_PATH}"

# 2. Clean up local backups older than the retention period
echo "Cleaning up local backups older than ${RETENTION_DAYS} days..."
find "${LOCAL_BACKUP_DIR}" -name "${DB_NAME}_prod_*.dump" -type f -mtime +"${RETENTION_DAYS}" -exec rm -f {} \;

echo "[$(date +"%Y-%m-%d_%H-%M-%S")] Backup process finished successfully!"

