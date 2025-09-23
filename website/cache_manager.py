"""
Advanced Cache Management System for DriveAhead
Provides Redis-like caching with SQLite fallback, TTL support, and performance optimization
"""

import sqlite3
import json
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps
import hashlib
import pickle
import gzip
import concurrent.futures

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedCacheManager:
    """
    High-performance cache manager with multiple storage backends
    Features: TTL support, compression, thread-safe operations, cache warming
    """
    
    def __init__(self, 
                 cache_dir: str = 'cache',
                 db_name: str = 'advanced_cache.db',
                 default_ttl: int = 300,  # 5 minutes
                 max_memory_items: int = 1000,
                 enable_compression: bool = True):
        
        self.cache_dir = cache_dir
        self.db_path = os.path.join(cache_dir, db_name)
        self.default_ttl = default_ttl
        self.max_memory_items = max_memory_items
        self.enable_compression = enable_compression
        
        # In-memory cache for frequently accessed data
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'evictions': 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Initialize storage
        self._init_cache_directory()
        self._init_database()
        
        # Background cleanup thread
        self._start_cleanup_thread()
        
    def _init_cache_directory(self):
        """Create cache directory if it doesn't exist"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _init_database(self):
        """Initialize SQLite database for persistent caching"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    created_at REAL,
                    expires_at REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    compressed BOOLEAN DEFAULT 0
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)')
            conn.commit()
            
    def _start_cleanup_thread(self):
        """Start background thread for cache maintenance"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_entries()
                    self._optimize_memory_cache()
                    time.sleep(60)  # Run every minute
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
                    
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        
    def _generate_key(self, key: str) -> str:
        """Generate a consistent cache key"""
        if isinstance(key, str):
            return hashlib.md5(key.encode('utf-8')).hexdigest()
        return hashlib.md5(str(key).encode('utf-8')).hexdigest()
        
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data if compression is enabled"""
        if self.enable_compression and len(data) > 1024:  # Only compress larger data
            return gzip.compress(data)
        return data
        
    def _decompress_data(self, data: bytes, is_compressed: bool) -> bytes:
        """Decompress data if it was compressed"""
        if is_compressed and self.enable_compression:
            return gzip.decompress(data)
        return data
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store data in cache with optional TTL"""
        if ttl is None:
            ttl = self.default_ttl
            
        cache_key = self._generate_key(key)
        expires_at = time.time() + ttl if ttl > 0 else 0  # 0 means never expires
        
        try:
            # Serialize data
            serialized_data = pickle.dumps(value)
            
            # Compress if enabled
            compressed_data = self._compress_data(serialized_data)
            is_compressed = len(compressed_data) < len(serialized_data)
            
            with self.lock:
                # Store in memory cache if it's small enough
                if len(self.memory_cache) < self.max_memory_items:
                    self.memory_cache[cache_key] = {
                        'data': value,
                        'expires_at': expires_at,
                        'created_at': time.time()
                    }
                
                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO cache_entries 
                        (key, data, created_at, expires_at, compressed, last_accessed)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (cache_key, compressed_data, time.time(), expires_at, 
                         is_compressed, time.time()))
                    conn.commit()
                    
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
            
    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache"""
        cache_key = self._generate_key(key)
        
        with self.lock:
            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                
                # Check if expired
                if entry['expires_at'] > 0 and time.time() > entry['expires_at']:
                    del self.memory_cache[cache_key]
                else:
                    self.cache_stats['hits'] += 1
                    self.cache_stats['memory_hits'] += 1
                    return entry['data']
            
            # Check database cache
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT data, expires_at, compressed 
                        FROM cache_entries 
                        WHERE key = ?
                    ''', (cache_key,))
                    
                    result = cursor.fetchone()
                    
                    if result:
                        data_blob, expires_at, is_compressed = result
                        
                        # Check if expired
                        if expires_at > 0 and time.time() > expires_at:
                            # Clean up expired entry
                            conn.execute('DELETE FROM cache_entries WHERE key = ?', (cache_key,))
                            conn.commit()
                            self.cache_stats['misses'] += 1
                            return None
                        
                        # Update access statistics
                        conn.execute('''
                            UPDATE cache_entries 
                            SET access_count = access_count + 1, last_accessed = ?
                            WHERE key = ?
                        ''', (time.time(), cache_key))
                        conn.commit()
                        
                        # Decompress and deserialize
                        decompressed_data = self._decompress_data(data_blob, is_compressed)
                        value = pickle.loads(decompressed_data)
                        
                        # Add to memory cache for faster future access
                        if len(self.memory_cache) < self.max_memory_items:
                            self.memory_cache[cache_key] = {
                                'data': value,
                                'expires_at': expires_at,
                                'created_at': time.time()
                            }
                        
                        self.cache_stats['hits'] += 1
                        self.cache_stats['disk_hits'] += 1
                        return value
                        
            except Exception as e:
                logger.error(f"Cache get error for key {key}: {e}")
                
        self.cache_stats['misses'] += 1
        return None
        
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        cache_key = self._generate_key(key)
        
        with self.lock:
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            # Remove from database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('DELETE FROM cache_entries WHERE key = ?', (cache_key,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Cache delete error for key {key}: {e}")
                return False
                
    def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries, optionally matching a pattern"""
        with self.lock:
            if pattern is None:
                # Clear all
                self.memory_cache.clear()
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute('DELETE FROM cache_entries')
                        count = cursor.rowcount
                        conn.commit()
                        return count
                except Exception as e:
                    logger.error(f"Cache clear error: {e}")
                    return 0
            else:
                # Clear matching pattern (simple contains match)
                count = 0
                keys_to_delete = []
                
                # Memory cache
                for key in list(self.memory_cache.keys()):
                    if pattern in key:
                        keys_to_delete.append(key)
                        
                for key in keys_to_delete:
                    if key in self.memory_cache:
                        del self.memory_cache[key]
                        count += 1
                
                # Database cache
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute('DELETE FROM cache_entries WHERE key LIKE ?', (f'%{pattern}%',))
                        count += cursor.rowcount
                        conn.commit()
                except Exception as e:
                    logger.error(f"Cache clear pattern error: {e}")
                    
                return count
                
    def _cleanup_expired_entries(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        
        with self.lock:
            # Clean memory cache
            expired_keys = []
            for key, entry in self.memory_cache.items():
                if entry['expires_at'] > 0 and current_time > entry['expires_at']:
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self.memory_cache[key]
                self.cache_stats['evictions'] += 1
            
            # Clean database cache
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        'DELETE FROM cache_entries WHERE expires_at > 0 AND expires_at < ?', 
                        (current_time,)
                    )
                    if cursor.rowcount > 0:
                        logger.info(f"Cleaned up {cursor.rowcount} expired cache entries")
                        self.cache_stats['evictions'] += cursor.rowcount
                    conn.commit()
            except Exception as e:
                logger.error(f"Database cleanup error: {e}")
                
    def _optimize_memory_cache(self):
        """Optimize memory cache by removing least recently accessed items"""
        with self.lock:
            if len(self.memory_cache) <= self.max_memory_items:
                return
                
            # Sort by last access time and remove oldest
            items = list(self.memory_cache.items())
            items.sort(key=lambda x: x[1].get('created_at', 0))
            
            # Remove oldest 20% of items
            remove_count = len(items) // 5
            for i in range(remove_count):
                key, _ = items[i]
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    self.cache_stats['evictions'] += 1
                    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('SELECT COUNT(*) FROM cache_entries')
                    db_count = cursor.fetchone()[0]
                    
                    cursor = conn.execute('SELECT COUNT(*) FROM cache_entries WHERE expires_at > 0 AND expires_at < ?', (time.time(),))
                    expired_count = cursor.fetchone()[0]
                    
            except Exception:
                db_count = 0
                expired_count = 0
                
            hit_rate = self.cache_stats['hits'] / max(self.cache_stats['hits'] + self.cache_stats['misses'], 1) * 100
            
            return {
                'memory_cache_size': len(self.memory_cache),
                'database_cache_size': db_count,
                'expired_entries': expired_count,
                'hit_rate': round(hit_rate, 2),
                'total_hits': self.cache_stats['hits'],
                'memory_hits': self.cache_stats['memory_hits'],
                'disk_hits': self.cache_stats['disk_hits'],
                'total_misses': self.cache_stats['misses'],
                'evictions': self.cache_stats['evictions']
            }


# Cache decorator for function memoization
def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
                
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
            
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = AdvancedCacheManager()

# Convenience functions
def get_cache_stats() -> Dict[str, Any]:
    """Get current cache statistics"""
    return cache_manager.get_stats()

def clear_cache(pattern: Optional[str] = None) -> int:
    """Clear cache entries"""
    return cache_manager.clear(pattern)

def warm_cache():
    """Pre-populate cache with frequently accessed data"""
    logger.info("Starting cache warming...")
    
    # This would be called during application startup
    # to pre-populate frequently accessed data
    
    try:
        # Example: Pre-load current race data
        # This would be implemented based on your specific needs
        pass
        
    except Exception as e:
        logger.error(f"Cache warming error: {e}")