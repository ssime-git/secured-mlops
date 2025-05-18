from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from typing import Callable, Awaitable
from fastapi.routing import APIRoute
from starlette.types import ASGIApp, Receive, Scope, Send

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

class MetricsMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]
        
        # Skip metrics endpoint to avoid recursive calls
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        status_code = 500  # Default to 500 in case of unhandled exceptions

        # Override the send function to capture the status code
        async def send_wrapper(response):
            nonlocal status_code
            if response["type"] == "http.response.start":
                status_code = response["status"]
            await send(response)

        try:
            await self.app(scope, receive, send_wrapper)
            
            # Record metrics
            request_duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path
            ).observe(request_duration)
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=500
            ).inc()
            raise

# Add a metrics endpoint handler
def metrics_endpoint(request: Request) -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
