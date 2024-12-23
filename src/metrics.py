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

LATENCY = Histogram(
    "latency_seconds",
    "Number of seconds",
    labelnames=['handler'],
    buckets=BUCKETS,
)

TOTAL_REQ = Counter(
    'counter_handler',
    'Считает то-то',
    labelnames=['handler']
)

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
