# API Gateway

This API Gateway serves as a single entry point for all client requests to the microservices. It routes requests to the appropriate backend services and handles cross-cutting concerns like CORS, authentication, and rate limiting.

## Features

- **Dynamic Service Routing**: Automatically routes requests to appropriate microservices based on path prefixes
- **Service Discovery**: Configurable service endpoints with environment variables
- **Health Monitoring**: Comprehensive health checks for all services
- **Error Handling**: Proper error responses and timeouts
- **CORS Handling**: Manages cross-origin resource sharing
- **Load Balancing Ready**: Can be extended to support multiple instances of services
- **Centralized Security**: Can be extended for authentication and authorization

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Client    │───▶│  API Gateway │───▶│ Auth Service    │
└─────────────┘    └──────────────┘    └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Product Service │
                   └─────────────────┘
```

## Service Configuration

Services are configured in the SERVICES dictionary in [main.py](file:///C:/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/gateway/main.py):

```python
SERVICES = {
    "auth": {
        "url": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
        "prefix": "/auth"
    },
    "product": {
        "url": os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002"),
        "prefix": "/api"
    }
}
```

## Routes

- `/auth/*` - Routes to Authentication Service
- `/api/*` - Routes to Product Service
- `/health` - Health check endpoint for all services
- `/*` - All other routes are dynamically routed based on service prefixes

## Environment Variables

- `AUTH_SERVICE_URL` - URL of the Authentication Service (default: http://auth-service:8001)
- `PRODUCT_SERVICE_URL` - URL of the Product Service (default: http://product-service:8002)

## Running with Docker

The API Gateway is included in the main `docker-compose.yml` file and will start automatically when you run:

```bash
docker-compose up --build
```

## Ports

- API Gateway: 8000 (external access)
- Auth Service: 8001 (internal, routed through gateway)
- Product Service: 8002 (internal, routed through gateway)
- Frontend: 3000

## Accessing Services

After starting the services:

1. Frontend: http://localhost:3000
2. API Gateway: http://localhost:8000
3. Direct Auth Service: http://localhost:8001 (for debugging)
4. Direct Product Service: http://localhost:8002 (for debugging)

All client requests should go through the API Gateway on port 8000.

## Implementation Details

The gateway uses a dynamic routing approach:
1. Incoming requests are matched against service prefixes
2. Matching requests are forwarded to the appropriate service
3. Responses are proxied back to the client
4. Health checks verify all services are operational

This implementation follows microservices best practices for API gateways.