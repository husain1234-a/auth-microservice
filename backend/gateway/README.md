# API Gateway

Modular API Gateway for microservices with advanced routing, performance optimizations, and reliability features.

## Modular Architecture

The gateway is organized into a modular structure for better maintainability and scalability:

```
gateway/
├── app/                    # Main application package
│   ├── __init__.py        # Package initializer
│   ├── config.py          # Configuration settings
│   ├── models.py          # Data models and structures
│   ├── services.py        # Business logic and service integrations
│   └── routing.py         # API routes and request handling
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
└── Dockerfile            # Container configuration
```

## Features

### Service Routing
- Intelligent path-based routing to microservices
- Support for multiple microservices (auth, product, etc.)
- Dynamic service discovery through environment variables

### Performance Optimizations
- HTTP connection pooling for efficient resource usage
- Asynchronous request handling
- Request/response streaming for large payloads

### Reliability & Resilience
- Circuit breaker pattern to prevent cascade failures
- Automatic service health monitoring
- Graceful degradation during service outages

### Security
- Rate limiting to prevent abuse
- Request filtering and validation
- Secure header management

### Monitoring & Observability
- Detailed request logging
- Performance metrics tracking
- Health check endpoints
- Gateway statistics API

## Architecture

The API Gateway acts as a single entry point for all client requests and routes them to the appropriate microservices based on the request path:

```
Client → API Gateway → Microservices
```

### Service Mapping

| Service | Path Prefix | Target URL |
|---------|-------------|------------|
| Auth Service | `/auth` | `http://auth-service:8001` |
| Product Service | `/api` | `http://product-service:8002` |

## Modules

### Config Module (`app/config.py`)
Centralized configuration management:
- Service definitions and URLs
- Circuit breaker settings
- Rate limiting parameters

### Models Module (`app/models.py`)
Data structures and type definitions:
- Service configuration models
- Circuit breaker state management
- Rate limiting state tracking

### Services Module (`app/services.py`)
Core business logic:
- HTTP client management
- Circuit breaker implementation
- Rate limiting enforcement
- Health check utilities

### Routing Module (`app/routing.py`)
API endpoint handling:
- Request routing and forwarding
- Middleware integration
- Error handling and responses

## Endpoints

### Core Endpoints
- `GET /` - Gateway health check
- `GET /health` - Detailed health status of all services
- `GET /gateway/stats` - Gateway statistics and metrics

### Service Endpoints
- `POST /auth/*` - Authentication service endpoints
- `GET/POST/PUT/DELETE /api/*` - Product service endpoints

## Configuration

The gateway is configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTH_SERVICE_URL` | Auth service base URL | `http://localhost:8001` |
| `PRODUCT_SERVICE_URL` | Product service base URL | `http://localhost:8002` |

## Circuit Breaker

The gateway implements a circuit breaker pattern to improve system resilience:

- **CLOSED**: Normal operation, requests forwarded to service
- **OPEN**: Service is failing, requests blocked temporarily
- **HALF_OPEN**: Testing service availability after timeout

Configuration:
- Failure threshold: 5 consecutive failures
- Recovery timeout: 30 seconds

## Rate Limiting

Per-client rate limiting prevents abuse:

- Maximum 100 requests per minute per client per service
- Automatic blocking when limits exceeded
- Gradual recovery after window expires

## Health Monitoring

The gateway continuously monitors service health:

- Periodic health checks to service `/health` endpoints
- Circuit breaker state tracking
- Detailed status reporting

## Deployment

### Docker

```bash
docker-compose up gateway
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the gateway
python main.py
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Gateway Statistics
```bash
curl http://localhost:8000/gateway/stats
```

## Error Handling

The gateway provides appropriate error responses:

- `404`: Service not found
- `429`: Rate limit exceeded
- `503`: Service unavailable (circuit breaker open)
- `504`: Gateway timeout

## Extending the Gateway

To add new services:

1. Update the `SERVICES` configuration in `app/config.py`
2. Add service URL to environment variables
3. Update docker-compose.yml with new service dependencies

## Best Practices

1. **Security**: In production, restrict CORS origins to specific domains
2. **Monitoring**: Implement centralized logging for production deployments
3. **Scaling**: Deploy multiple gateway instances behind a load balancer
4. **Configuration**: Use environment-specific configuration files