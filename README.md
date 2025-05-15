# Secure MLOps Architecture

A production-ready MLOps setup with comprehensive security, using Docker Compose, Traefik, and a Code Server development environment.

## Quick Start

```bash
chmod +x setup.sh
./setup.sh
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Traefik (Reverse Proxy)                │
│                    HTTPS Termination                        │
└─────────────────────┬─────────────────┬─────────────────────┘
                      │                 │
                      ▼                 ▼
            ┌─────────────────┐  ┌─────────────────┐
            │   Code Server   │  │    ML API       │
            │  Development    │  │   Service       │
            │  Environment    │  │                 │
            └─────────────────┘  └─────────────────┘
                      │                 │
                      │                 ▼
                      │          ┌─────────────────┐
                      │          │     Redis       │
                      │          │ Rate Limiting   │
                      │          └─────────────────┘
                      ▼                 │
            ┌─────────────────┐         │
            │   Prometheus    │         │
            │   Monitoring    │◄────────┘
            └─────────────────┘
```

## Security Features Implemented

### 1. Secure Data Handling ✅
- **Encryption**: All communication via HTTPS
- **Access Control**: JWT-based authentication with role-based access
- **Audit Logging**: Comprehensive structured logging of all actions
- **Data Validation**: Input validation and sanitization

### 2. Model Protection ✅
- **Model Integrity**: SHA256 hash verification for model files
- **Version Control**: Model versioning with metadata tracking
- **Performance Monitoring**: Real-time accuracy and behavior monitoring
- **Anomaly Detection**: Statistical validation during training

### 3. Infrastructure Security ✅
- **Container Security**: Non-root user execution, minimal base images
- **Network Segmentation**: Isolated backend network for services
- **Regular Updates**: Pinned dependencies with update procedures
- **Rate Limiting**: Per-user API rate limiting with Redis

### 4. Continuous Monitoring ✅
- **Prometheus Metrics**: Request counts, latency, prediction metrics
- **Health Checks**: Automated container health monitoring
- **Incident Response**: Structured error logging with severity levels
- **Audit Trail**: Complete request and prediction logging

## Services

### Code Server (Development Environment)
- **Access**: https://dev.localhost
- **Features**: VS Code in browser with ML libraries pre-installed
- **Security**: Password protected, isolated environment

### ML API Service
- **Access**: https://api.localhost
- **Model**: Iris classification using Random Forest
- **Security**: JWT authentication, input validation, rate limiting

### Monitoring Stack
- **Prometheus**: https://metrics.localhost
- **Metrics**: Request rates, response times, prediction counts

## API Endpoints

### Authentication
```bash
curl -X POST https://api.localhost/token
```

### Make Prediction
```bash
curl -X POST https://api.localhost/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

### Model Information
```bash
curl https://api.localhost/model/info \
  -H "Authorization: Bearer <token>"
```

## File Structure

```
.
├── docker-compose.yml          # Main orchestration
├── .env                        # Environment variables
├── setup.sh                    # Setup script
├── code-server/
│   └── Dockerfile             # Development environment
├── ml-service/
│   ├── Dockerfile             # ML API container
│   ├── main.py                # FastAPI application
│   └── requirements.txt       # Python dependencies
├── workspace/
│   ├── train_model.py         # Model training script
│   └── test_client.py         # API testing script
├── monitoring/
│   └── prometheus.yml         # Prometheus configuration
├── models/                    # Model storage (created at runtime)
├── logs/                      # Application logs
└── data/                      # Training data
```

## Development Workflow

1. **Train Model**: Use `workspace/train_model.py` to train and validate models
2. **Test API**: Run `workspace/test_client.py` to verify functionality
3. **Monitor**: Check metrics at https://metrics.localhost
4. **Develop**: Code in the browser at https://dev.localhost

## Security Best Practices

- Change default passwords in `.env`
- Use environment-specific secrets management
- Implement proper user authentication (demo uses simplified token generation)
- Regular security updates and container scanning
- Enable firewall rules in production
- Use real SSL certificates (not self-signed)

## Production Considerations

- Replace Traefik ACME staging with production server
- Implement proper user management and authentication
- Add container scanning to CI/CD pipeline
- Set up log aggregation (ELK stack)
- Configure backup strategies for models and data
- Implement proper secrets management (e.g., HashiCorp Vault)

## Troubleshooting

Check service logs:
```bash
docker-compose logs [service-name]
```

Restart services:
```bash
docker-compose restart
```

Full reset:
```bash
docker-compose down -v
docker-compose up -d
```