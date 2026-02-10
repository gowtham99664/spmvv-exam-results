# Deployment Script Comparison

## Scripts Available

### 1. deploy_simple.sh (RECOMMENDED)
- **Lines:** ~80 lines
- **Features:** 
  - Stop old containers
  - Start database
  - Build and start backend
  - Build and start frontend
  - Show status
- **Time:** ~5-10 minutes
- **Use when:** Quick deployments, testing, daily use

### 2. deploy_docker.sh (ADVANCED)
- **Lines:** ~365 lines
- **Features:**
  - All features from simple script
  - Automatic database backup before redeployment
  - Automatic database restore after rebuild
  - Port conflict detection
  - Deployment type detection (fresh vs redeployment)
  - Detailed progress indicators
  - Comprehensive testing
  - Backup history management
- **Time:** ~6-12 minutes (includes backup/restore)
- **Use when:** Production deployments, important updates, need backup safety

## Quick Commands

### Deploy with Simple Script
```bash
cd /root/spmvv-exam-results
./deploy_simple.sh
```

### Deploy with Full Script (with backups)
```bash
cd /root/spmvv-exam-results
./deploy_docker.sh
```

### Manual Container Management
```bash
# Check status
docker ps

# View logs
docker logs -f spmvv_backend
docker logs -f spmvv_frontend
docker logs -f spmvv_db

# Stop all
docker stop spmvv_backend spmvv_frontend spmvv_db

# Start all
docker start spmvv_db && sleep 10 && docker start spmvv_backend spmvv_frontend

# Restart one container
docker restart spmvv_backend
```

## Build Time Improvements

### Original Dockerfile
- Build time: 8-12 minutes
- Image size: ~443 MB
- Includes build tools in final image

### Optimized Dockerfile (Current)
- Build time: 4-6 minutes (first build), 30-60 seconds (cached)
- Image size: ~443 MB (same)
- Multi-stage build
- Better layer caching
- Removed build tools from runtime

### Key Optimizations
1. **Multi-stage build:** Build dependencies in separate stage
2. **Layer caching:** Dependencies cached unless requirements.txt changes
3. **No cache cleanup:** Faster pip installs when rebuilding
4. **Minimal runtime:** Only runtime dependencies in final image

## Backup Locations

All backups stored in: `/root/spmvv-exam-results/backups/`

Format: `db_backup_YYYYMMDD_HHMMSS.sql`

## Access Information

- Frontend: http://10.127.248.83:2026
- Backend: http://10.127.248.83:8000/api
- Username: admin
- Password: SpmvvExamResults
