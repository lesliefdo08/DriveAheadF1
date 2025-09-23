"""
API Response Optimization and Connection Pool Management
High-performance HTTP client with connection pooling, async support, and smart retries
"""

import asyncio
import aiohttp
import requests
import time
import threading
import logging
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
import weakref

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Structured API response with metadata"""
    data: Any
    status_code: int
    response_time: float
    cached: bool = False
    source: str = "api"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ConnectionPoolManager:
    """
    Advanced HTTP connection pool manager with intelligent request routing
    Features: Connection pooling, request retries, circuit breaking, rate limiting
    """
    
    def __init__(self):
        self.session_pool = {}
        self.pool_stats = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'avg_response_time': 0,
            'connection_errors': 0
        }
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Initialize session with optimized settings
        self._init_session()
        
    def _init_session(self):
        """Initialize requests session with optimal settings"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,  # Number of connection pools
            pool_maxsize=100,     # Max connections per pool
            pool_block=False      # Don't block if pool is full
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'DriveAhead-F1-Analytics/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        self.session = session
        
    def make_request(self, 
                    method: str,
                    url: str,
                    params: Dict = None,
                    data: Dict = None,
                    headers: Dict = None,
                    timeout: float = 10.0) -> APIResponse:
        """
        Make HTTP request with connection pooling and optimization
        """
        start_time = time.time()
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is open - too many recent failures")
        
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        try:
            # Merge headers
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            # Update statistics
            self.pool_stats['requests_total'] += 1
            if response.status_code < 400:
                self.pool_stats['requests_success'] += 1
                self.circuit_breaker.record_success()
            else:
                self.pool_stats['requests_failed'] += 1
                self.circuit_breaker.record_failure()
            
            # Update average response time
            current_avg = self.pool_stats['avg_response_time']
            total_requests = self.pool_stats['requests_total']
            self.pool_stats['avg_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            return APIResponse(
                data=response.json() if response.content else None,
                status_code=response.status_code,
                response_time=response_time,
                source="live_api"
            )
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            
            # Update error statistics
            self.pool_stats['requests_total'] += 1
            self.pool_stats['requests_failed'] += 1
            self.pool_stats['connection_errors'] += 1
            self.circuit_breaker.record_failure()
            
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    def make_batch_requests(self, requests_config: List[Dict]) -> List[APIResponse]:
        """
        Make multiple HTTP requests concurrently using thread pool
        """
        futures = []
        
        for config in requests_config:
            future = self.thread_pool.submit(
                self.make_request,
                **config
            )
            futures.append(future)
        
        results = []
        for future in as_completed(futures, timeout=30):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Batch request failed: {e}")
                # Add error response
                results.append(APIResponse(
                    data=None,
                    status_code=500,
                    response_time=0,
                    source="error"
                ))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            **self.pool_stats,
            'circuit_breaker_state': self.circuit_breaker.state,
            'circuit_breaker_failures': self.circuit_breaker.failure_count,
            'rate_limiter_active': self.rate_limiter.is_limited()
        }

class CircuitBreaker:
    """
    Circuit breaker pattern for handling API failures gracefully
    """
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if request can be executed based on circuit breaker state"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if (time.time() - self.last_failure_time) > self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def record_success(self):
        """Record successful request"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
        self.failure_count = 0
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RateLimiter:
    """
    Token bucket rate limiter to prevent API abuse
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.tokens = max_requests
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit exceeded"""
        with self.lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = int(elapsed * (self.max_requests / self.window_seconds))
            
            if tokens_to_add > 0:
                self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
                self.last_refill = now
            
            # Check if we have tokens available
            if self.tokens <= 0:
                wait_time = (1 / (self.max_requests / self.window_seconds))
                time.sleep(wait_time)
                self.tokens = 1
            
            self.tokens -= 1
    
    def is_limited(self) -> bool:
        """Check if currently rate limited"""
        return self.tokens <= 0

class AsyncAPIManager:
    """
    Asynchronous API manager for high-performance concurrent requests
    """
    
    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=100,              # Total connection pool size
            limit_per_host=30,      # Max connections per host
            keepalive_timeout=60,   # Keep connections alive
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'DriveAhead-F1-Analytics-Async/1.0',
                'Accept': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str, **kwargs) -> APIResponse:
        """Fetch single URL asynchronously"""
        async with self.semaphore:
            start_time = time.time()
            
            try:
                async with self.session.get(url, **kwargs) as response:
                    data = await response.json()
                    response_time = time.time() - start_time
                    
                    return APIResponse(
                        data=data,
                        status_code=response.status,
                        response_time=response_time,
                        source="async_api"
                    )
                    
            except Exception as e:
                response_time = time.time() - start_time
                logger.error(f"Async fetch failed for {url}: {e}")
                
                return APIResponse(
                    data=None,
                    status_code=500,
                    response_time=response_time,
                    source="error"
                )
    
    async def fetch_multiple(self, urls: List[str], **kwargs) -> List[APIResponse]:
        """Fetch multiple URLs concurrently"""
        tasks = [self.fetch(url, **kwargs) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Global connection pool manager
connection_pool = ConnectionPoolManager()

# Convenience functions for optimized API calls
def optimized_get(url: str, **kwargs) -> APIResponse:
    """Make optimized GET request"""
    return connection_pool.make_request("GET", url, **kwargs)

def optimized_post(url: str, **kwargs) -> APIResponse:
    """Make optimized POST request"""
    return connection_pool.make_request("POST", url, **kwargs)

def batch_requests(configs: List[Dict]) -> List[APIResponse]:
    """Make multiple requests concurrently"""
    return connection_pool.make_batch_requests(configs)

async def async_fetch_multiple(urls: List[str]) -> List[APIResponse]:
    """Fetch multiple URLs asynchronously"""
    async with AsyncAPIManager() as manager:
        return await manager.fetch_multiple(urls)

def get_connection_stats() -> Dict[str, Any]:
    """Get connection pool statistics"""
    return connection_pool.get_stats()