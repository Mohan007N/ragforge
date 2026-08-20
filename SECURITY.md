## Security Policy

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

### Security Features

#### 1. Authentication
- **API Key Authentication**: Set `ENABLE_AUTH=true` and provide comma-separated API keys in `API_KEYS` environment variable
- **Bearer Token**: Include API key in `Authorization: Bearer <your-key>` header

#### 2. Rate Limiting
- **Default**: 60 requests per minute per IP
- **Configurable**: Set `RATE_LIMIT_REQUESTS_PER_MINUTE` in environment

#### 3. CORS Protection
- **Configurable origins**: Set `ALLOWED_ORIGINS` environment variable
- **Default (dev)**: localhost:5173, 127.0.0.1:8000
- **Production**: Set to your specific domain(s)

#### 4. File Upload Security
- **File type validation**: Only PDF files accepted
- **Size limits**: Default 50MB (configurable via `MAX_FILE_SIZE`)
- **Content validation**: Filters blank pages and validates text

#### 5. Input Sanitization
- **Query length limits**: Max 5000 characters
- **XSS prevention**: Strips script tags and javascript: URLs
- **SQL injection**: Uses ORM/prepared statements (not applicable for document DB)

### Recommended Production Setup

#### 1. Enable HTTPS
```bash
# Use reverse proxy (nginx, Caddy, Traefik)
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

#### 2. Enable Authentication
```bash
# .env file
ENABLE_AUTH=true
API_KEYS=super-secret-key-123,another-key-456
```

#### 3. Configure CORS Properly
```bash
# .env file
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### 4. Use Environment Variables
```bash
# Never commit .env file to version control
echo ".env" >> .gitignore

# Use strong API keys
openssl rand -base64 32
```

#### 5. Set Up Monitoring
```bash
# Enable health checks
curl https://yourapi.com/api/health

# Monitor metrics (requires auth)
curl -H "Authorization: Bearer YOUR_KEY" https://yourapi.com/api/metrics
```

### Reporting a Vulnerability

If you discover a security vulnerability, please email security@example.com (replace with your email).

**Please do not open public issues for security vulnerabilities.**

We aim to respond within 48 hours and provide a fix within 7 days for critical issues.

### Security Best Practices

#### For Developers
1. Always validate user input
2. Use parameterized queries
3. Keep dependencies updated (`pip list --outdated`)
4. Run security audits (`pip-audit`)
5. Use HTTPS in production
6. Enable authentication
7. Set strong API keys (32+ characters)
8. Implement proper logging
9. Use rate limiting
10. Regular security updates

#### For Deployment
1. Use Docker with non-root user
2. Set resource limits (CPU, memory)
3. Use firewall rules
4. Enable automatic security updates
5. Regular backups
6. Monitoring and alerting
7. Penetration testing
8. Security scanning (Snyk, Dependabot)

### Known Limitations

#### Development Mode (Current)
- CORS allows all origins (set `ALLOWED_ORIGINS` for production)
- Authentication disabled by default (enable with `ENABLE_AUTH=true`)
- Rate limiting is in-memory (use Redis for distributed setup)
- No session management
- No audit logging

#### Production Recommendations
- [ ] Implement JWT authentication
- [ ] Use Redis for rate limiting
- [ ] Add audit logging
- [ ] Implement session management
- [ ] Add request signing
- [ ] Use API gateway (Kong, Tyk)
- [ ] Implement IP whitelisting
- [ ] Add DDoS protection
- [ ] Use WAF (Web Application Firewall)
- [ ] Implement RBAC (Role-Based Access Control)

### Security Checklist

Before deploying to production:

- [ ] HTTPS enabled
- [ ] Authentication enabled
- [ ] Strong API keys configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] File size limits set
- [ ] Input validation in place
- [ ] Error messages don't leak info
- [ ] Logs don't contain sensitive data
- [ ] Dependencies updated
- [ ] Security audit completed
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Incident response plan ready

### Compliance

#### GDPR Considerations
- Documents are stored locally (no cloud transfer)
- Delete endpoint removes all user data
- No personal data collection by default
- Privacy by design

#### Data Retention
- Documents: User-managed (manual delete)
- Logs: Configurable retention
- Metrics: In-memory (resets on restart)

### Updates

Check for security updates:
```bash
# Backend
pip list --outdated
pip-audit

# Frontend
cd react-frontend
npm audit
npm audit fix
```

### Contact

For security concerns: security@example.com  
For general issues: GitHub Issues (non-security only)
