# Production Deployment Checklist

**Project:** MGA Soap Calculator API v1.0.0
**Date:** 2025-11-02
**Target Deployment:** MGA Automotive Internal Infrastructure

Use this checklist to ensure the application is production-ready before deployment.

---

## Pre-Deployment (1-2 Days Before)

### Code & Dependencies
- [ ] All tests passing: `pytest tests/ -v` (expect 21/21 passing)
- [ ] Code coverage acceptable: `pytest --cov=app` (expect 80%+)
- [ ] No security vulnerabilities: Review dependencies with `pip-audit`
- [ ] Code formatting correct: `ruff check app/`
- [ ] Type checking passes: `mypy app/`

### Documentation
- [ ] API documentation complete at `/docs` endpoint
- [ ] Deployment guide reviewed: `docs/DEPLOYMENT.md`
- [ ] API reference complete: `docs/API_REFERENCE.md`
- [ ] Database schema documented
- [ ] Environment variables documented in `.env.example`

### Database
- [ ] Database schema finalized (no pending migrations)
- [ ] Seed data verified (11+ oils, 12+ additives)
- [ ] Database indexes created for performance
- [ ] Backup strategy documented
- [ ] Data retention policy defined

---

## Infrastructure Setup (Days Before Deployment)

### Servers
- [ ] Production server(s) provisioned
- [ ] CPU: 2+ cores, RAM: 2GB minimum
- [ ] Disk space: 10GB+ for PostgreSQL data
- [ ] Network connectivity verified
- [ ] Firewall rules configured (allow port 8000 or 443)

### Database Server
- [ ] PostgreSQL 15+ installed and configured
- [ ] PostgreSQL listening on secure port (default 5432)
- [ ] Database credentials generated and stored securely
- [ ] Connection pooling configured
- [ ] Backup schedule configured (daily minimum)
- [ ] WAL archiving enabled for point-in-time recovery

### Secrets Management
- [ ] Secure `SECRET_KEY` generated (32+ characters)
- [ ] Database passwords generated (20+ characters, random)
- [ ] Stored in secure vault (Vault, Secrets Manager, etc.)
- [ ] Not hardcoded in any files
- [ ] Rotation policy defined
- [ ] Access logging enabled

### Networking
- [ ] DNS records configured (if using custom domain)
- [ ] SSL/TLS certificates installed (if using HTTPS)
- [ ] Certificates valid and not self-signed
- [ ] Certificate expiry monitoring configured
- [ ] CORS origins configured correctly
- [ ] Load balancer configured (if multiple instances)

### Monitoring & Logging
- [ ] Log aggregation configured (ELK, CloudWatch, etc.)
- [ ] Application monitoring set up (Datadog, New Relic, etc.)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Alerting rules configured
  - [ ] API down alert
  - [ ] High error rate alert
  - [ ] Database connection errors alert
  - [ ] High response time alert
- [ ] Health check monitoring enabled

---

## Final Verification (1 Hour Before Deployment)

### Application Build
- [ ] Docker image built: `docker build -t mga-soap-api:1.0.0 .`
- [ ] Image scanned for vulnerabilities: `trivy image mga-soap-api:1.0.0`
- [ ] Image pushed to registry (if using private registry)
- [ ] Build artifacts verified in registry

### Environment Variables
- [ ] `.env` file created with production values
- [ ] All required variables set:
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY`
  - [ ] `ENVIRONMENT=production`
  - [ ] `ALLOWED_ORIGINS`
- [ ] No default/development values in production
- [ ] File permissions restricted (mode 600)
- [ ] File backed up to secure location

### Database Preparation
- [ ] Database created: `CREATE DATABASE mga_soap_calculator_prod;`
- [ ] Test connection successful: `psql $DATABASE_URL -c "SELECT 1;"`
- [ ] Migrations prepared but not yet run
- [ ] Seed data files prepared
- [ ] Backup of initial schema created

### Container Testing
- [ ] Run locally: `docker-compose -f docker-compose.prod.yml up`
- [ ] Health check responds: `curl http://localhost:8000/api/v1/health`
- [ ] Can register user
- [ ] Can login and get token
- [ ] Can create calculation
- [ ] Can retrieve calculation
- [ ] Container shuts down gracefully
- [ ] Logs are readable and contain no errors

---

## Deployment Day (Execution)

### Pre-Deployment Notification
- [ ] Notify stakeholders deployment is beginning
- [ ] Create incident/change ticket if required
- [ ] Establish rollback plan with team
- [ ] Have emergency contact list ready

### Database Migration
- [ ] Run migrations in production: `alembic upgrade head`
- [ ] Verify migration success (no errors in logs)
- [ ] Check tables created: `\dt` in psql
- [ ] Verify indexes: `\di` in psql

