"""
Prometheus metrics
"""
from prometheus_client import Counter, Histogram

# Request metrics
REQUEST_COUNT = Counter(
    'quanttxt_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'quanttxt_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)




