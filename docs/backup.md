# Backup and Recovery Strategy

This document outlines the backup and recovery procedures for the Holiday Holliday application deployed on Azure Container Apps.

## Database Backups

### Azure Database for PostgreSQL

The application uses Azure Database for PostgreSQL, which provides automated backups:

- **Automated backups**: Enabled by default with 7-day retention
- **Backup storage**: Geo-redundant storage (GRS) for disaster recovery
- **Point-in-time restore**: Available within the retention period

#### Configuring Backup Retention

To modify the backup retention period (up to 35 days):

```bash
az postgres server update \
  --resource-group <resource-group-name> \
  --name <server-name> \
  --backup-retention 30
```

#### Manual Backup (Snapshot)

Create a manual backup before major deployments:

```bash
az postgres server create \
  --resource-group <resource-group-name> \
  --name <server-name>-backup-$(date +%Y%m%d) \
  --location <location> \
  --sku-name GP_Gen5_2 \
  --storage-size 51200
```

## Manual Database Backup Scripts

### Full Database Dump

```bash
#!/bin/bash
# backup-db.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="holiday_holliday_backup_${TIMESTAMP}.sql"

pg_dump \
  -h ${POSTGRES_HOST} \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_NAME} \
  -F c \
  -f ${BACKUP_FILE}

# Compress the backup
gzip ${BACKUP_FILE}

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Automated Backup Script with Azure Storage

```bash
#!/bin/bash
# backup-to-azure.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="holiday_holliday_backup_${TIMESTAMP}.sql"
STORAGE_ACCOUNT="<storage-account-name>"
CONTAINER_NAME="backups"

# Create backup
pg_dump \
  -h ${POSTGRES_HOST} \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_NAME} \
  -F c \
  -f ${BACKUP_FILE}

# Compress
gzip ${BACKUP_FILE}

# Upload to Azure Blob Storage
az storage blob upload \
  --account-name ${STORAGE_ACCOUNT} \
  --container-name ${CONTAINER_NAME} \
  --name ${BACKUP_FILE}.gz \
  --file ${BACKUP_FILE}.gz

# Clean up local file
rm ${BACKUP_FILE}.gz

echo "Backup uploaded to Azure Storage"
```

## Recovery Procedures

### Point-in-Time Restore (Azure Portal)

1. Navigate to Azure Portal > PostgreSQL servers
2. Select your server
3. Click "Restore" in the top menu
4. Choose "Point-in-time" restore type
5. Select the restore point
6. Configure the new server details
7. Review and create

### Restore from Backup File

```bash
#!/bin/bash
# restore-db.sh

BACKUP_FILE=$1

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
  gunzip ${BACKUP_FILE}
  BACKUP_FILE=${BACKUP_FILE%.gz}
fi

# Restore
pg_restore \
  -h ${POSTGRES_HOST} \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_NAME} \
  --clean \
  --if-exists \
  ${BACKUP_FILE}

echo "Restore completed"
```

## Environment Variables Backup

Store these environment variables securely:

```bash
# .env.backup (store in secure location, NOT in git)
SECRET_KEY=<your-secret-key>
POSTGRES_NAME=holiday_holliday
POSTGRES_USER=holiday
POSTGRES_PASSWORD=<secure-password>
POSTGRES_HOST=<server>.postgres.database.azure.com
POSTGRES_PORT=5432
REDIS_URL=redis://<redis-host>:6379/0
DEBUG=false
ALLOWED_HOSTS=<your-domain>
```

## Redis Cache

Redis is used for caching and WebSocket channels. Data is ephemeral and doesn't require backup.

## Backup Schedule Recommendations

| Backup Type | Frequency | Retention |
|-------------|-----------|-----------|
| Automated PostgreSQL | Daily | 30 days |
| Manual snapshot | Before deployments | 90 days |
| Environment variables | On change | Indefinite |

## Disaster Recovery Plan

### Scenario 1: Database Corruption

1. Assess the extent of corruption
2. Stop the application to prevent further damage
3. Restore from the last known good backup
4. Verify data integrity
5. Restart the application

### Scenario 2: Complete Region Failure

1. Azure's geo-redundant storage ensures backups are available
2. Deploy application to secondary region
3. Restore database from geo-redundant backup
4. Update DNS to point to new region
5. Verify application functionality

### Scenario 3: Accidental Data Deletion

1. Identify the deletion time
2. Use point-in-time restore to just before deletion
3. Export the deleted data
4. Import the data to production
5. Verify data integrity

## Testing Backups

Regularly test backup restoration:

```bash
# Monthly test restore to staging
./restore-db.sh holiday_holliday_backup_20260220_120000.sql

# Verify key data points
python manage.py shell << EOF
from apps.leave.models import LeaveEntry
print(f"Total entries: {LeaveEntry.objects.count()}")
EOF
```

## Monitoring and Alerts

Configure Azure Monitor alerts for:

- Backup failures
- Storage capacity thresholds
- Database connection issues
- Unusual query patterns

## Security Considerations

- Encrypt backups at rest (enabled by default in Azure)
- Use managed identities for backup operations
- Restrict backup storage access to authorized personnel
- Rotate database credentials regularly
- Never commit credentials to version control

## Contact

For backup-related issues, contact the development team or refer to the Azure Portal documentation.