### Load Initial Data
- [ ] Load seed data: `python scripts/seed_database.py`
- [ ] Verify oils loaded: `SELECT COUNT(*) FROM oils;` (expect 11+)
- [ ] Verify additives loaded: `SELECT COUNT(*) FROM additives;` (expect 12+)

### Deploy Application
- [ ] Pull/build latest image
- [ ] Start containers: `docker-compose -f docker-compose.prod.yml up -d`
- [ ] Wait 30 seconds for startup
- [ ] Check container logs: `docker logs mga_soap_api_prod`
- [ ] Verify no errors in logs
- [ ] Verify health endpoint: `curl https://api.yourserver.com/api/v1/health`

### Smoke Tests
- [ ] Register test user
- [ ] Login and get token
- [ ] Create test calculation
- [ ] Retrieve calculation
- [ ] Verify response data is correct
- [ ] Check API documentation loads: `/docs`
- [ ] Run automated smoke tests if available

### Monitoring Verification
- [ ] Health alerts configured and testing
- [ ] Error rate monitored
- [ ] Response time monitored
- [ ] Database connections monitored
- [ ] CPU and memory monitored
- [ ] Disk space monitored

### Documentation Updates
- [ ] Update production server URL in documentation
- [ ] Update runbooks with production procedures
- [ ] Document any deployment-specific configurations
- [ ] Record deployment time and status

---

## Post-Deployment (Ongoing)

### First Hour
- [ ] Monitor error logs closely
- [ ] Watch for any alerts triggered
- [ ] Monitor database connection pool
- [ ] Verify response times are acceptable (<500ms p95)
- [ ] Check calculation accuracy against reference data

### First Day
- [ ] Review all logs for errors or warnings
- [ ] Verify backups are working
- [ ] Test failover procedures if applicable
- [ ] Document any issues encountered
- [ ] Monitor performance metrics

### First Week
- [ ] Verify calculation accuracy with multiple test cases
- [ ] Load test with realistic user patterns
- [ ] Monitor resource usage trends
- [ ] Verify data integrity
- [ ] Review and analyze error logs
- [ ] Update incident response procedures based on learnings

### Ongoing
- [ ] Monitor health metrics daily
- [ ] Review logs at least weekly
- [ ] Test disaster recovery procedures monthly
- [ ] Update security patches as needed
- [ ] Monitor token expiry and refresh processes
- [ ] Track API usage and performance trends

---

## Rollback Plan

If critical issues occur during/after deployment:

### Immediate Actions
1. [ ] Notify stakeholders of issue
2. [ ] Collect error logs and diagnostics
3. [ ] Decide: fix forward vs. rollback

### Rollback Procedure
1. [ ] Stop new application: `docker-compose down`
2. [ ] Restore from previous backup if data changed
3. [ ] Restart old version: `docker-compose -f docker-compose.old.yml up -d`
4. [ ] Verify health: `curl http://localhost:8000/api/v1/health`
5. [ ] Verify core functionality works
6. [ ] Notify stakeholders rollback complete

### Investigation After Rollback
1. [ ] Collect all logs and metrics
2. [ ] Identify root cause
3. [ ] Create issue tickets for problems found
4. [ ] Schedule fixes and retry deployment

---

## Performance Benchmarks

**Acceptable Ranges (Post-Deployment):**

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Response Time (p95) | <500ms | >500ms | >2000ms |
| Error Rate | <0.1% | >0.1% | >1% |
| CPU Usage | <40% | >60% | >80% |
| Memory Usage | <50% | >70% | >85% |
| Database Pool | <10/20 | >15/20 | >18/20 |
| Uptime | >99.5% | <99.5% | <99% |

---

## Security Verification

- [ ] All secrets stored securely (no plaintext in config)
- [ ] HTTPS enabled (if applicable)
- [ ] JWT tokens properly validated
- [ ] Database password protected
- [ ] Access logs enabled
- [ ] Audit logging configured
- [ ] CORS properly restricted
- [ ] No sensitive data in logs
- [ ] Rate limiting configured (if needed)
- [ ] API documentation doesn't expose sensitive info

---

## Success Criteria

Deployment is successful when:

1. ✓ All tests passing in production environment
2. ✓ Health endpoint responds correctly
3. ✓ Can complete full user workflow (register → login → calculate → retrieve)
4. ✓ No errors in application logs (first hour)
5. ✓ Response times within benchmarks
6. ✓ Monitoring and alerting working
7. ✓ Database backups operational
8. ✓ Documentation updated

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Deployer | | | |
| QA Lead | | | |
| Product Manager | | | |
| DevOps Lead | | | |

---

**Deployment Date:** _______________
**Deployment Time:** _______________
**Deployed By:** _______________
**Status:** ☐ Success ☐ Partial ☐ Rollback

**Notes:**
_________________________________________________________________
_________________________________________________________________

---

**Last Updated:** 2025-11-02
**Document Version:** 1.0
