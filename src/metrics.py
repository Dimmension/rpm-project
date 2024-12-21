from prometheus_client import Counter, Histogram

BUCKETS = [
    0.2,
    0.4,
    0.6,
    0.8,
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0,
    float('+inf'),
]

# histogram_quantile(0.99, sum(rate(latency_seconds_bucket[1m])) by (le, handler))
LATENCY = Histogram(
    "latency_seconds",
    "Number of seconds",
    labelnames=['handler'],
    buckets=BUCKETS,
)

# sum(increase(counter_handler_total{handler="method_funcio..."}[1m]))
TOTAL_REQ = Counter(
    'counter_handler',
    'Считает то-то',
    labelnames=['handler']
)

# sum(increase(counter_handler_total{handler="method_funcio..."}[1m]))
TOTAL_SEND_MESSAGES = Counter(
    'send_messages',
    'Считает то-то',
)
TOTAL_REQ_WITH_STATUS_CODE = Counter(
    'counter_handler1',
    'Считает то-то',
    labelnames=['handler', 'status_code']
)

TOTAL_REQ.labels('handler1').inc()
TOTAL_REQ_WITH_STATUS_CODE.labels('handler1', 500).inc()
TOTAL_REQ_WITH_STATUS_CODE.labels('handler1', 200).inc()