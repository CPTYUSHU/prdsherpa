"""
Custom middleware for the application.
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        # Start timer
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"(client: {request.client.host if request.client else 'unknown'})"
        )
        
        # Log request body for POST/PUT/PATCH (if JSON)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                # Note: This is a simplified version, in production you might want to
                # read and restore the body properly
                logger.debug(f"  Content-Type: {content_type}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            status_emoji = "✅" if response.status_code < 400 else "❌"
            logger.info(
                f"{status_emoji} {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration_ms:.2f}ms)"
            )
            
            return response
        
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"❌ {request.method} {request.url.path} "
                f"→ ERROR ({duration_ms:.2f}ms): {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            raise

