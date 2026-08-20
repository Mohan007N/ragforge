"""Monitoring and metrics collection"""
import time
import psutil
import logging
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self):
        self.request_count = defaultdict(int)
        self.request_latency = defaultdict(list)
        self.error_count = defaultdict(int)
        self.start_time = time.time()
    
    def record_request(self, endpoint: str, latency: float, status_code: int):
        """Record a request"""
        self.request_count[endpoint] += 1
        self.request_latency[endpoint].append(latency)
        
        if status_code >= 400:
            self.error_count[endpoint] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        
        # Calculate average latencies
        avg_latencies = {}
        for endpoint, latencies in self.request_latency.items():
            if latencies:
                avg_latencies[endpoint] = sum(latencies) / len(latencies)
        
        return {
            "uptime_seconds": uptime,
            "total_requests": sum(self.request_count.values()),
            "requests_by_endpoint": dict(self.request_count),
            "average_latency_ms": avg_latencies,
            "total_errors": sum(self.error_count.values()),
            "errors_by_endpoint": dict(self.error_count),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reset(self):
        """Reset all metrics"""
        self.request_count.clear()
        self.request_latency.clear()
        self.error_count.clear()

# Global metrics collector
metrics = MetricsCollector()

def get_system_metrics() -> Dict[str, Any]:
    """Get system resource metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_percent": disk.percent
            }
        }
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        return {}

def get_storage_metrics() -> Dict[str, Any]:
    """Get storage-related metrics"""
    try:
        from app.config import DATA_DIR, CHROMA_DIR, BM25_DIR
        
        def get_dir_size(path: Path) -> float:
            """Get directory size in MB"""
            if not path.exists():
                return 0.0
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return total / (1024**2)
        
        return {
            "documents_size_mb": get_dir_size(DATA_DIR),
            "chromadb_size_mb": get_dir_size(CHROMA_DIR),
            "bm25_size_mb": get_dir_size(BM25_DIR)
        }
    except Exception as e:
        logger.error(f"Failed to collect storage metrics: {e}")
        return {}

class RequestTimer:
    """Context manager for timing requests"""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        latency = (time.time() - self.start_time) * 1000  # ms
        status_code = 500 if exc_type else 200
        metrics.record_request(self.endpoint, latency, status_code)
