from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import secure
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:;"
        )
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with sanitized data"""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = datetime.now()
        
        # Get request details
        method = request.method
        url = str(request.url)
        client = request.client.host if request.client else "unknown"
        
        # Sanitize headers for logging
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "***"
        if "cookie" in headers:
            headers["cookie"] = "***"
        
        # Log request
        logger.info(
            f"Request: {method} {url}\n"
            f"Client: {client}\n"
            f"Headers: {json.dumps(headers, indent=2)}"
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log response
        logger.info(
            f"Response: {response.status_code}\n"
            f"Duration: {duration:.3f}s"
        )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting"""
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = datetime.now().timestamp()
        
        # Clean up old requests
        self.requests = {
            ip: reqs for ip, reqs in self.requests.items()
            if current_time - reqs[-1] < self.window_seconds
        }
        
        # Check rate limit
        if client_ip in self.requests:
            requests = self.requests[client_ip]
            if len(requests) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                raise HTTPException(status_code=429, detail="Too many requests")
            requests.append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)

class SQLInjectionMiddleware(BaseHTTPMiddleware):
    """Middleware to detect and prevent SQL injection attempts"""
    def __init__(self, app):
        super().__init__(app)
        self.sql_patterns = [
            "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION",
            "OR '1'='1", "OR 1=1", "--", "/*", "*/", "EXEC", "EXECUTE"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check query parameters
        query_params = str(request.query_params)
        if any(pattern.lower() in query_params.lower() for pattern in self.sql_patterns):
            logger.warning(f"Potential SQL injection detected in query params: {query_params}")
            raise HTTPException(status_code=403, detail="Invalid request")
        
        # Check request body if it's a POST/PUT request
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.json()
                body_str = json.dumps(body).lower()
                if any(pattern.lower() in body_str for pattern in self.sql_patterns):
                    logger.warning(f"Potential SQL injection detected in request body")
                    raise HTTPException(status_code=403, detail="Invalid request")
            except:
                pass  # Not JSON body or empty body
        
        return await call_next(request)

class XSSMiddleware(BaseHTTPMiddleware):
    """Middleware to prevent XSS attacks"""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add XSS protection headers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:;"
        )
        
        return response 