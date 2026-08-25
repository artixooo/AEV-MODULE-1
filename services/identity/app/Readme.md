## Infrastructure 

- PostgreSQL connection configured through environment variables
- Redis connection configured through environment variables
- Redis connectivity verified during application startup
- Graceful Redis connection shutdown on application termination

## Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api |main and  health check|
| GET | /health | Service health check |
| GET | /ready | Redis readiness check |

## Local Service Startup

```bash
uvicorn app.main:app --reload
```

PostgreSQL and  Redis must be available before starting the Identity Service.
