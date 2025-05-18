# Secure MLOps Architecture

A production-ready MLOps setup with comprehensive security, using Docker Compose, Traefik, and a Code Server development environment.

## Quick Start

```bash
chmod +x setup.sh
./setup.sh
```

## Architecture Overview

```sh
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

## HTTPS Implementation

### Why HTTPS?

This implementation uses HTTPS (HTTP Secure) for all services to ensure:
- **Data Confidentiality**: Encrypts all data in transit between clients and services
- **Data Integrity**: Prevents tampering with data during transmission
- **Authentication**: Verifies the identity of the server
- **SEO Benefits**: Search engines prioritize HTTPS websites
- **Modern Web Standards**: Many web features require secure contexts

### Implementation Details

1. **Traefik as Reverse Proxy**
   - Terminates TLS/SSL connections
   - Handles automatic HTTP to HTTPS redirection
   - Manages Let's Encrypt certificates

2. **Automatic Certificate Management**
   - Uses Let's Encrypt for free SSL/TLS certificates
   - Automatic certificate renewal
   - Supports both HTTP and TLS challenges

3. **Security Headers**
   - HTTP Strict Transport Security (HSTS) enabled
   - Content Security Policy (CSP) headers
   - X-Content-Type-Options and X-Frame-Options set

### Accessing Services

All services are accessible via HTTPS on port 9443 with the following URLs:

- **Code Server (Development Environment)**: https://dev.localhost:9443
- **ML API**: https://api.localhost:9443
- **Grafana (Monitoring)**: https://grafana.localhost:9443
- **Prometheus (Metrics)**: https://metrics.localhost:9443
- **Traefik Dashboard**: https://dashboard.localhost:9443

### Development Notes

- **Self-Signed Certificates**: For local development, self-signed certificates are used
  - You may need to accept the security warning in your browser
  - In production, use proper domain names and Let's Encrypt certificates

- **Local DNS**: Add these entries to your `/etc/hosts` file:
  ```
  127.0.0.1 dashboard.localhost
  127.0.0.1 dev.localhost
  127.0.0.1 api.localhost
  127.0.0.1 grafana.localhost
  127.0.0.1 metrics.localhost
  ```

## Security Best Practices

- TLS 1.3 encryption enabled via Traefik

### 1. Secure Data Handling 
- **Encryption**: All communication via HTTPS
- **Access Control**: JWT-based authentication with role-based access
- **Audit Logging**: Comprehensive structured logging of all actions
- **Data Validation**: Input validation and sanitization

### 2. Model Protection 
- **Model Integrity**: SHA256 hash verification for model files
- **Version Control**: Model versioning with metadata tracking
- **Performance Monitoring**: Real-time accuracy and behavior monitoring
- **Anomaly Detection**: Statistical validation during training

### 3. Infrastructure Security 
- **Container Security**: Non-root user execution, minimal base images
- **Network Segmentation**: Isolated backend network for services
- **Regular Updates**: Pinned dependencies with update procedures
- **Rate Limiting**: Per-user API rate limiting with Redis

### 4. Continuous Monitoring 
- **Prometheus Metrics**: Request counts, latency, prediction metrics
- **Health Checks**: Automated container health monitoring
- **Incident Response**: Structured error logging with severity levels
- **Audit Trail**: Complete request and prediction logging

## Services

### Code Server (Development Environment)
- **Access**: https://dev.localhost:9443
- **Features**: VS Code in browser with ML libraries pre-installed
- **Security**: Password protected, isolated environment
- **Connectivity**: Direct access to ML API via helper module (`connect_api.py`)

### ML API Service
- **Access**: https://api.localhost:9443
- **Direct Access**: http://172.19.0.5:8000 (from code-server)
- **Model**: Iris classification using Random Forest
- **Security**: JWT authentication, input validation, rate limiting

### Monitoring Stack
- **Prometheus**: https://metrics.localhost:9443
- **Grafana**: https://grafana.localhost:9443
- **Traefik Dashboard**: https://dashboard.localhost:9443
- **Metrics**: Request rates, response times, prediction counts

## Environment Setup

### Configuration

The environment is configured using the `.env` file. A template is provided in `.env.template` that you can copy and modify:

```bash
cp .env.template .env
# Edit .env with your preferred settings
```

### Building and Starting Services

```bash
# Build and start all services
make rebuild

# View logs
make logs

# Restart services
make restart
```

## API Endpoints

### Authentication
```bash
curl -X POST https://api.localhost:9443/token
```

## Development Workflow

### Connecting to ML API from Code Server

The code server environment includes a helper module (`connect_api.py`) that simplifies connectivity to the ML API service. This module handles the direct IP-based connection to ensure reliable communication between services.

```python
# Import the helper module
from connect_api import get_health, predict, get_model_info

# Check API health
health = get_health()
print(f"API Status: {health['status']}")

# Make predictions
result = predict({"features": [5.1, 3.5, 1.4, 0.2]})
print(f"Prediction: {result}")

# Get model information
model_info = get_model_info()
print(f"Model Info: {model_info}")
```

### Testing Connectivity

To verify connectivity between the code server and ML API, run:

```bash
make test-connectivity
```

### Training a New Model

To train a new model from the code server environment:

```bash
make train
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

- TLS 1.3 encryption enabled via Traefik
- Automated Let's Encrypt certificate management
- Strict certificate pinning
- HSTS headers enforced
- OCSP stapling configured

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